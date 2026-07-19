#!/usr/bin/env python3
"""Validate the Alfred framework structure and run the sub-validators.

Python is the canonical helper runtime; bash is the only installer.
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
    "rules/common/context-retrieval-policy.md",
    "rules/common/verification-loop.md",
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
    "scripts/validators/validate-knowledge.py",
    "scripts/validators/validate-links.py",
    "scripts/validators/validate-context-manifest-fixtures.py",
    "rules/demand-types/playbooks/README.md",
    "rules/demand-types/playbooks/migration.md",
    "install/README.md",
    "install/install.sh",
    "hosts/README.md",
    "hosts/_template/shim.md",
    "hosts/_template/hosts.json",
    "hosts/devin-cli/SKILL.md",
    "hosts/devin-cli/environment-management.md",
    "hosts/devin-cli/config.template.json",
    "hosts/devin-cli/config.local.template.json",
    "hosts/claude-code/SKILL.md",
    "hosts/github-copilot/copilot-instructions.md",
    "hosts/codex/AGENTS.md",
    "docs/implementation-status.md",
    "docs/layer-1-framework-closure.md",
    "docs/onboarding-sigla.md",
    "docs/framework-validation.md",
    "docs/host-adapter-readiness.md",
    "docs/scripts-architecture.md",
    "docs/version-adoption.md",
    "docs/release-governance.md",
    "docs/hardening-pilot-matrix.md",
    "CHANGELOG.md",
    "docs/skills-activation.md",
    "skills/lang-python/SKILL.md",
    "skills/lang-sql/SKILL.md",
    "skills/lang-terraform/SKILL.md",
    "skills/platform-aws-data/SKILL.md",
    "scripts/workflow/alfred-boot.py",
    "scripts/workflow/context-manifest.py",
    "scripts/workflow/generate-host-shims.py",
    "scripts/workflow/generate-registry.py",
    "scripts/workflow/generate-memory-index.py",
    "scripts/workflow/render-toolbar.py",
    "scripts/workflow/sync-host-shims.py",
    "scripts/workflow/devin-rtk-hook.py",
    "scripts/workflow/devin-context-hook.py",
    "scripts/workflow/context-read-advisor.py",
    "scripts/workflow/memory-query.py",
    "scripts/workflow/migrate-state-v2.py",
    "scripts/metrics/collect-observability.py",
    "scripts/metrics/generate-metrics-rollup.py",
    "scripts/metrics/generate-metrics-insights.py",
    "scripts/metrics/observability.py",
    "scripts/metrics/import-ccusage.py",
    "scripts/metrics/apply-usage-rate-card.py",
    "scripts/metrics/normalize-usage-cost.py",
    "scripts/metrics/measure-context-budget.py",
    "scripts/metrics/session-cost.py",
    "scripts/metrics/evaluate-context-benchmark.py",
    "scripts/validators/validate-devin-blueprint.py",
    ".github/workflows/validate.yml",
    "scripts/metrics/budget-monitor.py",
    "scripts/shared/__init__.py",
    "scripts/shared/context_budget.py",
    "scripts/shared/observability/domain/models.py",
    "scripts/shared/observability/domain/enums.py",
    "scripts/shared/observability/application/ports/adapters.py",
    "scripts/shared/observability/application/use_cases/reconcile_usage_summary.py",
    "scripts/shared/observability/infrastructure/repositories/jsonl_event_repository.py",
    "scripts/shared/observability/infrastructure/repositories/json_usage_summary_repository.py",
    "scripts/shared/observability/composition/adapter_bootstrap.py",
    "scripts/shared/observability/presentation/toolbar_presenter.py",
    "scripts/validators/validate-framework.py",
    "scripts/validators/validate-demand.py",
    "scripts/validators/validate-reverse-eng-staleness.py",
    "scripts/validators/validate-sdd-gate.py",
    "scripts/validators/validate-toolbar-fixtures.py",
    "scripts/validators/validate-skills-registry.py",
    "scripts/validators/validate-connectors.py",
    "scripts/validators/validate-email-adapter.py",
    "scripts/validators/validate-tool-discovery-policy.py",
    "scripts/validators/validate-context-compression-policy.py",
    "scripts/validators/validate-token-economy-policy.py",
    "scripts/validators/validate-observability-hygiene.py",
    "scripts/validators/validate-observability-intelligence.py",
    "scripts/validators/validate-scripts-architecture.py",
    "scripts/validators/validate-model-policy.py",
    "scripts/validators/validate-context-budget.py",
    "connectors/usage-cost.md",
    "connectors/usage-rate-card.md",
    "connectors/adapter-template.md",
    "docs/adapter-implementation.md",
    "examples/connectors",
    "examples/connectors/vcs-git-dry-run-adapter.md",
    "examples/connectors/tracker-sim-adapter.md",
    "examples/connectors/tracker-sim-demand.md",
    "examples/connectors/notification-sim-adapter.md",
    "examples/connectors/ccusage-session.json",
    "examples/connectors/usage-rate-card.json",
    "examples/connectors/usage-export.jsonl",
    "examples/connectors/usage-attribution-events.jsonl",
    "examples/connectors/usage-attribution-tokens-only.jsonl",
    "examples/connectors/observability-decision-events.jsonl",
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
    "examples/context-manifest-fixtures/safe-engineering-migration.txt",
    "examples/generated/metrics-rollup.md",
    "examples/generated/insights.md",
    "examples/observability-fixtures/example-demand/05-operation/011-observability-log.jsonl",
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
        "scripts/workflow/sync-host-shims.py": [
            "HOST_SOURCES",
            "claude-code",
            "devin-cli",
            "codex",
            "Host shim sync completed",
            "InstallHooks",
            "claude-code-usage-hook.py",
        ],
        "hosts/_template/hosts.json": [
            "alfred.py host sync --host claude-code --install-hooks",
            "alfred.py host sync --host devin-cli --install-hooks",
            "alfred.py host sync --host codex",
        ],
        "hosts/claude-code/SKILL.md": [
            "alfred.py host sync --host claude-code --install-hooks",
            "-RegisterActive",
        ],
        "hosts/devin-cli/SKILL.md": [
            "alfred.py host sync --host devin-cli --install-hooks",
        ],
        "hosts/codex/AGENTS.md": [
            "alfred.py host sync --host codex",
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
            str(root / "scripts/workflow/sync-host-shims.py"),
            "-Host",
            "claude-code",
            "-AlfredHome",
            str(root),
            "-Target",
            str(root / ".tmp-sync-check" / "SKILL.md"),
            "-Create",
            "-InstallHooks",
            "-ClaudeSettingsPath",
            str(root / ".tmp-sync-check" / "settings.json"),
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
    if "DRY-RUN claude-code hook" not in result.stdout:
        raise SystemExit("Host shim sync dry-run did not report Claude Code hook action")
    print("OK host shim sync policy")


def assert_toolbar_rendering_policy(root):
    checks = {
        "core/boot.md": [
            "scripts/workflow/render-toolbar.py",
            "-RegisterActive",
            "load `presentation/toolbar-quick.md`",
            "do not hand-draw a rich toolbar from memory",
        ],
        "rules/agents/orchestrator.md": [
            "scripts/workflow/render-toolbar.py",
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
            "Never forecast the demand from a",
            "-RegisterActive",
        ],
        "core/presentation/toolbar.md": [
            "Session totals",
            "A linear forecast appears only when demand-scoped cost",
        ],
        "docs/framework-validation.md": [
            "Toolbar forecast display is demand-scoped only",
            "0<progress<100",
        ],
        "docs/automation-fallback.md": [
            "--allow-text-fallback",
            "load `core/presentation/toolbar-quick.md`",
            "do not hand-draw the rich block",
        ],
        "scripts/workflow/render-toolbar.py": [
            "allow_text_fallback",
            "--profile text is the degraded fallback",
            "--allow-text-fallback",
            "RegisterActive",
            "active-demand.json",
            "--no-fence",
        ],
        "scripts/shared/observability/presentation/toolbar_presenter.py": [
            "fonte de custo não configurada",
            "adapter de uso não configurado",
            "CostForecastService",
        ],
        "scripts/metrics/claude-code-usage-hook.py": [
            "active-demand.json",
            "render-toolbar.py -RegisterActive",
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
            str(root / "scripts/workflow/render-toolbar.py"),
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
    if "Previs" in result.stdout or "session" not in result.stdout:
        raise SystemExit("Toolbar must not forecast demand cost from unavailable or session-only cost.")
    print("OK toolbar rendering policy")


def assert_usage_cost_policy(root):
    checks = {
        "connectors/usage-cost.md": [
            "host_cost_command",
            "Claude Code `/cost`",
            "cost source: host_cost_command",
            "cost usd: <value>",
            "usage_rate_card",
            "Do not allocate a ccusage session total",
        ],
        "connectors/usage-rate-card.md": [
            "usage-rate-card",
            "append_cost_event",
            "usage_cost_attributed",
            "ccusage session totals",
        ],
        "docs/usage-cost-adoption.md": [
            "## Claude Code Manual Cost Capture",
            "## Interaction Cost from Rate Cards",
            "Ask the human to run `/cost`",
            "cost usd: <numeric USD value>",
        ],
        "hosts/claude-code/SKILL.md": [
            "## Cost (host-specific",
            "automatically import the current local CLI session",
            "Claude Code may also expose the current session cost through `/cost`",
            "renderer reads `cost usd`",
            "apply-usage-rate-card.py",
        ],
        "templates/hub/state.md": [
            "- cost source:",
            "- cost usd:",
            "- cost confidence:",
            "- cost granularity:",
        ],
        "core/presentation/toolbar-quick.md": [
            "If `state` has session-level `cost usd:`",
            "Claude Code `/cost`",
            "Do not read ccusage session totals from observability JSONL",
            "do not treat",
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


def assert_bash_only_installer_policy(root):
    # Scope is fixed on purpose: CHANGELOG.md and docs/plan/* are historical
    # records and must keep naming install.ps1 (see validate-links.py).
    live_docs = [
        "AGENTS.md",
        "install/README.md",
        "docs/automation-fallback.md",
        "scripts/README.md",
        "core/hooks/rtk.md",
        "hosts/_template/hosts.json",
        "connectors/codebase-memory.md",
    ]
    if (root / "install/install.ps1").exists():
        raise SystemExit(
            "bash is the only installer; owner decision 2026-07-15: "
            "install/install.ps1 must not exist"
        )
    installer = (root / "install/install.sh").read_text(encoding="utf-8")
    if "#!/usr/bin/env bash" not in installer:
        raise SystemExit("install/install.sh must declare #!/usr/bin/env bash")
    for rel in live_docs:
        if "install.ps1" in (root / rel).read_text(encoding="utf-8"):
            raise SystemExit(f"Stale PowerShell installer reference in {rel}: install.ps1")
    print("OK bash-only installer policy")


def assert_ccusage_import_policy(root):
    checks = {
        "connectors/usage-cost.md": [
            "scripts/metrics/import-ccusage.py",
            "ccusage session --json",
            "cost source: ccusage",
            "cost granularity: session",
            "must not be appended",
            "cost confidence:",
            "estimated",
        ],
        "docs/usage-cost-adoption.md": [
            "ccusage` import is active",
            "Claude Code automatic path",
            "selection_method: latest_agent_session",
            "API import remains",
            "Session totals are state fields",
        ],
        "hosts/_template/hosts.json": [
            "automatically import the current local CLI session",
            "do not append the ccusage session total",
            "For Devin, automatic usage attribution requires",
            "append JSONL only when the export provides interaction/request-granular usage",
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
            "does not append session totals to observability JSONL",
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
            str(root / "scripts/metrics/import-ccusage.py"),
            "-InputPath",
            str(root / "examples/connectors/ccusage-session.json"),
            "-Host",
            "claude-code",
            "-EmitJson",
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
    if event.get("event_type") == "usage_attributed":
        raise SystemExit("ccusage session totals must not emit usage_attributed")
    if event.get("record_type") != "session_usage_snapshot":
        raise SystemExit("ccusage import fixture did not emit a session snapshot")
    if event.get("output", {}).get("cost_usd") != 1.23:
        raise SystemExit("ccusage import fixture did not map totalCost")
    metadata = event.get("metadata", {})
    if metadata.get("source_kind") != "ccusage" or metadata.get("granularity") != "session":
        raise SystemExit("ccusage import fixture did not mark source kind and session granularity")
    print("OK ccusage import policy")


def assert_usage_rate_card_policy(root):
    checks = {
        "metrics/metrics.md": [
            "usage_cost_attributed",
            "approved `usage-rate-card`",
            "Session totals",
            "allocated into interaction cost",
        ],
        "core/hooks/usage-attribution.md": [
            "usage-rate-card",
            "usage_cost_attributed",
            "not in the interaction JSONL log",
        ],
        "scripts/README.md": [
            "apply-usage-rate-card",
            "never allocates `ccusage` session totals",
        ],
        "hosts/_template/hosts.json": [
            "apply-usage-rate-card.py",
            "do not allocate session ACU/USD totals",
        ],
        "scripts/metrics/attribute-usage-transcript.py": [
            "--rate-card-path",
            "--allocate-cost/--session-cost-usd are deprecated",
            "ccusage/session totals are not allocated",
        ],
        "scripts/metrics/apply-usage-rate-card.py": [
            "usage_cost_attributed",
            "rate_card_hash",
            "no session-total allocation",
        ],
        "scripts/metrics/generate-metrics-rollup.py": [
            "USAGE_EVENT",
            "COST_EVENT",
            "tokens_cache_read",
            "cache_reuse_ratio",
        ],
        "scripts/validators/validate-observability-intelligence.py": [
            "cursor",
            "AI_OBS_RAW_LOG",
            "usage_cost_attributed",
            "Human decision: pending",
        ],
        "scripts/validators/validate-scripts-architecture.py": [
            "Forbidden import",
            "Shared package must not import",
            "SyntheticCreditAdapter",
        ],
    }
    for rel, phrases in checks.items():
        text = (root / rel).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                raise SystemExit(f"Usage rate card policy missing in {rel}: {phrase}")

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/metrics/apply-usage-rate-card.py"),
            "-InputPath",
            str(root / "examples/connectors/usage-attribution-tokens-only.jsonl"),
            "-RateCardPath",
            str(root / "examples/connectors/usage-rate-card.json"),
            "-NoAppend",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise SystemExit("usage rate card fixture failed")
    event = json.loads(result.stdout.strip().splitlines()[-1])
    if event.get("event_type") != "usage_cost_attributed":
        raise SystemExit("rate card helper must emit usage_cost_attributed")
    if event.get("parent_event_id") != "usage-example-tokens-001":
        raise SystemExit("rate card helper did not reference the parent usage event")
    if event.get("output", {}).get("cost_usd", 0) <= 0:
        raise SystemExit("rate card helper did not compute a positive cost")
    if event.get("output", {}).get("cost_confidence") != "rated":
        raise SystemExit("rate card helper did not preserve rated confidence")
    print("OK usage rate card policy")


def assert_hardening_contracts(root):
    state = (root / "templates/hub/state.md").read_text(encoding="utf-8-sig")
    for field in ("usage schema: alfred.usage.v2", "usage unit:", "usage observed at:", "usage cycle reset at:"):
        if field not in state:
            raise SystemExit(f"Usage v2 state contract missing: {field}")
    for legacy in ("usage acu cycle:", "usage acu display:", "demand acu:", "session acu:"):
        if legacy in state:
            raise SystemExit(f"Legacy usage field remains in state template: {legacy}")

    devin = json.loads((root / "hosts/devin-cli/config.template.json").read_text(encoding="utf-8"))
    permissions = devin.get("permissions") or {}
    if "Exec(git)" in permissions.get("allow", []):
        raise SystemExit("Devin config must not allow every git command")
    for denied in ("Exec(git reset --hard)", "Exec(git clean -f)", "Exec(git push --force)"):
        if denied not in permissions.get("deny", []):
            raise SystemExit(f"Devin config missing deny rule: {denied}")

    local = (root / "hosts/devin-cli/config.local.template.json").read_text(encoding="utf-8")
    if "--api-key" in local or "CONTEXT7_API_KEY" not in local:
        raise SystemExit("Context7 secret must be injected by environment, never argv")
    installer = (root / "install/install.sh").read_text(encoding="utf-8-sig")
    for marker in ("ALFRED_RTK_SHA256", "RTK SHA-256 mismatch"):
        if marker not in installer:
            raise SystemExit(f"Installer checksum contract missing: {marker}")
    email_adapter = (root / "scripts/adapters/mcp-email-server.py").read_text(encoding="utf-8-sig")
    if 'file_smtp.get("password", "")' in email_adapter or "secret_in_file" not in email_adapter:
        raise SystemExit("E-mail adapter must refuse legacy file-based SMTP passwords")

    verification = (root / "rules/common/verification-loop.md").read_text(encoding="utf-8-sig")
    for marker in ("Guided-then-strict corrections", "Guided autonomy", "Corrective", "Strict minimal"):
        if marker not in verification:
            raise SystemExit(f"Guided-then-strict contract missing: {marker}")
    execution_plan = (root / "templates/hub/execution-plan.md").read_text(encoding="utf-8-sig")
    for marker in ("## Relatorios de exploracao", "Arquivos/simbolos", "Nao investigado", "## Tentativas de implementacao"):
        if marker not in execution_plan:
            raise SystemExit(f"Exploration/attempt evidence contract missing: {marker}")
    model_policy = (root / "core/model-policy.md").read_text(encoding="utf-8-sig")
    for marker in ("## Conditional delegation", "1-3 focused tasks", "no claimed model-cost saving"):
        if marker not in model_policy:
            raise SystemExit(f"Conditional delegation contract missing: {marker}")
    routing_eval = (root / "docs/hardening-pilot-matrix.md").read_text(encoding="utf-8-sig")
    for marker in ("## Organizational-routing eval", "strong direct", "review-only", "total usage"):
        if marker not in routing_eval:
            raise SystemExit(f"Organizational-routing eval contract missing: {marker}")
    print("OK hardening contracts")


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
    assert_jsonl(root / "examples/connectors/observability-decision-events.jsonl")
    assert_question_format_policy(root)
    assert_gender_neutral_persona_policy(root)
    assert_host_shim_sync_policy(root)
    assert_toolbar_rendering_policy(root)
    assert_usage_cost_policy(root)
    assert_optional_npm_tools_policy(root)
    assert_bash_only_installer_policy(root)
    assert_ccusage_import_policy(root)
    assert_usage_rate_card_policy(root)
    assert_hardening_contracts(root)

    run_sub(root, "scripts/validators/validate-toolbar-fixtures.py", "-Root", str(root))
    run_sub(root, "scripts/workflow/generate-registry.py", "-Root", str(root), "--check")
    run_sub(root, "scripts/workflow/generate-host-shims.py", "-Root", str(root), "--check")
    run_sub(root, "scripts/workflow/generate-memory-index.py",
            "-Root", str(root / "examples/memory-fixtures/hub"), "--check")
    run_sub(root, "scripts/validators/validate-context-manifest-fixtures.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-skills-registry.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-connectors.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-email-adapter.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-tool-discovery-policy.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-context-compression-policy.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-token-economy-policy.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-context-budget.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-devin-blueprint.py",
            "--path", str(root / "examples/devin-fixtures/enterprise-blueprint.yaml"),
            "--tier", "enterprise")
    run_sub(root, "scripts/validators/validate-observability-hygiene.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-observability-intelligence.py")
    run_sub(root, "scripts/validators/validate-scripts-architecture.py")
    run_sub(root, "scripts/validators/validate-model-policy.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-knowledge.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-links.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-demand.py",
            "-HubDemandPath", str(root / STRICT_EXAMPLE_DEMAND),
            "-AppDemandPath", str(root / STRICT_EXAMPLE_APP_DEMAND),
            "-AppCurrentCommit", STRICT_EXAMPLE_APP_COMMIT,
            "--strict")
    run_sub(root, "scripts/workflow/alfred-boot.py", "-Root", str(root))
    run_sub(root, "scripts/validators/validate-reverse-eng-staleness.py",
            "-ReverseEngPath", str(root / "examples/staleness-fixtures/reverse-eng-fresh.md"),
            "-CurrentCommit", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    run_sub(root, "scripts/validators/validate-sdd-gate.py", "-HubDemandPath", str(root / STRICT_EXAMPLE_DEMAND))

    print("Framework validation completed.")


if __name__ == "__main__":
    main()
