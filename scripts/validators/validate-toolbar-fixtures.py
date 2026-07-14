#!/usr/bin/env python3
"""Check that the toolbar renderer does not drift from saved fixtures."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.common import read_text  # noqa: E402
from shared.toolbar.service import render_toolbar  # noqa: E402
from shared.validation import Severity, ValidationIssue, ValidationReport  # noqa: E402

CASES = [
    ("fast",
     "examples/toolbar-states/fast.md",
     "examples/toolbar-fixtures/fast.txt"),
    ("safe",
     "examples/toolbar-states/safe.md",
     "examples/toolbar-fixtures/safe.txt"),
    ("execution-first",
     "examples/toolbar-states/execution-first.md",
     "examples/toolbar-fixtures/execution-first.txt"),
    ("standard-parallel-units",
     "examples/toolbar-states/standard.md",
     "examples/toolbar-fixtures/standard-parallel-units.txt"),
]


def issue(code, message, path=None):
    return ValidationIssue(
        code=code,
        severity=Severity.ERROR,
        message=message,
        path=None if path is None else str(path),
    )


def validate_toolbar_fixtures(root) -> ValidationReport:
    root = Path(root).resolve()
    issues = []
    successes = []

    for name, state_rel, expected_rel in CASES:
        state_path = root / state_rel
        expected_path = root / expected_rel
        if not state_path.exists():
            issues.append(issue(
                "toolbar_fixture.state_missing",
                f"Missing toolbar fixture state for {name}: {state_path}",
                state_path,
            ))
            continue
        if not expected_path.exists():
            issues.append(issue(
                "toolbar_fixture.expected_missing",
                f"Missing toolbar fixture expected output for {name}: {expected_path}",
                expected_path,
            ))
            continue

        actual = "\n".join(render_toolbar(
            str(state_path),
            framework_root=root,
            model="GPT-5",
            cost="n/a",
            profile="text",
        ))
        expected = read_text(expected_path)

        # Normalize line endings before comparing (fixtures use CRLF).
        if actual.replace("\r\n", "\n").rstrip() != expected.replace("\r\n", "\n").rstrip():
            issues.append(issue(
                "toolbar_fixture.drift",
                f"Toolbar fixture drift: {name}. Regenerate or update expected output intentionally.",
                expected_path,
            ))
            continue
        successes.append(f"OK toolbar fixture {name}")

    return ValidationReport(tuple(issues), tuple(successes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    report = validate_toolbar_fixtures(args.root)
    for message in report.successes:
        print(message)
    if not report.passed:
        for item in report.issues:
            print(f"ERROR {item.message}", file=sys.stderr)
        raise SystemExit(f"Toolbar fixture validation failed: {len(report.issues)} error(s)")

    print("Toolbar fixture validation completed.")


if __name__ == "__main__":
    main()
