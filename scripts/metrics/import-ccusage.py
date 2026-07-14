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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import read_state_fields, value_or  # noqa: E402
from metrics.observability import canonical_artifact  # noqa: E402
from shared.observability.application.use_cases.import_ccusage_session import (  # noqa: E402
    ImportCcusageSession,
    ImportCcusageSessionCommand,
)
from shared.observability.infrastructure.adapters.ccusage.session import (  # noqa: E402
    CcusageSessionAdapter,
    NoSessionMatch,
    last_activity,
    models,
)


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
    try:
        row, selection_method = CcusageSessionAdapter().select_session(payload, args.agent, args.session_id)
    except NoSessionMatch as error:
        # Non-fatal: never crash the toolbar path and never freeze cost silently.
        # Keep any prior cost but mark it stale so the toolbar tells the human to
        # reimport, instead of showing a frozen value as if it were current.
        if state_path and args.state_update and value_or(state_fields.get("cost usd"), ""):
            update_state(state_path, {"cost confidence": "stale", "usage imported at": now_iso()})
            print(f"{error} Kept prior cost but marked it stale in {state_path}", file=sys.stderr)
        else:
            print(str(error), file=sys.stderr)
        return
    if selection_method in ("fallback_prefix", "fallback_latest"):
        print(
            f"ccusage: state 'usage session id' ({args.session_id!r}) did not match a session exactly; "
            f"used {selection_method} and reconciled the id to period {row.get('period')!r}.",
            file=sys.stderr,
        )
    source_path = args.input_path if args.input_path else "ccusage session --json"
    result = ImportCcusageSession(artifact_builder=canonical_artifact, now=now_iso).execute(
        ImportCcusageSessionCommand(
            row=row,
            state_fields=state_fields,
            selection_method=selection_method,
            source_path=source_path,
            run_id=args.run_id,
            phase=args.phase,
            host=args.host,
            model=models(row),
            last_activity=last_activity(row),
        )
    )
    snapshot = result.snapshot
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
        update_state(state_path, result.state_updates)
        print(f"Updated usage-cost fields in {state_path}")


if __name__ == "__main__":
    main()
