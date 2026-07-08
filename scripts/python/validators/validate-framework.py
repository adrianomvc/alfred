#!/usr/bin/env python3
"""Validate the Alfred framework structure and run the sub-validators.

Python mirror of ``scripts/powershell/validators/validate-framework.ps1``. Runs the
Python sub-validators so the framework can be checked without PowerShell.
"""

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _common import find_observability_logs, iter_jsonl  # noqa: E402

REQUIRED_PATHS = [
    "core",
    "core/presentation/README.md",
    "core/presentation/toolbar-quick.md",
    "core/presentation/welcome-screen.md",
    "rules/common",
    "rules/demand-types",
    "rules/lanes",
    "rules/lifecycle",
    "rules/agents",
    "skills",
    "connectors",
    "metrics",
    "templates/hub",
    "templates/app",
    "docs",
    "examples",
    "rules/common/units.md",
    "rules/common/escalation-triggers.md",
    "rules/common/workflow-changes.md",
    "rules/lifecycle/design/sub-activities/README.md",
    "rules/lifecycle/design/sub-activities/application-design.md",
    "rules/lifecycle/design/sub-activities/functional-design.md",
    "rules/lifecycle/design/sub-activities/nfr-design.md",
    "rules/lifecycle/design/sub-activities/infrastructure-design.md",
    "rules/lifecycle/design/sub-activities/user-stories.md",
    "rules/lifecycle/inception/sub-activities/README.md",
    "rules/lifecycle/inception/sub-activities/business-inception.md",
    "rules/lifecycle/inception/sub-activities/technical-inception.md",
    "rules/lifecycle/inception/sub-activities/requirements-elicitation.md",
    "rules/lifecycle/inception/sub-activities/risk-mode-proposal.md",
    "rules/lifecycle/execution/sub-activities/README.md",
    "rules/lifecycle/execution/sub-activities/workflow-planning.md",
    "rules/lifecycle/execution/sub-activities/unit-loop.md",
    "rules/lifecycle/execution/sub-activities/code-generation.md",
    "rules/lifecycle/execution/sub-activities/technical-review.md",
    "rules/lifecycle/validation/sub-activities/README.md",
    "rules/lifecycle/validation/sub-activities/unit-testing.md",
    "rules/lifecycle/validation/sub-activities/regression-testing.md",
    "rules/lifecycle/validation/sub-activities/integration-testing.md",
    "rules/lifecycle/validation/sub-activities/contract-testing.md",
    "rules/lifecycle/validation/sub-activities/e2e-testing.md",
    "rules/lifecycle/validation/sub-activities/performance-testing.md",
    "rules/lifecycle/validation/sub-activities/security-testing.md",
    "rules/lifecycle/operations/sub-activities/README.md",
    "rules/lifecycle/operations/sub-activities/metrics-collection.md",
    "rules/lifecycle/operations/sub-activities/baseline-drift-check.md",
    "rules/lifecycle/operations/sub-activities/closure-summary.md",
    "rules/lifecycle/operations/sub-activities/hub-sync.md",
    "rules/lifecycle/operations/sub-activities/strategic-notification.md",
    "rules/lifecycle/operations/sub-activities/followup-conversion.md",
    "templates/hub/execution-plan.md",
    "templates/hub/environment-parameters.md",
    "templates/hub/validation-evidence.md",
    "knowledge/README.md",
    "knowledge/policy-template.md",
    "docs/knowledge-governance.md",
    "docs/automation-fallback.md",
    "scripts/powershell/validators/validate-knowledge.ps1",
    "scripts/python/validators/validate-knowledge.py",
    "scripts/powershell/validators/validate-links.ps1",
    "scripts/python/validators/validate-links.py",
    "rules/demand-types/playbooks/README.md",
    "rules/demand-types/playbooks/migration.md",
    "install/README.md",
    "install/install.ps1",
    "install/install.sh",
    "hosts/README.md",
    "hosts/devin-cli/SKILL.md",
    "hosts/claude-code/SKILL.md",
    "hosts/github-copilot/copilot-instructions.md",
    "hosts/codex/AGENTS.md",
    "docs/implementation-status.md",
    "docs/layer-1-framework-closure.md",
    "docs/onboarding-sigla.md",
    "docs/framework-validation.md",
    "docs/host-adapter-readiness.md",
    "docs/version-adoption.md",
    "docs/release-governance.md",
    "CHANGELOG.md",
    "scripts/powershell/workflow/alfred-boot.ps1",
    "scripts/powershell/workflow/render-toolbar.ps1",
    "docs/skills-activation.md",
    "skills/lang-python.md",
    "skills/lang-sql.md",
    "skills/lang-terraform.md",
    "skills/platform-aws-data.md",
    "scripts/powershell/metrics/collect-observability.ps1",
    "scripts/powershell/metrics/generate-metrics-rollup.ps1",
    "scripts/powershell/metrics/normalize-usage-cost.ps1",
    "scripts/powershell/validators/validate-demand.ps1",
    "scripts/powershell/validators/validate-reverse-eng-staleness.ps1",
    "scripts/powershell/validators/validate-sdd-gate.ps1",
    "scripts/powershell/validators/validate-toolbar-fixtures.ps1",
    "scripts/powershell/validators/validate-skills-registry.ps1",
    "scripts/powershell/validators/validate-connectors.ps1",
    "scripts/powershell/validators/validate-model-policy.ps1",
    "scripts/python/workflow/alfred-boot.py",
    "scripts/python/workflow/render-toolbar.py",
    "scripts/python/metrics/collect-observability.py",
    "scripts/python/metrics/generate-metrics-rollup.py",
    "scripts/python/metrics/normalize-usage-cost.py",
    "scripts/python/validators/validate-framework.py",
    "scripts/python/validators/validate-demand.py",
    "scripts/python/validators/validate-reverse-eng-staleness.py",
    "scripts/python/validators/validate-sdd-gate.py",
    "scripts/python/validators/validate-toolbar-fixtures.py",
    "scripts/python/validators/validate-skills-registry.py",
    "scripts/python/validators/validate-connectors.py",
    "scripts/python/validators/validate-model-policy.py",
    "connectors/usage-cost.md",
    "connectors/adapter-template.md",
    "docs/adapter-implementation.md",
    "examples/connectors",
    "examples/connectors/vcs-git-dry-run-adapter.md",
    "examples/connectors/tracker-sim-adapter.md",
    "examples/connectors/tracker-sim-demand.md",
    "examples/connectors/notification-sim-adapter.md",
    "examples/connectors/usage-export.jsonl",
    "examples/connectors/usage-attribution-events.jsonl",
    "examples/toolbar-fixtures/fast.txt",
    "examples/toolbar-fixtures/safe.txt",
    "examples/toolbar-fixtures/execution-first.txt",
    "examples/toolbar-fixtures/standard-parallel-units.txt",
    "examples/generated/metrics-rollup.md",
    "examples/generated/insights.md",
    "examples/staleness-fixtures/reverse-eng-fresh.md",
]

