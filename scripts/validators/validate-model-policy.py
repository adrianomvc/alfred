#!/usr/bin/env python3
"""Validate the Alfred model policy."""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_text  # noqa: E402
from shared.validation import Severity, ValidationIssue, ValidationReport  # noqa: E402

REQUIRED_HEADINGS = (
    "Selection rule",
    "Floor per lane",
    "Adjustment per step",
    "Effort per step",
    "Task budget",
    "Parallel units",
    "Tier",
    "real model",
    "Mechanism",
    "User override",
    "In the toolbar",
)

REQUIRED_FLOORS = {"FAST": "cheap", "Standard": "medium", "SAFE": "strong"}

REQUIRED_PATTERNS = (
    *((
        r"(?im)^\|\s*" + lane + r"\s*\|\s*" + tier + r"\s*\|",
        f"{lane} floor = {tier}",
    ) for lane, tier in REQUIRED_FLOORS.items()),
    *((r"(?im)^\|\s*" + tier + r"\s*\|", f"tier map includes {tier}") for tier in ("cheap", "medium", "strong")),
    (r"(?im)^\|\s*Inception\b.*FAST=strong.*Standard=medium", "Inception FAST=strong / Standard=medium"),
    (r"(?im)^\|\s*Operate\s*\|.*even in SAFE", "Operate may drop to medium in SAFE (floor exception)"),
    (r"(?im)^\|\s*Design.*spec-design.*\|\s*strong", "Design pinned to strong"),
    (r"(?im)^\|\s*Inception\s*\|\s*high\s*\|\s*high\s*\|\s*xhigh", "Inception effort high/high/xhigh"),
    (r"(?im)^\|\s*Execution\s*\|\s*medium\s*\|\s*high\s*\|\s*xhigh", "Execution effort medium/high/xhigh"),
    (r"(?im)^\|\s*Operate\s*\|\s*low\s*\|\s*low\s*\|\s*medium", "Operate effort low/low/medium"),
    (r"(?im)task budget.*min 20,000 tokens|min 20,000 tokens", "Execution task budget min 20k"),
    (r"(?im)Execution.*minimum medium.*never runs on `cheap`", "Execution never runs on cheap (min medium)"),
    (r"(?im)Validate.*reviewer.*minimum medium.*\+1 if risk", "Validate reviewer min medium, +1 if risk"),
    (r"(?im)Decisions / architecture \(SAFE\).*\|\s*strongest\s*\|", "SAFE architecture decisions use strongest"),
    (r"(?im)below the risk floor.*warns? the trade-off", "override below floor warns human"),
    (r"(?im)record[s]? it in `state`/`audit`", "override is recorded"),
    (r"(?im)toolbar shows the \*\*current model\*\*", "toolbar declares current model"),
)


def validate_model_policy(root) -> ValidationReport:
    root = Path(root).resolve()
    policy_path = root / "core" / "model-policy.md"
    if not policy_path.exists():
        return ValidationReport((
            ValidationIssue(
                code="model_policy.missing",
                severity=Severity.ERROR,
                message=f"Missing model policy: {policy_path}",
                path=str(policy_path),
            ),
        ))

    content = read_text(policy_path)
    issues = []
    successes = []

    for text in REQUIRED_HEADINGS:
        pattern = r"(?im)^##\s+.*" + re.escape(text) + r".*$"
        if re.search(pattern, content):
            successes.append(f"OK heading {text}")
        else:
            issues.append(ValidationIssue(
                code="model_policy.heading_missing",
                severity=Severity.ERROR,
                message=f"Model policy is missing required heading containing: {text}",
                path=str(policy_path),
            ))

    for pattern, label in REQUIRED_PATTERNS:
        if re.search(pattern, content):
            successes.append(f"OK policy {label}")
        else:
            issues.append(ValidationIssue(
                code="model_policy.rule_missing",
                severity=Severity.ERROR,
                message=f"Model policy is missing or changed: {label}",
                path=str(policy_path),
            ))

    return ValidationReport(tuple(issues), tuple(successes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    report = validate_model_policy(args.root)
    for message in report.successes:
        print(message)
    if not report.passed:
        for issue in report.issues:
            print(f"ERROR {issue.message}", file=sys.stderr)
        raise SystemExit(f"Model policy validation failed: {len(report.issues)} error(s)")

    print("Model policy validation completed.")


if __name__ == "__main__":
    main()
