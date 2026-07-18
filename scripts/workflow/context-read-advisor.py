#!/usr/bin/env python3
"""Advisory hook for expensive source reads; never denies the tool call."""

import json
import math
import sys
from pathlib import Path


def advice(path, threshold=1500):
    target = Path(path)
    if not target.is_file():
        return None
    estimated = math.ceil(target.stat().st_size / 4)
    if estimated <= threshold:
        return None
    memory = next((parent / "005-memory.md" for parent in target.parents
                   if (parent / "005-memory.md").is_file()), None)
    selector = f"search {memory} by trigger/tags, then " if memory else ""
    return (f"Estimated full read cost: ~{estimated} tokens. Consider {selector}an outline, "
            "symbol, or bounded range first. This is advisory: read the current source whenever correctness requires it.")


def main():
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    tool_input = event.get("tool_input") or event.get("toolInput") or {}
    path = tool_input.get("path") or tool_input.get("file_path") or ""
    message = advice(path) if path else None
    if message:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": event.get("hook_event_name") or event.get("hookEventName") or "PreToolUse",
            "additionalContext": message,
        }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
