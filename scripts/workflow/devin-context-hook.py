#!/usr/bin/env python3
"""Re-anchor the active Alfred demand on Devin SessionStart/PostCompaction."""

import json
import os
import sys
from pathlib import Path


def active_pointer():
    runtime = os.environ.get("ALFRED_RUNTIME_DIR")
    base = Path(runtime).expanduser() if runtime else Path.home() / ".alfred" / "runtime"
    return base / "active-demand.json"


def context_for_active_demand():
    pointer = active_pointer()
    try:
        payload = json.loads(pointer.read_text(encoding="utf-8-sig"))
        state = Path(payload["state_path"])
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return ""
    if not state.is_file():
        return ""
    memory = ""
    for parent in state.parents:
        candidate = parent / "005-memory.md"
        if candidate.is_file():
            memory = str(candidate)
            break
    parts = [
        f"Alfred active demand: {payload.get('demand_id') or state.parent.name}.",
        f"Re-read the authoritative state before acting: {state}.",
    ]
    if memory:
        parts.append(f"Scan the compact memory index first and load details JIT: {memory}.")
    parts.append("Conversation summaries and memory are pointers, not authority.")
    return " ".join(parts)


def main():
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        event = {}
    event_name = event.get("hook_event_name") or event.get("hookEventName") or "SessionStart"
    context = context_for_active_demand()
    if context:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context,
        }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
