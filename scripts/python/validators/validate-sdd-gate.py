#!/usr/bin/env python3
"""Validate the minimum SDD clarity gate before Execution.

Python mirror of ``scripts/powershell/validators/validate-sdd-gate.ps1``.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_lines, read_text  # noqa: E402


def has_useful_content(path):
    """Return True if the markdown file has lines beyond headings/labels."""
    skip = [
        re.compile(r"^#"),
        re.compile(r"^>"),
        re.compile(r"^\|[-\s|]+\|$"),
        re.compile(r"^-\s*[A-Za-z /]+:\s*$"),
        re.compile(r"^\[Resposta\]:\s*$"),
    ]
    for raw in read_lines(path):
        line = raw.strip()
        if line == "":
            continue
        if any(rx.match(line) for rx in skip):
            continue
        return True
    return False


def run(hub_demand_path, app_demand_path="", strict=False):
    issues = []
    output = []

    def add_issue(severity, code, message):
        issues.append((severity, code, message))

    def test_useful(path, label, severity="ERROR"):
        if not path.exists():
            add_issue(severity, f"missing_{label}", f"Missing {label} at {path}")
            return
        if not has_useful_content(path):
            add_issue(severity, f"empty_{label}", f"{label} has no useful content: {path}")
        else:
            output.append(f"OK content {label}")

    def test_section(path, section, severity="WARN"):
        if not path.exists():
            add_issue(severity, "missing_section_file",
                      f"Cannot check section {section} because file is missing: {path}")
            return
        content = read_text(path)
        if not re.search(r"(?im)^##\s+" + re.escape(section) + r"\s*$", content):
            add_issue(severity, "missing_section", f"Missing section '{section}' in {path}")
        else:
            output.append(f"OK section {section}")

    def test_file(path, code, severity="ERROR"):
        if not path.exists():
            add_issue(severity, code, f"Missing {path}")
            return False
        output.append(f"OK file {path}")
        return True

    hub = Path(hub_demand_path).resolve()
    problem = hub / "01-inception/002-problem.md"
    requirements = hub / "01-inception/003-requirements.md"
    risk = hub / "01-inception/004-risk.md"
    tech_inception = hub / "01-inception/005-tech-inception.md"
    decisions = hub / "02-design/006-decisions.md"
    execution_plan = hub / "03-execution/012-execution-plan.md"

    test_useful(problem, "problem")
    test_useful(requirements, "requirements")
    test_useful(risk, "risk", "WARN")
    test_useful(tech_inception, "tech_inception", "WARN")
    test_useful(decisions, "decisions", "WARN")
    test_useful(execution_plan, "execution_plan")

    if execution_plan.exists():
        test_section(execution_plan, "Plano", "ERROR")
        test_section(execution_plan, "Sequencia", "WARN")
        test_section(execution_plan, "Evidencias esperadas", "WARN")

    if app_demand_path:
        app = Path(app_demand_path).resolve()
        spec = app / "02-design/003-spec.md"
        if test_file(spec, "missing_app_spec", "WARN"):
            test_useful(spec, "app_spec", "WARN")
            test_section(spec, "Technical solution", "WARN")
            test_section(spec, "Acceptance criteria", "WARN")
            test_section(spec, "Test plan", "WARN")

    warnings = [i for i in issues if i[0] == "WARN"]
    errors = [i for i in issues if i[0] == "ERROR"]

    for severity, code, message in issues:
        output.append(f"{severity} {code}: {message}")

    output.append(
        f"SDD gate completed. errors={len(errors)}, warnings={len(warnings)}, strict={strict}"
    )
    failed = len(errors) > 0 or (strict and len(warnings) > 0)
    return output, errors, warnings, failed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hub-demand-path", "-HubDemandPath", dest="hub_demand_path", required=True)
    parser.add_argument("--app-demand-path", "-AppDemandPath", dest="app_demand_path", default="")
    parser.add_argument("--strict", "-Strict", dest="strict", action="store_true")
    args = parser.parse_args()

    output, errors, warnings, failed = run(
        args.hub_demand_path, args.app_demand_path, args.strict
    )
    for line in output:
        print(line)
    if failed:
        sys.exit(
            f"SDD gate failed. errors={len(errors)}, warnings={len(warnings)}, strict={args.strict}"
        )


if __name__ == "__main__":
    main()
