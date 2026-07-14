#!/usr/bin/env python3
"""Check reverse-engineering staleness against the current app commit."""

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.validation.reverse_eng_staleness import validate_reverse_eng_staleness  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reverse-eng-path", "-ReverseEngPath", dest="reverse_eng_path", required=True)
    parser.add_argument("--app-repo-path", "-AppRepoPath", dest="app_repo_path", default="")
    parser.add_argument("--current-commit", "-CurrentCommit", dest="current_commit", default="")
    parser.add_argument("--strict", "-Strict", dest="strict", action="store_true")
    args = parser.parse_args()

    result = validate_reverse_eng_staleness(
        args.reverse_eng_path,
        app_repo_path=args.app_repo_path,
        current_commit=args.current_commit,
        strict=args.strict,
    )
    for line in result.output:
        print(line)
    if result.failure_message:
        raise SystemExit(result.failure_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
