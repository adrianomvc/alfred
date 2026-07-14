#!/usr/bin/env python3
"""Validate the Alfred model policy."""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_text  # noqa: E402
from shared.model_policy import CLAUDE_TIER_MODEL, FLOOR_BY_LANE, resolve_model_policy  # noqa: E402
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
    (r"(?im)toolbar shows the \*\*model actually running\*\*", "toolbar declares the running model"),
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

    check_resolver_consistency(content, policy_path, issues, successes)
    return ValidationReport(tuple(issues), tuple(successes))


def resolver_issue(message, policy_path):
    return ValidationIssue(
        code="model_policy.resolver_drift",
        severity=Severity.ERROR,
        message=message,
        path=str(policy_path),
    )


def check_resolver_consistency(content, policy_path, issues, successes):
    """The runtime resolver (shared/model_policy.py) is what actually applies the
    policy. Assert it matches the markdown floors + tier->model map and encodes
    the key resolved outcomes, so "written" and "applied" cannot drift."""
    # Floors mirror the markdown table.
    for lane, tier in REQUIRED_FLOORS.items():
        if FLOOR_BY_LANE.get(lane.lower()) != tier:
            issues.append(resolver_issue(
                f"Resolver floor for {lane} is {FLOOR_BY_LANE.get(lane.lower())!r}, markdown says {tier!r}", policy_path))
        else:
            successes.append(f"OK resolver floor {lane}={tier}")

    # Tier -> concrete model rows match the markdown table.
    for tier, model in CLAUDE_TIER_MODEL.items():
        pattern = r"(?im)^\|\s*" + tier + r"\s*\|\s*`?" + re.escape(model) + r"`?\s*\|"
        if re.search(pattern, content):
            successes.append(f"OK resolver model {tier}->{model}")
        else:
            issues.append(resolver_issue(
                f"Resolver maps tier {tier!r} to {model!r} but the markdown tier->model table does not", policy_path))

    # Key resolved outcomes the policy commits to.
    expectations = [
        ("Standard", "Design", "strong", "Design pinned strong on every lane"),
        ("SAFE", "Design", "strong", "Design pinned strong on every lane"),
        ("FAST", "Execution", "medium", "Execution never runs on cheap"),
        ("FAST", "Inception", "strong", "FAST Inception compensated up to strong"),
        ("Standard", "Inception", "medium", "Standard Inception is medium"),
        ("SAFE", "Validate", "strong", "SAFE floor holds on Validate"),
        ("SAFE", "Operation", "medium", "Operate may drop to medium even in SAFE"),
        ("FAST", "Operation", "cheap", "cheap remains only for FAST Operate"),
    ]
    for lane, phase, tier, why in expectations:
        decision = resolve_model_policy(lane, phase)
        if decision is None or decision.tier != tier:
            got = None if decision is None else decision.tier
            issues.append(resolver_issue(
                f"Resolver {lane}/{phase} tier={got!r}, policy requires {tier!r} ({why})", policy_path))
        else:
            successes.append(f"OK resolver {lane}/{phase}={tier}")


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
