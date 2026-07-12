#!/usr/bin/env python3
"""Import ccusage session JSON into Alfred state for toolbar display.

ccusage reports a host session total. That value is useful for the toolbar and
for session-level cost visibility, but it is not an interaction-level
observability event. Per-interaction JSONL attribution must come from a source
with interaction/request granularity, such as a host transcript.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_state_fields, value_or  # noqa: E402
from metrics.observability import canonical_artifact  # noqa: E402


HOST_AGENT = {
    "claude-code": "claude",
    "codex": "codex",
    "github-copilot": "copilot",
    "copilot": "copilot",
}


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def update_state(path, updates):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    pending = {key.lower(): (key, value) for key, value in updates.items()}
    output = []
    in_host_adapters = False
    inserted = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_host_adapters and not inserted:
                for _, (key, value) in pending.items():
                    output.append(f"- {key}: {value}")
                inserted = True
            in_host_adapters = stripped.lower() == "## host adapters"

        if stripped.startswith("- ") and ":" in stripped:
            key = stripped[2:].split(":", 1)[0].strip().lower()
            if key in pending:
                original_key, value = pending.pop(key)
                output.append(f"- {original_key}: {value}")
                continue

        output.append(line)

    if pending:
        if not inserted:
            if not in_host_adapters:
                output.extend(["", "## Host Adapters"])
            for _, (key, value) in pending.items():
                output.append(f"- {key}: {value}")

    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def load_ccusage(args):
    if args.input_path:
        return json.loads(Path(args.input_path).read_text(encoding="utf-8-sig"))

    command = ["ccusage", "session", "--json"]
    if args.since:
        command.extend(["--since", args.since])
    if args.until:
        command.extend(["--until", args.until])
    if args.session_id:
        command.extend(["--id", args.session_id])

    # Resolve the executable via PATHEXT so Windows npm shims (ccusage.cmd)
    # are found. subprocess/CreateProcess only appends .exe, so a bare
    # "ccusage" name raises WinError 2 even when the shim is on PATH.
    resolved = shutil.which(command[0])
    if resolved is None:
        raise SystemExit(
            "ccusage not found on PATH. Install it (see connectors/usage-cost.md) "
            "or dump `ccusage session --json` to a file and pass it with -InputPath."
        )
    command[0] = resolved

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as error:
        raise SystemExit(
            f"Could not run ccusage ({error}). Dump `ccusage session --json` to a "
            "file and pass it with -InputPath."
        )
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit("ccusage session import failed")
    return json.loads(result.stdout)


def session_rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ["session", "sessions", "rows", "data"]:
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def last_activity(row):
    metadata = row.get("metadata") or {}
    return value_or(metadata.get("lastActivity"), "")


def select_row(rows, agent, session_id):
    candidates = []
    for row in rows:
        if agent and row.get("agent") != agent:
            continue
        if session_id and row.get("period") != session_id:
            continue
        candidates.append(row)

    if not candidates:
        raise SystemExit("No ccusage session matched the requested filters.")

    if session_id:
        return candidates[0], "session_id"

    candidates.sort(key=last_activity, reverse=True)
    return candidates[0], "latest_agent_session"


def models(row):
    used = row.get("modelsUsed")
    if isinstance(used, list) and used:
        return ",".join(str(item) for item in used)
    breakdowns = row.get("modelBreakdowns")
    if isinstance(breakdowns, list):
        names = [item.get("modelName") for item in breakdowns if item.get("modelName")]
        if names:
            return ",".join(names)
    return None


def make_snapshot(row, args, state_fields, selection_method):
    total_cost = row.get("totalCost")
    event_id = f"usage-ccusage-{row.get('period', 'session')}"
    ts = value_or(last_activity(row), now_iso())
    model = models(row)
    source_path = args.input_path if args.input_path else "ccusage session --json"
    metadata = row.get("metadata") or {}

    return {
        "schema_version": "alfred.usage-session.v1",
        "alfred": {
            "version": value_or(state_fields.get("framework version"), "unknown"),
            "framework_ref": value_or(state_fields.get("framework ref"), "local"),
            "framework_commit": value_or(state_fields.get("framework commit"), None),
            "schema_version": "alfred.usage-session.v1",
        },
        "ts": ts,
        "snapshot_id": event_id,
        "trace_id": value_or(state_fields.get("alfred run id"), value_or(args.run_id, "unknown")),
        "session_id": value_or(row.get("period"), "unknown"),
        "interaction_id": "unknown",
        "sequence": 1,
        "initiative_id": value_or(state_fields.get("initiative id"), "unknown"),
        "demand_id": value_or(state_fields.get("id"), "unknown"),
        "record_type": "session_usage_snapshot",
        "phase": value_or(args.phase, value_or(state_fields.get("current phase"), "operation")),
        "lane": value_or(state_fields.get("lane"), value_or(state_fields.get("modo"), "unknown")),
        "actor_type": "system",
        "actor_id": "usage-cost-ccusage",
        "action": "capture_session_usage",
        "status": "recorded",
        "step": {
            "id": "usage-cost",
            "name": "Usage and cost attribution",
            "sequence": 1,
            "goal": "Import ccusage session usage into Alfred state for toolbar display",
        },
        "artifacts_used": [
            canonical_artifact(source_path, "read", selection_reason="source_usage_export", observed_by="usage-cost-ccusage", ts=ts)
        ],
        "duration_ms": None,
        "tokens_input": row.get("inputTokens"),
        "tokens_output": row.get("outputTokens"),
        "cost_usd": total_cost,
        "retry_count": None,
        "input": {
            "source": "ccusage",
            "source_kind": "ccusage",
            "selection_method": selection_method,
            "agent": row.get("agent"),
            "last_activity": metadata.get("lastActivity"),
        },
        "derivation": {
            "rules_applied": ["connectors/usage-cost.md", "metrics/metrics.md"],
            "method": "ccusage session JSON import; session total only, not an interaction observability event",
        },
        "output": {
            "model": model,
            "tokens_input": row.get("inputTokens"),
            "tokens_output": row.get("outputTokens"),
            "tokens_cache_creation": row.get("cacheCreationTokens"),
            "tokens_cache_read": row.get("cacheReadTokens"),
            "total_tokens": row.get("totalTokens"),
            "cost_usd": total_cost,
            "cost_confidence": "estimated",
        },
        "model": model,
        "tool": "scripts/python/metrics/import-ccusage.py",
        "parent_event_id": None,
        "artifacts": [],
        "files_changed": [],
        "validation": {
            "source_record_parse": "ok",
            "selection_method": selection_method,
        },
        "risk": None,
        "blocker": None,
        "error": None,
        "state_transition": None,
        "actions": [{"type": "import_ccusage_session_total", "status": "completed"}],
        "questions_open": [],
        "assumptions": [],
        "metric_impact": {"session_cost_state": "captured"},
        "next": [],
        "metadata": {
            "connector_type": "usage-cost",
            "source_kind": "ccusage",
            "agent": row.get("agent"),
            "granularity": "session",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", "-StatePath", dest="state_path", default="")
    parser.add_argument("--input-path", "-InputPath", dest="input_path", default="")
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    parser.add_argument("--append", "-Append", dest="append", action="store_true", default=False,
                        help="deprecated: ccusage session totals must not be appended to observability JSONL")
    parser.add_argument("--no-append", "-NoAppend", dest="no_append", action="store_true",
                        help="deprecated no-op; state-only is the default")
    parser.add_argument("--write-snapshot", "-WriteSnapshot", dest="write_snapshot", action="store_true",
                        help="write the session snapshot JSON to -OutputPath for debugging; never append to observability JSONL")
    parser.add_argument("--emit-json", "-EmitJson", dest="emit_json", action="store_true",
                        help="print the session snapshot JSON to stdout")
    parser.add_argument("--host", "-Host", dest="host", default="claude-code")
    parser.add_argument("--agent", "-Agent", dest="agent", default="")
    parser.add_argument("--session-id", "-SessionId", dest="session_id", default="")
    parser.add_argument("--since", "-Since", dest="since", default="")
    parser.add_argument("--until", "-Until", dest="until", default="")
    parser.add_argument("--run-id", "-RunId", dest="run_id", default=os.environ.get("ALFRED_RUN_ID", ""))
    parser.add_argument("--phase", "-Phase", dest="phase", default="")
    parser.add_argument("--no-state-update", "-NoStateUpdate", dest="state_update", action="store_false", default=True)
    args = parser.parse_args()
    if args.append:
        raise SystemExit(
            "-Append is no longer supported for ccusage session totals. "
            "Use the state fields for toolbar cost; append JSONL only from interaction/request-granular sources."
        )

    state_path = Path(args.state_path).resolve() if args.state_path else None
    state_fields = read_state_fields(state_path) if state_path else {}
    if not args.agent:
        args.agent = HOST_AGENT.get(args.host, args.host)
    if not args.session_id:
        args.session_id = value_or(state_fields.get("usage session id"), "")

    payload = load_ccusage(args)
    row, selection_method = select_row(session_rows(payload), args.agent, args.session_id)
    snapshot = make_snapshot(row, args, state_fields, selection_method)
    snapshot_line = json.dumps(snapshot, separators=(",", ":"))

    if args.output_path and args.write_snapshot:
        output_path = Path(args.output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(snapshot_line + "\n", encoding="utf-8")
        print(f"Wrote ccusage session snapshot to {output_path}")
    elif args.output_path:
        raise SystemExit("-OutputPath requires -WriteSnapshot; ccusage session totals are not observability JSONL events.")
    if args.emit_json:
        print(snapshot_line)

    if state_path and args.state_update:
        updates = {
            "usage-cost": "ccusage automatic",
            "cost source": "ccusage",
            "cost usd": str(row.get("totalCost")),
            "cost confidence": "estimated",
            "cost granularity": "session",
            "host": args.host,
            "usage session id": str(row.get("period")),
            "usage imported at": now_iso(),
        }
        if args.run_id:
            updates["alfred run id"] = args.run_id
        update_state(state_path, updates)
        print(f"Updated usage-cost fields in {state_path}")


if __name__ == "__main__":
    main()
