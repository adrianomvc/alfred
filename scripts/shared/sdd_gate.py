import re
from pathlib import Path

from shared.common import read_lines, read_text

FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]
# Semantic baseline: content only counts when it goes beyond the template mold.
TEMPLATE_FOR = {
    "problem": "templates/hub/problem.md",
    "risk": "templates/hub/risk.md",
    "tech_inception": "templates/hub/tech-inception.md",
    "decisions": "templates/hub/decisions.md",
    "execution_plan": "templates/hub/execution-plan.md",
    "app_spec": "templates/app/spec.md",
}
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}|<\.\.\.>|^<[^>]+>$")
DEFAULT_ROWS = ("| unit-001 |", "| explore-001 |")


def has_useful_content(path, template_path=None):
    """True when the file carries real content beyond headings/labels — and,
    when a template mold is known, beyond the template's own default lines."""
    skip = [
        re.compile(r"^#"),
        re.compile(r"^>"),
        re.compile(r"^\|[-\s|]+\|$"),
        re.compile(r"^-\s*[A-Za-z /]+:\s*$"),
        re.compile(r"^\[Resposta\]:\s*$"),
    ]
    template_lines = set()
    if template_path is not None and Path(template_path).exists():
        template_lines = {raw.strip() for raw in read_lines(template_path) if raw.strip()}
    for raw in read_lines(path):
        line = raw.strip()
        if line == "":
            continue
        if any(rx.match(line) for rx in skip):
            continue
        if PLACEHOLDER.search(line):
            continue
        if any(line.startswith(row) for row in DEFAULT_ROWS):
            continue
        if line in template_lines:
            continue  # verbatim template boilerplate is not demand content
        return True
    return False


def run(hub_demand_path, app_demand_path="", strict=False, lane=""):
    issues = []
    output = []
    fast_lane = lane.strip().upper() == "FAST"

    def add_issue(severity, code, message):
        issues.append((severity, code, message))

    def test_useful(path, label, severity="ERROR"):
        if not path.exists():
            add_issue(severity, f"missing_{label}", f"Missing {label} at {path}")
            return
        template_rel = TEMPLATE_FOR.get(label)
        template = FRAMEWORK_ROOT / template_rel if template_rel else None
        if not has_useful_content(path, template):
            add_issue(severity, f"empty_{label}", f"{label} has no useful content beyond the template: {path}")
        else:
            output.append(f"OK content {label}")

    def test_section(path, section, severity="WARN"):
        # ``section`` may be one name or (canonical EN, legacy pt-BR aliases).
        names = (section,) if isinstance(section, str) else tuple(section)
        if not path.exists():
            add_issue(severity, "missing_section_file",
                      f"Cannot check section {names[0]} because file is missing: {path}")
            return
        content = read_text(path)
        pattern = "|".join(re.escape(name) for name in names)
        if not re.search(r"(?im)^##\s+(?:" + pattern + r")\s*$", content):
            add_issue(severity, "missing_section", f"Missing section '{names[0]}' in {path}")
        else:
            output.append(f"OK section {names[0]}")

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
    if fast_lane:
        # FAST folds Design into Execution: spec lives inline in the PR, so the
        # separate tech-inception/decisions/execution-plan artifacts are optional.
        output.append("SKIP FAST lane: inline Design artifacts not required")
    else:
        test_useful(tech_inception, "tech_inception", "WARN")
        test_useful(decisions, "decisions", "WARN")
        test_useful(execution_plan, "execution_plan")

    if execution_plan.exists():
        test_section(execution_plan, ("Plan", "Plano"), "ERROR")
        test_section(execution_plan, ("Sequence", "Sequencia"), "WARN")
        test_section(execution_plan, ("Expected evidence", "Evidencias esperadas"), "WARN")

    if app_demand_path:
        app = Path(app_demand_path).resolve()
        spec = app / "02-design/003-spec.md"
        if test_file(spec, "missing_app_spec", "WARN"):
            test_useful(spec, "app_spec", "WARN")
            test_section(spec, "Technical solution", "WARN")
            test_section(spec, "Acceptance criteria", "WARN")
            test_section(spec, "Test plan", "WARN")

    warnings = [item for item in issues if item[0] == "WARN"]
    errors = [item for item in issues if item[0] == "ERROR"]

    for severity, code, message in issues:
        output.append(f"{severity} {code}: {message}")

    output.append(
        f"SDD gate completed. errors={len(errors)}, warnings={len(warnings)}, strict={strict}"
    )
    failed = len(errors) > 0 or (strict and len(warnings) > 0)
    return output, errors, warnings, failed
