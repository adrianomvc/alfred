#!/usr/bin/env python3
"""Validate Alfred's safe context compression guardrails."""

import argparse
from pathlib import Path


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def require(path, expected):
    content = read(path)
    if expected not in content:
        raise SystemExit(f"Missing required text in {path}: {expected}")
    print(f"OK text {path} / {expected}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    policy = root / "rules/common/context-compression-policy.md"
    require(policy, "Compression may select and prioritize context")
    require(policy, "must open the original source files")
    require(policy, "Validation evidence must come from original sources")
    require(policy, "Compressed context can point to what")

    require(root / "core/boot.md", "context-compression-policy.md")
    require(root / "rules/README.md", "context-compression-policy")

    require(root / "rules/lifecycle/design/design.md", "must not replace a detailed `spec`")
    require(root / "rules/lifecycle/execution/execution.md", "Before editing, open the original source")
    require(root / "rules/lifecycle/execution/sub-activities/code-generation.md",
            "compressed context may point to them, but cannot replace them")
    require(root / "rules/lifecycle/validation/validation.md",
            "validation evidence must point to")
    require(root / "docs/framework-validation.md", "validate-context-compression-policy")

    print("Context compression policy validation completed.")


if __name__ == "__main__":
    main()
