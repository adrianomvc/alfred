#!/usr/bin/env python3
"""Check reverse-engineering staleness against the current app commit.

Python mirror of ``scripts/powershell/validate-reverse-eng-staleness.ps1``.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_lines  # noqa: E402

UNAVAILABLE = ("not-git", "unknown", "a confirmar")


def get_recorded_commit(lines):
    patterns = [
        r"^\s*-\s+commit\s*:\s*(not-git|unknown|a confirmar)\s*$",
        r"^\s*-\s+app commit\s*:\s*(not-git|unknown|a confirmar)\s*$",
        r"^\s*-\s+commit\s*:\s*`?([A-Fa-f0-9]{7,40})`?\s*$",
        r"^\s*-\s+app commit\s*:\s*`?([A-Fa-f0-9]{7,40})`?\s*$",
    ]
    for line in lines:
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                return match.group(1)
    for line in lines:
        match = re.search(r"\b([A-Fa-f0-9]{40})\b", line)
        if match:
            return match.group(1)
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reverse-eng-path", "-ReverseEngPath", dest="reverse_eng_path", required=True)
    parser.add_argument("--app-repo-path", "-AppRepoPath", dest="app_repo_path", default="")
    parser.add_argument("--current-commit", "-CurrentCommit", dest="current_commit", default="")
    parser.add_argument("--strict", "-Strict", dest="strict", action="store_true")
    args = parser.parse_args()

    reverse_eng = Path(args.reverse_eng_path)
    if not reverse_eng.exists():
        raise SystemExit(f"Reverse-eng artifact not found: {reverse_eng}")

    recorded = get_recorded_commit(read_lines(reverse_eng))

    if recorded == "":
        message = "Reverse-eng artifact does not record an app commit."
        if args.strict:
            raise SystemExit(message)
        print(f"WARN missing_commit: {message}")
        return

    if recorded in UNAVAILABLE:
        print(f"OK reverse-eng staleness explicitly unavailable: recorded={recorded}")
        return

    current = args.current_commit
    if current == "":
        if args.app_repo_path == "":
            print(f"OK recorded commit {recorded}")
            print("WARN current_commit_unknown: provide -AppRepoPath or -CurrentCommit to check staleness")
            return
        if not (Path(args.app_repo_path) / ".git").exists():
            message = f"AppRepoPath is not a git repository: {args.app_repo_path}"
            if args.strict:
                raise SystemExit(message)
            print(f"OK recorded commit {recorded}")
            print(f"WARN app_repo_not_git: {message}")
            return
        current = subprocess.run(
            ["git", "-C", args.app_repo_path, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()

    if current == "":
        raise SystemExit("Could not determine current app commit.")

    recorded_prefix = recorded.lower()
    current_prefix = current.lower()
    if current_prefix.startswith(recorded_prefix) or recorded_prefix.startswith(current_prefix):
        print(f"OK reverse-eng fresh: recorded={recorded} current={current}")
        return

    message = f"Reverse-eng stale: recorded={recorded} current={current}"
    if args.strict:
        raise SystemExit(message)
    print(f"WARN reverse_eng_stale: {message}")


if __name__ == "__main__":
    main()
