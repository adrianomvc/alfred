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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metrics.observability import canonical_artifact, file_hash, now_iso, safe_path  # noqa: E402
from shared.common import iter_jsonl  # noqa: E402
from shared.observability.application.use_cases.process_claude_hook import (  # noqa: E402
    ClaudeHookContext,
    EngineInvocation,
    EngineRunResult,
    ProcessClaudeHook,
    ProcessClaudeHookCommand,
)
from shared.observability.infrastructure.adapters.claude.hook import ClaudeHookAdapter  # noqa: E402
from shared.observability.infrastructure.adapters.claude.transcript_cursor import TranscriptCursor  # noqa: E402

ENGINE = Path(__file__).resolve().parent / "attribute-usage-transcript.py"
COST_ENGINE = Path(__file__).resolve().parent / "apply-usage-rate-card.py"
FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]


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


def hook_adapter():
    return ClaudeHookAdapter(artifact_builder=canonical_artifact, path_sanitizer=safe_path, now=now_iso)


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


def resolve_rate_card_path(active):
    """Locate the approved usage rate card so the engine can price each request
    as it is logged. Precedence: env var, active-demand pointer, then the
    conventional config path. Returns None when none exists (cost stays null)."""
    configured = os.environ.get("ALFRED_RATE_CARD_PATH", "") or active.get("rate_card_path", "")
    if configured:
        candidate = Path(configured).expanduser()
        return str(candidate) if candidate.exists() else None
    default = Path.home() / ".alfred" / "config" / "usage-rate-card.json"
    return str(default) if default.exists() else None


def event_exists(path, event_id):
    if not path or not path.exists():
        return False
    try:
        for _line_number, event, _raw in iter_jsonl(path):
            if event is not None and event.get("event_id") == event_id:
                return True
    except OSError:
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


def run_alfred_engine(invocation: EngineInvocation) -> EngineRunResult:
    command = [
        sys.executable,
        str(ENGINE),
        *invocation.args,
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return EngineRunResult(result.returncode, result.stdout, result.stderr)


def price_new_usage(active):
    """Emit ``usage_cost_attributed`` events for newly attributed usage, so the
    toolbar's demand cost reflects real spend. Runs after attribution, prices via
    the approved rate card, and is idempotent (already-priced events are skipped
    by apply-usage-rate-card). Non-blocking: any failure — no rate card, no new
    usage to price, unknown model — is a benign no-op that never blocks the host.
    """
    rate_card_path = resolve_rate_card_path(active)
    obs_log = resolve_obs_log(active)
    if not rate_card_path or not obs_log or not obs_log.exists():
        return None
    command = [
        sys.executable,
        str(COST_ENGINE),
        "--input-path", str(obs_log),
        "--rate-card-path", rate_card_path,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except (OSError, subprocess.SubprocessError) as error:
        return f"alfred-usage-hook cost: {error}"
    # "No interaction cost events generated" is the idempotent no-op case.
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        if "No interaction cost events" in detail:
            return None
        return f"alfred-usage-hook cost: {detail}"
    return None


def build_context(transcript_path, active, raw_log, mode):
    state_path = os.environ.get("ALFRED_STATE_PATH", "") or active.get("state_path", "")
    obs_log = os.environ.get("ALFRED_OBS_LOG", "") or active.get("observability_log", "")
    run_id = os.environ.get("ALFRED_RUN_ID") or active.get("alfred_run_id") or ""
    return ClaudeHookContext(
        transcript_path=str(transcript_path),
        mode=mode,
        raw_log=raw_log,
        raw_cursor_path=str(cursor_path(transcript_path, "raw")),
        alfred_cursor_path=str(cursor_path(transcript_path, "alfred")),
        state_path=state_path,
        obs_log=obs_log,
        run_id=run_id,
        provider=os.environ.get("AI_OBS_PROVIDER", "claude-code"),
        project=os.environ.get("AI_OBS_PROJECT"),
        team=os.environ.get("AI_OBS_TEAM"),
        environment=os.environ.get("AI_OBS_ENVIRONMENT"),
    )


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
    cursor = TranscriptCursor()
    result = ProcessClaudeHook(
        raw_adapter=hook_adapter(),
        append_events=append_jsonl,
        write_cursor=cursor.write,
        write_policy_snapshot=write_policy_snapshot,
        run_engine=run_alfred_engine,
    ).execute(
        ProcessClaudeHookCommand(
            payload=payload,
            active=active,
            context=build_context(transcript_path, active, raw_log, mode),
        )
    )
    for message in result.messages:
        print(message, file=sys.stderr)

    cost_message = price_new_usage(active)
    if cost_message:
        print(cost_message, file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
