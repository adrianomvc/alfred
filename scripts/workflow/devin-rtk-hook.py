#!/usr/bin/env python3
"""DEVIN CLI PreToolUse hook: rewrite shell commands through rtk.

The DEVIN CLI runs a `PreToolUse` hook and can transparently rewrite a tool's
input by printing `hookSpecificOutput.updatedInput` (docs.devin.ai/cli/
extensibility/hooks). RTK ships no Devin preset — its stock hook matches the
Claude `Bash` tool, not Devin's `exec` — so this bridges the two: read the event
on stdin, ask `rtk rewrite` for a compact equivalent of the command, and return
it as updatedInput. rtk is the single source of truth for the rewrite.

Fail-open by design (D3, optional layer): on any parse mismatch, a non-`exec`
tool, a missing rtk, or a command rtk cannot compact, print nothing and exit 0 so
the original command runs unchanged.
"""

import json
import shutil
import subprocess
import sys


def rewrite(event):
    tool_name = event.get("tool_name") or event.get("toolName") or ""
    # Devin's shell tool is `exec`; only rewrite shell commands. An empty/unknown
    # tool_name is treated as "maybe shell" and still checked for a command.
    if tool_name and tool_name != "exec":
        return None

    tool_input = event.get("tool_input") or event.get("toolInput") or {}
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command") or tool_input.get("cmd") or ""
    if not isinstance(command, str) or not command.strip():
        return None

    rtk = shutil.which("rtk")
    if not rtk:
        return None

    try:
        result = subprocess.run(
            [rtk, "rewrite", command],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    # Trust stdout, not the exit code: rtk 0.43.0 prints the rewritten command on
    # a *non-zero* code (3) when there is an equivalent, and prints nothing (exit
    # 1) when there is none. The documented "exit 0" is not what the binary does,
    # so gating on the exit code would drop every rewrite. Empty output = no-op.
    rewritten = (result.stdout or "").strip()
    if not rewritten or rewritten == command.strip():
        return None

    # Preserve any other input fields; only swap the command.
    updated = dict(tool_input)
    updated["command"] = rewritten
    return updated


def main():
    raw = sys.stdin.read()
    try:
        event = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return 0
    if not isinstance(event, dict):
        return 0

    updated = rewrite(event)
    if updated is not None:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "updatedInput": updated,
            }
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
