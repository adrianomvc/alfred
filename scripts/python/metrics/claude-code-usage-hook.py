#!/usr/bin/env python3
"""Claude Code Stop hook: stamp exact transcript usage out-of-band (Layer 3).

Claude Code hooks do NOT receive token usage inline, but Stop/SubagentStop pass
``transcript_path`` — and the transcript owns exact per-request usage. This hook
runs the transcript attribution engine (turn granularity, idempotent) so usage
is stamped by the layer that owns the object, not guessed by the in-band agent.

Wire it in Claude Code ``settings.json`` under ``hooks.Stop``. It reads the hook
JSON from stdin and targets the demand log via env:
- ``ALFRED_STATE_PATH``  — demand ``001-state.md`` (log derived next to it), or
- ``ALFRED_OBS_LOG``     — explicit observability JSONL path.
Optional: ``ALFRED_ALLOCATE_COST=1`` allocates the session cost across turns.

Safety: this hook must never block the session. It exits 0 on every path; a
missing target or any error is reported to stderr and ignored. The transcript is
written asynchronously and may lag the final turn, so the last turn is picked up
on the next Stop; the ccusage session import remains the session-total backstop.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent / "attribute-usage-transcript.py"


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

    state_path = os.environ.get("ALFRED_STATE_PATH", "")
    obs_log = os.environ.get("ALFRED_OBS_LOG", "")
    if not state_path and not obs_log:
        print("alfred-usage-hook: set ALFRED_STATE_PATH or ALFRED_OBS_LOG; skipping", file=sys.stderr)
        return

    command = [
        sys.executable,
        str(ENGINE),
        "--transcript-path",
        str(transcript_path),
        "--granularity",
        "turn",
    ]
    if state_path:
        command += ["--state-path", state_path]
    if obs_log:
        command += ["--output-path", obs_log]
    if payload.get("session_id"):
        command += ["--session-id", str(payload["session_id"])]
    if os.environ.get("ALFRED_RUN_ID"):
        command += ["--run-id", os.environ["ALFRED_RUN_ID"]]
    if os.environ.get("ALFRED_ALLOCATE_COST"):
        command += ["--allocate-cost"]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0 and result.stderr:
            print(f"alfred-usage-hook: {result.stderr.strip()}", file=sys.stderr)
    except OSError as error:
        print(f"alfred-usage-hook: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
    sys.exit(0)
