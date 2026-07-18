#!/usr/bin/env python3
"""Conservative policy checks for a Devin declarative blueprint."""

import argparse
import re
import sys
from pathlib import Path

REPO_COMMANDS = (
    re.compile(r"\bnpm\s+(?:ci|install)(?!\s+-g)"),
    re.compile(r"\b(?:pnpm|yarn)\s+install\b"),
    re.compile(r"\buv\s+sync\b"),
    re.compile(r"\bpip\s+install\s+-r\b"),
)
SECRET_LITERAL = re.compile(
    r"(?im)^\s*(?:[A-Z0-9_]*(?:TOKEN|PASSWORD|SECRET|API_KEY|PRIVATE_KEY)[A-Z0-9_]*)\s*[:=]\s*['\"]?(?!\$|<|\{\{)([^\s'\"]+)"
)


def validate(text, tier):
    errors = []
    if tier in {"enterprise", "organization"}:
        for pattern in REPO_COMMANDS:
            if pattern.search(text):
                errors.append(f"repo-specific dependency command is not allowed in {tier} tier: {pattern.pattern}")
    for match in SECRET_LITERAL.finditer(text):
        errors.append(f"possible literal secret in blueprint: {match.group(0).strip().split(':', 1)[0]}")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--tier", required=True, choices=["enterprise", "organization", "repository"])
    args = parser.parse_args()
    errors = validate(Path(args.path).read_text(encoding="utf-8-sig"), args.tier)
    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK Devin {args.tier} blueprint policy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
