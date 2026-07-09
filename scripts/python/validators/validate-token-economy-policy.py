#!/usr/bin/env python3
"""Validate token-budget and deferred-work policy wiring."""

import argparse
from pathlib import Path


def require_text(path, needle):
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        raise SystemExit(f"Missing text in {path}: {needle}")
    print(f"OK text {path} / {needle}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    require_text(root / "rules/common/token-budget-policy.md", "Plan the token spend before loading context")
    require_text(root / "rules/common/token-budget-policy.md", "Do not reduce context by dropping acceptance criteria")
    require_text(root / "rules/common/token-budget-policy.md", "If the host has token counting")
    require_text(root / "rules/common/deferred-work-policy.md", "not on the human's critical path")
    require_text(root / "rules/common/deferred-work-policy.md", "Deferred outputs are drafts or inputs")
    require_text(root / "rules/common/deferred-work-policy.md", "batch, flex, background")

    require_text(root / "core/boot.md", "token-budget-policy.md")
    require_text(root / "core/model-policy.md", "Deferred work")
    require_text(root / "rules/README.md", "token-budget-policy")
    require_text(root / "rules/README.md", "deferred-work-policy")
    require_text(root / "rules/lifecycle/execution/execution.md", "token-budget-policy.md")
    require_text(root / "rules/lifecycle/execution/sub-activities/workflow-planning.md", "context budget per unit")
    require_text(root / "rules/lifecycle/operations/operations.md", "deferred-work-policy.md")
    require_text(root / "rules/lifecycle/operations/sub-activities/metrics-collection.md", "deferred-work-policy.md")
    require_text(root / "docs/framework-validation.md", "validate-token-economy-policy")

    print("Token economy policy validation completed.")


if __name__ == "__main__":
    main()
