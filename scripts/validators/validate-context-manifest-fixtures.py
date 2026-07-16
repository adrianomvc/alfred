#!/usr/bin/env python3
"""Check context-manifest output against saved fixtures."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.common import read_text  # noqa: E402
from shared.context_manifest import ContextManifestError, build_manifest  # noqa: E402
from shared.validation import Severity, ValidationIssue, ValidationReport  # noqa: E402

CASES = [
    (
        "standard-product-design",
        {
            "phase": "Design",
            "lane": "Standard",
            "demand_type": "product",
            "agent": "spec-design",
            "sub_activity": "functional-design",
        },
        "examples/context-manifest-fixtures/standard-product-design.txt",
    ),
    (
        "fast-operational-execution",
        {
            "phase": "Execution",
            "lane": "FAST",
            "demand_type": "operational",
            "agent": "orchestrator",
            "sub_activity": "workflow-planning",
        },
        "examples/context-manifest-fixtures/fast-operational-execution.txt",
    ),
    (
        "safe-engineering-inception",
        {
            "phase": "Inception",
            "lane": "SAFE",
            "demand_type": "engineering",
            "agent": "discovery",
            "sub_activity": "risk-mode-proposal",
        },
        "examples/context-manifest-fixtures/safe-engineering-inception.txt",
    ),
    (
        "safe-engineering-migration",
        {
            "phase": "Execution",
            "lane": "SAFE",
            "demand_type": "engineering",
            "agent": "orchestrator",
            "playbook": "migration",
        },
        "examples/context-manifest-fixtures/safe-engineering-migration.txt",
    ),
]

STABLE_PREFIX = [
    "core/principles.md",
    "rules/README.md",
    "rules/rules-index.md",
    "rules/common/overconfidence.md",
]


def issue(code, message, path=None):
    return ValidationIssue(
        code=code,
        severity=Severity.ERROR,
        message=message,
        path=None if path is None else str(path),
    )


def validate_context_manifest_fixtures(root) -> ValidationReport:
    root = Path(root).resolve()
    issues = []
    successes = []

    for name, params, fixture_rel in CASES:
        fixture_path = root / fixture_rel
        if not fixture_path.exists():
            issues.append(issue(
                "context_manifest_fixture.missing",
                f"Missing context-manifest fixture for {name}: {fixture_path}",
                fixture_path,
            ))
            continue

        try:
            actual_lines = build_manifest(root, **params)
        except ContextManifestError as exc:
            issues.append(issue(
                "context_manifest_fixture.render_failed",
                str(exc),
                root,
            ))
            continue
        if actual_lines[:len(STABLE_PREFIX)] != STABLE_PREFIX:
            issues.append(issue(
                "context_manifest_fixture.prefix_drift",
                f"Context manifest cache-friendly prefix drift: {name}. "
                "Stable framework context must remain first.",
                fixture_path,
            ))
            continue
        actual = "\n".join(actual_lines)
        expected = read_text(fixture_path)
        if actual.replace("\r\n", "\n").rstrip() != expected.replace("\r\n", "\n").rstrip():
            issues.append(issue(
                "context_manifest_fixture.drift",
                f"Context manifest fixture drift: {name}. Regenerate or update expected output intentionally.",
                fixture_path,
            ))
            continue
        successes.append(f"OK context manifest fixture {name}")

    return ValidationReport(tuple(issues), tuple(successes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    report = validate_context_manifest_fixtures(args.root)
    for message in report.successes:
        print(message)
    if not report.passed:
        for item in report.issues:
            print(f"ERROR {item.message}", file=sys.stderr)
        raise SystemExit(f"Context manifest fixture validation failed: {len(report.issues)} error(s)")

    print("Context manifest fixture validation completed.")


if __name__ == "__main__":
    main()
