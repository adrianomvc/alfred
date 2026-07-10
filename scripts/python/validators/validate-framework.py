#!/usr/bin/env python3
"""Validate the Alfred framework structure and run the sub-validators.

Python is the canonical helper runtime. The PowerShell validator remains a
compatibility entry point for Windows-first host flows.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _common import find_observability_logs, iter_jsonl  # noqa: E402

REQUIRED_PATHS = [
    "core",
    "core/hooks/README.md",
    "core/hooks/rtk.md",
    "core/presentation/README.md",
    "core/presentation/toolbar-quick.md",
    "core/presentation/welcome-screen.md",
    "rules/common",
    "rules/rules-index.md",
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
    "examples/examples.md",
    "rules/common/units.md",
    "rules/common/escalation-triggers.md",
    "rules/common/terminal-token-policy.md",
    "rules/common/prompt-caching-policy.md",
    "rules/common/tool-discovery-policy.md",
    "rules/common/context-compression-policy.md",
    "rules/common/token-budget-policy.md",
    "rules/common/deferred-work-policy.md",
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
    "knowledge/knowledge.md",
    "knowledge/policy-template.md",
    "docs/knowledge-governance.md",
    "docs/automation-fallback.md",
    "scripts/python/validators/validate-knowledge.py",
    "scripts/python/validators/validate-links.py",
    "scripts/python/validators/validate-context-manifest-fixtures.py",
    "rules/demand-types/playbooks/README.md",
    "rules/demand-types/playbooks/migration.md",
    "install/README.md",
    "install/install.ps1",
    "install/install.sh",
    "hosts/README.md",
    "hosts/_template/shim.md",
    "hosts/_template/hosts.json",
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
    "docs/skills-activation.md",
    "skills/lang-python/SKILL.md",
    "skills/lang-sql/SKILL.md",
    "skills/lang-terraform/SKILL.md",
    "skills/platform-aws-data/SKILL.md",
    "scripts/python/workflow/alfred-boot.py",
    "scripts/python/workflow/context-manifest.py",
    "scripts/python/workflow/generate-host-shims.py",
    "scripts/python/workflow/generate-registry.py",
    "scripts/python/workflow/render-toolbar.py",
    "scripts/python/workflow/sync-host-shims.py",
    "scripts/python/metrics/collect-observability.py",
    "scripts/python/metrics/generate-metrics-rollup.py",
    "scripts/python/metrics/import-ccusage.py",
    "scripts/python/metrics/normalize-usage-cost.py",
    "scripts/python/validators/validate-framework.py",
    "scripts/python/validators/validate-demand.py",
    "scripts/python/validators/validate-reverse-eng-staleness.py",
    "scripts/python/validators/validate-sdd-gate.py",
    "scripts/python/validators/validate-toolbar-fixtures.py",
    "scripts/python/validators/validate-skills-registry.py",
    "scripts/python/validators/validate-connectors.py",
    "scripts/python/validators/validate-email-adapter.py",
    "scripts/python/validators/validate-tool-discovery-policy.py",
    "scripts/python/validators/validate-context-compression-policy.py",
    "scripts/python/validators/validate-token-economy-policy.py",
    "scripts/python/validators/validate-model-policy.py",
    "connectors/usage-cost.md",
    "connectors/adapter-template.md",
    "docs/adapter-implementation.md",
    "examples/connectors",
    "examples/connectors/vcs-git-dry-run-adapter.md",
    "examples/connectors/tracker-sim-adapter.md",
    "examples/connectors/tracker-sim-demand.md",
    "examples/connectors/notification-sim-adapter.md",
    "examples/connectors/ccusage-session.json",
    "examples/connectors/usage-export.jsonl",
    "examples/connectors/usage-attribution-events.jsonl",
    "examples/toolbar-fixtures/fast.txt",
    "examples/toolbar-fixtures/safe.txt",
    "examples/toolbar-fixtures/execution-first.txt",
    "examples/toolbar-fixtures/standard-parallel-units.txt",
    "examples/toolbar-states/fast.md",
    "examples/toolbar-states/safe.md",
    "examples/toolbar-states/execution-first.md",
    "examples/toolbar-states/standard.md",
    "examples/context-manifest-fixtures/standard-product-design.txt",
    "examples/context-manifest-fixtures/fast-operational-execution.txt",
    "examples/context-manifest-fixtures/safe-engineering-inception.txt",
    "examples/generated/metrics-rollup.md",
    "examples/generated/insights.md",
    "examples/staleness-fixtures/reverse-eng-fresh.md",
]

STRICT_EXAMPLE_DEMAND = "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/006-simulado-adocao-v2"
STRICT_EXAMPLE_APP_DEMAND = "examples/sq9-pilot/.alfred-docs-app/iniciativa-001-piloto/006-simulado-adocao-v2"
STRICT_EXAMPLE_APP_COMMIT = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def assert_path(root, rel):
    if not (root / rel).exists():
        raise SystemExit(f"Missing required path: {rel}")
    print(f"OK path {rel}")


def assert_jsonl(file_path):
    for line_number, parsed, _ in iter_jsonl(file_path):
        if parsed is None:
            raise SystemExit(f"Invalid JSON in {file_path} at line {line_number}")
    print(f"OK jsonl {file_path}")


def assert_question_format_policy(root):
    text = (root / "rules/common/question-format.md").read_text(encoding="utf-8")
    required = [
        "No host-native question widgets for requirements",
        "must not be used to ask or collect requirements answers",
        "Do not duplicate the question text/options in chat",
        "if a material question is needed, it still goes in the requirements artifact",
    ]
    for phrase in required:
        if phrase not in text:
            raise SystemExit(f"Question-format policy missing: {phrase}")
    forbidden = [
        "question widgets may point",
        "few or no questions, inline",
    ]
    lowered = text.lower()
    for phrase in forbidden:
        if phrase in lowered:
            raise SystemExit(f"Question-format policy still allows deprecated behavior: {phrase}")
    elicitation = (root / "rules/lifecycle/inception/sub-activities/requirements-elicitation.md").read_text(encoding="utf-8")
    if "Do not open host-native question widgets for requirements" not in elicitation:
        raise SystemExit("Requirements elicitation must forbid host-native question widgets.")
    print("OK question-format requirements-file-only policy")


def assert_gender_neutral_persona_policy(root):
    welcome = (root / "core/welcome.md").read_text(encoding="utf-8")
    required = [
        "gender-neutral address",
        "Do not use gendered honorifics",
        "senhor",
        "senhora",
        "senhor(a)",
    ]
    for phrase in required:
        if phrase not in welcome:
            raise SystemExit(f"Gender-neutral persona policy missing: {phrase}")

    forbidden_rendered = ["senhor(a)", "senhor", "senhora", "sir/ma'am", "sir,", "sir.", "ma'am"]
    for rel in ["core/presentation/welcome-screen.md", "docs/assets/alfred-fluxo.svg"]:
        text = (root / rel).read_text(encoding="utf-8").lower()
        for phrase in forbidden_rendered:
            if phrase in text:
                raise SystemExit(f"Rendered persona still uses gendered address in {rel}: {phrase}")

    concept = (root / "docs/plan/alfred-conceptual-plan.md").read_text(encoding="utf-8")
    if "Tratamento cordial e neutro" not in concept or "Não usar \"senhor\"" not in concept:
        raise SystemExit("Conceptual persona plan must record neutral-address guidance.")
    print("OK gender-neutral persona policy")


def assert_host_shim_sync_policy(root):
    checks = {
        "scripts/python/workflow/sync-host-shims.py": [
            "HOST_SOURCES",
            "claude-code",
            "devin-cli",
            "codex",
            "Host shim sync completed",
        ],
        "hosts/_template/hosts.json": [
            "sync-host-shims.py -Host claude-code",
            "sync-host-shims.py -Host devin-cli",
            "sync-host-shims.py -Host codex",
        ],
        "hosts/claude-code/SKILL.md": [
            "sync-host-shims.py -Host claude-code",
        ],
        "hosts/devin-cli/SKILL.md": [
            "sync-host-shims.py -Host devin-cli",
        ],
        "hosts/codex/AGENTS.md": [
            "sync-host-shims.py -Host codex",
        ],
        "hosts/README.md": [
            "Syncing installed host entries",
            "sync-host-shims.py",
        ],
        "install/README.md": [
            "Refresh copied host entries",
            "sync-host-shims.py",
        ],
    }
    for rel, phrases in checks.items():
        text = (root / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                raise SystemExit(f"Host shim sync policy missing in {rel}: {phrase}")

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/python/workflow/sync-host-shims.py"),
            "-Host",
            "claude-code",
            "-AlfredHome",
            str(root),
            "-Target",
            str(root / ".tmp-sync-check" / "SKILL.md"),
            "-Create",
            "-DryRun",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit("Host shim sync dry-run failed")
    if "DRY-RUN claude-code" not in result.stdout:
        raise SystemExit("Host shim sync dry-run did not report expected action")
    print("OK host shim sync policy")


def assert_toolbar_rendering_policy(root):
    checks = {
        "core/boot.md": [
            "scripts/python/workflow/render-toolbar.py",
            "load `presentation/toolbar-quick.md`",
            "do not hand-draw a rich toolbar from memory",
        ],
        "rules/agents/orchestrator.md": [
            "scripts/python/workflow/render-toolbar.py",
            "load `core/presentation/toolbar-quick.md` first",
            "Do not improvise a rich toolbar",
        ],
        "core/presentation/README.md": [
            "The model never produces the rich visual",
            "Do not hand-draw rich toolbar blocks",
            "manual fallback is the documented `text` profile only",
        ],
        "core/presentation/toolbar-quick.md": [
            "## Rendering procedure",
            "Prefer the helper",
            "Do not pass `-Profile text` in a host that renders Unicode/emoji",
            "-AllowTextFallback",
            "Never hand-draw the rich block from memory",
            "progress at 0% or 100%",
        ],
        "core/presentation/toolbar.md": [
            "progress is 0% or 100%",
            "forecast as unavailable",
        ],
        "docs/framework-validation.md": [
            "Toolbar forecast display shows a reason",
            "0<progress<100",
        ],
        "docs/automation-fallback.md": [
            "--allow-text-fallback",
            "load `core/presentation/toolbar-quick.md`",
            "do not hand-draw the rich block",
        ],
        "scripts/python/workflow/render-toolbar.py": [
            "allow_text_fallback",
            "--profile text is the degraded fallback",
            "--allow-text-fallback",
            "indisponível (0% concluído)",
        ],
        "hosts/_template/shim.md": [
            "default rich profile",
            "Do not force `--profile text`",
        ],
    }
    for rel, phrases in checks.items():
        text = (root / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                raise SystemExit(f"Toolbar rendering policy missing in {rel}: {phrase}")
    zero_state = root / "examples/fresh-sigla-onboarding/alfred-docs-hub/iniciativa-001-onboarding-alfred/001-preparar-alfred/001-state.md"
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/python/workflow/render-toolbar.py"),
            "-StatePath",
            str(zero_state),
            "-CostUsd",
            "1.23",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit("Toolbar zero-progress forecast smoke failed")
    if "Previs" not in result.stdout or "indisponível (0% concluído)" not in result.stdout:
        raise SystemExit("Toolbar must explain unavailable forecast at 0% progress with numeric cost.")
    print("OK toolbar rendering policy")


def assert_usage_cost_policy(root):
    checks = {
        "connectors/usage-cost.md": [
            "host_cost_command",
            "Claude Code `/cost`",
            "cost source: host_cost_command",
            "cost usd: <value>",
        ],
        "docs/usage-cost-adoption.md": [
            "## Claude Code Manual Cost Capture",
            "Ask the human to run `/cost`",
            "cost usd: <numeric USD value>",
        ],
        "hosts/claude-code/SKILL.md": [
            "## Cost (host-specific",
            "automatically import the current local CLI session",
            "Claude Code may also expose the current session cost through `/cost`",
            "renderer reads `cost usd`",
        ],
        "templates/hub/state.md": [
            "- cost source:",
            "- cost usd:",
            "- cost confidence:",
        ],
        "core/presentation/toolbar-quick.md": [
            "If `state` has `cost usd:`",
            "Claude Code `/cost`",
        ],
    }
    for rel, phrases in checks.items():
        text = (root / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                raise SystemExit(f"Usage-cost policy missing in {rel}: {phrase}")
    print("OK usage-cost policy")


def assert_optional_npm_tools_policy(root):
    checks = {
        "install/install.ps1": [
            "NpmRegistry",
            "CcusagePackage",
            "CodebaseMemoryPackage",
            "SkipNpmTools",
            "npm tool installed/updated",
            "Alfred works without it",
        ],
        "install/install.sh": [
            "ALFRED_NPM_REGISTRY",
            "ALFRED_CCUSAGE_PACKAGE",
            "ALFRED_CODEBASE_MEMORY_PACKAGE",
            "ALFRED_SKIP_NPM_TOOLS",
            "install_npm_tool",
            "Alfred will degrade",
        ],
        "install/README.md": [
            "npm registry / Artifactory",
            "ALFRED_NPM_REGISTRY",
            "ALFRED_CCUSAGE_PACKAGE",
            "ALFRED_CODEBASE_MEMORY_PACKAGE",
            "Skip npm tools",
        ],
        "connectors/codebase-memory.md": [
            "ALFRED_CODEBASE_MEMORY_PACKAGE",
            "MCP registration remains host-specific",
        ],
        "connectors/usage-cost.md": [
            "ALFRED_CCUSAGE_PACKAGE",
            "ALFRED_NPM_REGISTRY",
        ],
    }
    for rel, phrases in checks.items():
        text = (root / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                raise SystemExit(f"Optional npm tools policy missing in {rel}: {phrase}")
    print("OK optional npm tools policy")


def assert_ccusage_import_policy(root):
    checks = {
        "connectors/usage-cost.md": [
            "scripts/python/metrics/import-ccusage.py",
            "ccusage session --json",
            "cost source: ccusage",
            "cost confidence:",
            "estimated",
        ],
        "docs/usage-cost-adoption.md": [
            "ccusage` import is active",
            "Claude Code automatic path",
            "selection_method: latest_agent_session",
            "API import remains",
        ],
        "hosts/_template/hosts.json": [
            "automatically import the current local CLI session",
            "For Devin, automatic usage attribution requires",
        ],
        "templates/hub/state.md": [
            "- alfred run id:",
            "- host:",
            "- usage session id:",
            "- usage imported at:",
        ],
        "scripts/README.md": [
            "import-ccusage",
            "ccusage session --json",
        ],
    }
    for rel, phrases in checks.items():
        text = (root / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                raise SystemExit(f"ccusage import policy missing in {rel}: {phrase}")

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/python/metrics/import-ccusage.py"),
            "-InputPath",
            str(root / "examples/connectors/ccusage-session.json"),
            "-Host",
            "claude-code",
            "-NoAppend",
            "-NoStateUpdate",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit("ccusage import fixture failed")
    event = json.loads(result.stdout.strip().splitlines()[-1])
    if event.get("event_type") != "usage_attributed":
        raise SystemExit("ccusage import fixture did not emit usage_attributed")
    if event.get("cost_usd") != 1.23:
        raise SystemExit("ccusage import fixture did not map totalCost")
    if event.get("metadata", {}).get("source_kind") != "ccusage":
        raise SystemExit("ccusage import fixture did not mark source_kind")
    print("OK ccusage import policy")


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
    assert_question_format_policy(root)
    assert_gender_neutral_persona_policy(root)
    assert_host_shim_sync_policy(root)
    assert_toolbar_rendering_policy(root)
    assert_usage_cost_policy(root)
    assert_optional_npm_tools_policy(root)
    assert_ccusage_import_policy(root)

    run_sub(root, "scripts/python/validators/validate-toolbar-fixtures.py", "-Root", str(root))
    run_sub(root, "scripts/python/workflow/generate-registry.py", "-Root", str(root), "--check")
    run_sub(root, "scripts/python/workflow/generate-host-shims.py", "-Root", str(root), "--check")
    run_sub(root, "scripts/python/validators/validate-context-manifest-fixtures.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-skills-registry.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-connectors.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-email-adapter.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-tool-discovery-policy.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-context-compression-policy.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-token-economy-policy.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-model-policy.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-knowledge.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-links.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-demand.py",
            "-HubDemandPath", str(root / STRICT_EXAMPLE_DEMAND),
            "-AppDemandPath", str(root / STRICT_EXAMPLE_APP_DEMAND),
            "-AppCurrentCommit", STRICT_EXAMPLE_APP_COMMIT,
            "--strict")
    run_sub(root, "scripts/python/workflow/alfred-boot.py", "-Root", str(root))
    run_sub(root, "scripts/python/validators/validate-reverse-eng-staleness.py",
            "-ReverseEngPath", str(root / "examples/staleness-fixtures/reverse-eng-fresh.md"),
            "-CurrentCommit", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    run_sub(root, "scripts/python/validators/validate-sdd-gate.py", "-HubDemandPath", str(root / STRICT_EXAMPLE_DEMAND))

    print("Framework validation completed.")


if __name__ == "__main__":
    main()