EXAMPLE_DEMAND = "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units"


def assert_path(root, rel):
    if not (root / rel).exists():
        raise SystemExit(f"Missing required path: {rel}")
    print(f"OK path {rel}")


def assert_jsonl(file_path):
    for line_number, parsed, _ in iter_jsonl(file_path):
        if parsed is None:
            raise SystemExit(f"Invalid JSON in {file_path} at line {line_number}")
    print(f"OK jsonl {file_path}")


def run_sub(root, rel_script, *script_args):
    script = root / rel_script
    result = subprocess.run(
        [sys.executable, str(script), *script_args],
        capture_output=True, text=True,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit(f"Sub-validator failed: {rel_script}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    for rel in REQUIRED_PATHS:
        assert_path(root, rel)

    for log in find_observability_logs(root / "examples"):
        assert_jsonl(log)

    assert_jsonl(root / "examples/connectors/usage-export.jsonl")
    assert_jsonl(root / "examples/connectors/usage-attribution-events.jsonl")

    run_sub(root, "scripts/python/validators/validate-toolbar-fixtures.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-skills-registry.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-connectors.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-model-policy.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-knowledge.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-links.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-demand.py", "-HubDemandPath", str(root / EXAMPLE_DEMAND))
    run_sub(root, "scripts/python/workflow/alfred-boot.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-reverse-eng-staleness.py",
            "-ReverseEngPath", str(root / "examples/staleness-fixtures/reverse-eng-fresh.md"),
            "-CurrentCommit", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    run_sub(root, "scripts/python/validators/validate-sdd-gate.py", "-HubDemandPath", str(root / EXAMPLE_DEMAND))

    print("Framework validation completed.")


if __name__ == "__main__":
    main()
