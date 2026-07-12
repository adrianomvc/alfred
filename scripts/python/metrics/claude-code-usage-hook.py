#!/usr/bin/env python3
"""Claude Code hook: collect sanitized raw telemetry and Alfred usage events.

Claude Code hooks do not pass token usage directly; they pass
``transcript_path``. The transcript contains request ids, prompt ids, tool
metadata, and exact token usage. This hook is intentionally non-blocking: every
path exits 0 and failures are reported to stderr only.

Toolbar display remains owned by workflow/render-toolbar.py; after this hook
updates Alfred state/logs, callers still render with
``render-toolbar.py -RegisterActive``.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from metrics.observability import canonical_artifact, file_hash, now_iso, safe_path  # noqa: E402

ENGINE = Path(__file__).resolve().parent / "attribute-usage-transcript.py"
FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]


def active_demand():
    runtime_dir = os.environ.get("ALFRED_RUNTIME_DIR")
    base = Path(runtime_dir).expanduser() if runtime_dir else Path.home() / ".alfred" / "runtime"
    active_path = base / "active-demand.json"
    if not active_path.exists():
        return {}
    try:
        return json.loads(active_path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return {}


def cursor_dir():
    configured = os.environ.get("AI_OBS_CURSOR_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".alfred" / "runtime" / "cursors"


def cursor_path(transcript_path, suffix):
    digest = hashlib.sha256(str(Path(transcript_path).resolve()).encode("utf-8")).hexdigest()
    return cursor_dir() / f"{digest}.{suffix}.json"


def read_cursor(path, transcript_path):
    if not path.exists():
        return 0
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if payload.get("transcript_path") != str(Path(transcript_path).resolve()):
            return 0
        offset = int(payload.get("last_byte_offset") or 0)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0
    size = Path(transcript_path).stat().st_size
    return 0 if offset < 0 or offset > size else offset


def write_cursor(path, transcript_path, offset, last_request_id=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "transcript_path": str(Path(transcript_path).resolve()),
        "last_byte_offset": offset,
        "last_request_id": last_request_id,
        "updated_at": now_iso(),
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_new_lines(transcript_path, cursor):
    offset = read_cursor(cursor, transcript_path)
    with Path(transcript_path).open("rb") as handle:
        handle.seek(offset)
        data = handle.read()
        end_offset = handle.tell()
    return data.decode("utf-8-sig", errors="replace").splitlines(), end_offset


def extract_tool_paths(tool_name, tool_input):
    if not isinstance(tool_input, dict):
        return []
    candidates = []
    for key in ("file_path", "path", "notebook_path"):
        if tool_input.get(key):
            candidates.append(tool_input[key])
    if tool_name in ("Bash", "Shell") and tool_input.get("command"):
        candidates.append("command_output")
    return candidates


def operation_for_tool(tool_name):
    if tool_name in ("Read", "Glob", "Grep", "LS"):
        return "read"
    if tool_name in ("Write",):
        return "create"
    if tool_name in ("Edit", "MultiEdit"):
        return "update"
    if tool_name in ("Bash", "Shell"):
        return "execute"
    return "use"


def raw_events_from_transcript(transcript_path, lines, provider):
    events = []
    last_request_id = None
    current_prompt_id = None
    for raw in lines:
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            continue
        ts = record.get("timestamp") or now_iso()
        record_type = record.get("type")
        session_id = record.get("sessionId") or record.get("session_id")
        if record_type == "user":
            current_prompt_id = record.get("promptId") or current_prompt_id
            events.append(
                {
                    "schema_version": "ai.agent.raw.v1",
                    "ts": ts,
                    "provider": provider,
                    "raw_event_type": "user_prompt",
                    "session_id": session_id,
                    "interaction_id": record.get("promptId"),
                    "message_uuid": record.get("uuid"),
                    "cwd": safe_path(record.get("cwd")),
                    "git_branch": record.get("gitBranch"),
                    "content_recorded": False,
                }
            )
        elif record_type == "assistant":
            message = record.get("message") or {}
            request_id = record.get("requestId") or record.get("uuid")
            last_request_id = request_id or last_request_id
            usage = message.get("usage") or {}
            events.append(
                {
                    "schema_version": "ai.agent.raw.v1",
                    "ts": ts,
                    "provider": provider,
                    "raw_event_type": "model_request",
                    "session_id": session_id,
                    "interaction_id": current_prompt_id,
                    "request_id": request_id,
                    "model": message.get("model"),
                    "tokens_input": usage.get("input_tokens"),
                    "tokens_output": usage.get("output_tokens"),
                    "tokens_cache_creation": usage.get("cache_creation_input_tokens"),
                    "tokens_cache_read": usage.get("cache_read_input_tokens"),
                    "content_recorded": False,
                }
            )
            content = message.get("content")
            if isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict) or item.get("type") != "tool_use":
                        continue
                    tool_name = item.get("name")
                    tool_input = item.get("input") if isinstance(item.get("input"), dict) else {}
                    event = {
                        "schema_version": "ai.agent.raw.v1",
                        "ts": ts,
                        "provider": provider,
                        "raw_event_type": "tool_use",
                        "session_id": session_id,
                        "interaction_id": current_prompt_id,
                        "request_id": request_id,
                        "tool_use_id": item.get("id"),
                        "tool_name": tool_name,
                        "operation": operation_for_tool(tool_name),
                        "input_keys": sorted(tool_input.keys()),
                        "artifacts": [
                            canonical_artifact(
                                path,
                                operation_for_tool(tool_name),
                                selection_reason="claude_tool_input",
                                observed_by="claude_hook",
                                ts=ts,
                            )
                            for path in extract_tool_paths(tool_name, tool_input)
                        ],
                        "content_recorded": False,
                    }
                    events.append(event)
    return events, last_request_id


def append_jsonl(path, events):
    if not events:
        return
    target = Path(path).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, separators=(",", ":")) + "\n")


def resolve_obs_log(active):
    obs_log = os.environ.get("ALFRED_OBS_LOG", "") or active.get("observability_log", "")
    if obs_log:
        return Path(obs_log).expanduser()
    state_path = os.environ.get("ALFRED_STATE_PATH", "") or active.get("state_path", "")
    if not state_path:
        return None
    return Path(state_path).expanduser().parent / "05-operation" / "011-observability-log.jsonl"


def event_exists(path, event_id):
    if not path or not path.exists():
        return False
    try:
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            if not raw.strip():
                continue
            event = json.loads(raw)
            if event.get("event_id") == event_id:
                return True
    except (json.JSONDecodeError, OSError):
        return False
    return False


def framework_commit():
    try:
        result = subprocess.run(
            ["git", "-C", str(FRAMEWORK_ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 and result.stdout.strip() else None


def write_policy_snapshot(payload, active):
    target = resolve_obs_log(active)
    if not target:
        return
    session_id = payload.get("session_id") or payload.get("sessionId") or active.get("session_id")
    run_id = os.environ.get("ALFRED_RUN_ID") or active.get("alfred_run_id")
    basis = run_id or session_id or str(target.resolve())
    event_id = "policy-snapshot-" + hashlib.sha256(str(basis).encode("utf-8")).hexdigest()[:16]
    if event_exists(target, event_id):
        return
    version_path = FRAMEWORK_ROOT / "VERSION"
    framework_version = None
    if version_path.exists():
        try:
            framework_version = version_path.read_text(encoding="utf-8-sig").strip()
        except OSError:
            framework_version = None
    ts = now_iso()
    tracked = [
        "core/model-policy.md",
        "rules/common/token-budget-policy.md",
        "rules/common/prompt-caching-policy.md",
        "rules/common/context-compression-policy.md",
        "rules/common/tool-discovery-policy.md",
        "rules/common/terminal-token-policy.md",
        "core/hooks/usage-attribution.md",
    ]
    artifacts = []
    for rel in tracked:
        path = FRAMEWORK_ROOT / rel
        item = canonical_artifact(
            rel,
            operation="snapshot",
            selection_reason="session_policy_snapshot",
            observed_by="claude_hook",
            ts=ts,
        )
        item["content_hash"] = file_hash(path)
        try:
            item["size_bytes"] = path.stat().st_size
        except OSError:
            item["size_bytes"] = None
        artifacts.append(item)
    event = {
        "schema_version": "alfred.observability.v1",
        "event_id": event_id,
        "event_type": "policy_snapshot",
        "event_scope": "session",
        "ts": ts,
        "session_id": session_id,
        "interaction_id": None,
        "request_id": None,
        "alfred_run_id": run_id,
        "framework_version": framework_version,
        "framework_commit": framework_commit(),
        "observed_by": "claude_hook",
        "artifacts_used": artifacts,
    }
    append_jsonl(target, [event])


def resolve_mode(active, raw_log):
    configured = os.environ.get("AI_OBS_MODE", "").lower().strip()
    if configured in ("raw", "alfred", "both"):
        return configured
    has_alfred = bool(os.environ.get("ALFRED_STATE_PATH") or os.environ.get("ALFRED_OBS_LOG") or active.get("state_path") or active.get("observability_log"))
    if raw_log and has_alfred:
        return "both"
    if raw_log:
        return "raw"
    return "alfred"


def run_alfred_engine(transcript_path, payload, active):
    state_path = os.environ.get("ALFRED_STATE_PATH", "") or active.get("state_path", "")
    obs_log = os.environ.get("ALFRED_OBS_LOG", "") or active.get("observability_log", "")
    if not state_path and not obs_log:
        print(
            "alfred-usage-hook: set ALFRED_STATE_PATH/ALFRED_OBS_LOG or render toolbar with -RegisterActive; skipping Alfred log",
            file=sys.stderr,
        )
        return

    command = [
        sys.executable,
        str(ENGINE),
        "--transcript-path",
        str(transcript_path),
        "--granularity",
        "request",
        "--emit-interactions",
        "--cursor-path",
        str(cursor_path(transcript_path, "alfred")),
    ]
    if state_path:
        command += ["--state-path", state_path]
    if obs_log:
        command += ["--output-path", obs_log]
    if payload.get("session_id") or payload.get("sessionId"):
        command += ["--session-id", str(payload.get("session_id") or payload.get("sessionId"))]
    run_id = os.environ.get("ALFRED_RUN_ID") or active.get("alfred_run_id")
    if run_id:
        command += ["--run-id", run_id]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"alfred-usage-hook: {result.stderr.strip() or result.stdout.strip()}", file=sys.stderr)


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        return

    transcript_path = payload.get("transcript_path")
    if not transcript_path or not Path(transcript_path).exists():
        print("alfred-usage-hook: no transcript_path; skipping", file=sys.stderr)
        return

    active = active_demand()
    raw_log = os.environ.get("AI_OBS_RAW_LOG", "")
    mode = resolve_mode(active, raw_log)

    if mode in ("raw", "both") and raw_log:
        try:
            raw_cursor = cursor_path(transcript_path, "raw")
            lines, end_offset = read_new_lines(transcript_path, raw_cursor)
            events, last_request_id = raw_events_from_transcript(
                transcript_path,
                lines,
                os.environ.get("AI_OBS_PROVIDER", "claude-code"),
            )
            for event in events:
                event["project"] = os.environ.get("AI_OBS_PROJECT")
                event["team"] = os.environ.get("AI_OBS_TEAM")
                event["environment"] = os.environ.get("AI_OBS_ENVIRONMENT")
            append_jsonl(raw_log, events)
            write_cursor(raw_cursor, transcript_path, end_offset, last_request_id)
        except Exception as error:  # noqa: BLE001 - hook must never block host
            print(f"alfred-usage-hook raw: {error}", file=sys.stderr)

    if mode in ("alfred", "both"):
        try:
            write_policy_snapshot(payload, active)
            run_alfred_engine(transcript_path, payload, active)
        except Exception as error:  # noqa: BLE001 - hook must never block host
            print(f"alfred-usage-hook alfred: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
