#!/usr/bin/env python3
"""Validate SOLID boundaries in the Python helper scripts."""

import ast
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "shared"
OBS = PACKAGE / "observability"
ENTRYPOINT_DIRS = ("workflow", "metrics", "validators", "adapters")

# Commands migrated to thin drivers: host-format parsing and cost math must live
# in shared.*, not be reintroduced inline. (Wave 1 ingestion migration.)
MIGRATED_COMMANDS = (
    "attribute-usage-transcript.py",
    "claude-code-usage-hook.py",
    "import-ccusage.py",
    "apply-usage-rate-card.py",
)
# Host-parsing/pricing functions that moved into shared adapters/domain; a
# command redefining them locally is a regression.
FORBIDDEN_COMMAND_DEFS = (
    "load_transcript_requests",
    "raw_events_from_transcript",
    "read_new_lines",
    "session_rows",
    "select_row",
    "operation_for_tool",
    "extract_tool_paths",
    "event_tokens",
    "rate_for",
    "make_cost_event",
    "make_snapshot",
    "make_request_event",
    "make_interaction_events",
    "phase_lane",
)
# Commands that attribute cost must delegate pricing to the domain service.
PRICING_COMMANDS = ("attribute-usage-transcript.py", "apply-usage-rate-card.py")
# Adapters that must carry real host parsing now (not delegate to the generic
# passthrough). Codex/Devin passthrough adapters may exist only in the
# experimental registry until a real source fixture is approved.
REAL_ADAPTER_MODULES = (
    OBS / "infrastructure" / "adapters" / "claude" / "transcript.py",
    OBS / "infrastructure" / "adapters" / "ccusage" / "session.py",
)


def imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    output = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            output.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            output.append(node.module or "")
    return output


def function_defs(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    return {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def fail(message):
    raise SystemExit(message)


def assert_no_imports(base, forbidden):
    for path in base.rglob("*.py"):
        found = imports(path)
        for item in found:
            if any(item == rule or item.startswith(rule + ".") for rule in forbidden):
                fail(f"Forbidden import in {path.relative_to(ROOT)}: {item}")


def assert_architecture():
    if not PACKAGE.exists():
        fail("Missing shared scripts package: scripts/shared")
    for path in PACKAGE.rglob("*.py"):
        found = imports(path)
        for item in found:
            if item == "_common" or item.startswith(("workflow.", "metrics.", "validators.", "adapters.")):
                fail(f"Shared package must not import entrypoint/legacy helpers: {path.relative_to(ROOT)} -> {item}")
    assert_no_imports(OBS / "domain", ["shared.observability.infrastructure", "subprocess", "os", "json"])
    assert_no_imports(OBS / "application", ["shared.observability.infrastructure", "subprocess", "os"])
    assert_no_imports(OBS / "presentation", ["shared.observability.infrastructure", "subprocess", "os"])
    for dirname in ENTRYPOINT_DIRS:
        if not (ROOT / dirname).exists():
            fail(f"Missing scripts entrypoint directory: {dirname}")
    toolbar = ROOT / "workflow" / "render-toolbar.py"
    toolbar_imports = imports(toolbar)
    for forbidden in ("ccusage", "attribute-usage-transcript", "claude-code-usage-hook"):
        if any(forbidden in item for item in toolbar_imports):
            fail(f"Toolbar imports forbidden runtime source: {forbidden}")
    boot = ROOT / "workflow" / "alfred-boot.py"
    boot_imports = imports(boot)
    if "importlib.util" in boot_imports:
        fail("alfred-boot must import shared services directly, not scripts by filename.")
    if "render-toolbar.py" in boot.read_text(encoding="utf-8-sig"):
        fail("alfred-boot must not depend on render-toolbar.py by filename.")
    toolbar_fixtures = ROOT / "validators" / "validate-toolbar-fixtures.py"
    fixture_imports = imports(toolbar_fixtures)
    if "importlib.util" in fixture_imports:
        fail("validate-toolbar-fixtures must import shared toolbar services directly, not scripts by filename.")
    if "render-toolbar.py" in toolbar_fixtures.read_text(encoding="utf-8-sig"):
        fail("validate-toolbar-fixtures must not depend on render-toolbar.py by filename.")
    context_fixtures = ROOT / "validators" / "validate-context-manifest-fixtures.py"
    context_fixture_imports = imports(context_fixtures)
    if "importlib.util" in context_fixture_imports:
        fail("validate-context-manifest-fixtures must import shared services directly, not scripts by filename.")
    if "context-manifest.py" in context_fixtures.read_text(encoding="utf-8-sig"):
        fail("validate-context-manifest-fixtures must not depend on context-manifest.py by filename.")
    tool_discovery = ROOT / "validators" / "validate-tool-discovery-policy.py"
    tool_discovery_imports = imports(tool_discovery)
    if "importlib.util" in tool_discovery_imports:
        fail("validate-tool-discovery-policy must import shared MCP tool metadata directly, not scripts by filename.")
    if "scripts/adapters/mcp-email-server.py" in tool_discovery.read_text(encoding="utf-8-sig"):
        fail("validate-tool-discovery-policy must not depend on mcp-email-server.py by path.")
    validate_demand = ROOT / "validators" / "validate-demand.py"
    demand_imports = imports(validate_demand)
    if "importlib.util" in demand_imports:
        fail("validate-demand must import shared validators directly, not scripts by filename.")
    if "validate-sdd-gate.py" in validate_demand.read_text(encoding="utf-8-sig"):
        fail("validate-demand must not depend on validate-sdd-gate.py by filename.")
    if "validate-reverse-eng-staleness.py" in validate_demand.read_text(encoding="utf-8-sig"):
        fail("validate-demand must not depend on validate-reverse-eng-staleness.py by filename.")
    if "subprocess" in demand_imports:
        fail("validate-demand must compose shared validators directly, not use subprocess internally.")


def assert_commands_delegate():
    """Migrated commands are thin drivers: they import shared.* and never
    reintroduce host-parsing or pricing logic inline."""
    metrics = ROOT / "metrics"
    for name in MIGRATED_COMMANDS:
        path = metrics / name
        if not path.exists():
            fail(f"Missing migrated command: {name}")
        found = imports(path)
        if not any(item.startswith("shared.observability") for item in found):
            fail(f"Migrated command must delegate into shared.observability: {name}")
        local_defs = function_defs(path)
        clashes = local_defs.intersection(FORBIDDEN_COMMAND_DEFS)
        if clashes:
            fail(f"Command reintroduces shared host/parsing logic locally ({name}): {', '.join(sorted(clashes))}")
    for name in PRICING_COMMANDS:
        found = imports(metrics / name)
        if not any("rate_card" in item for item in found):
            fail(f"Cost-attributing command must price via shared rate_card service: {name}")


def assert_real_adapters_not_stub():
    """Host adapters expected to parse must not merely delegate to the generic
    passthrough."""
    for module in REAL_ADAPTER_MODULES:
        if not module.exists():
            fail(f"Missing real adapter module: {module.relative_to(ROOT)}")
        if any("GenericJsonlAdapter" in item for item in imports(module)):
            fail(f"Adapter must implement real parsing, not delegate to GenericJsonlAdapter: {module.relative_to(ROOT)}")
        if "GenericJsonlAdapter" in module.read_text(encoding="utf-8-sig"):
            fail(f"Adapter must not reference GenericJsonlAdapter: {module.relative_to(ROOT)}")


def assert_adapter_roundtrip():
    """Behavioral anti-stub proof: real adapters parse host format into events."""
    sys.path.insert(0, str(ROOT))
    from shared.observability.domain.models import AdapterContext
    from shared.observability.infrastructure.adapters.ccusage.session import CcusageSessionAdapter

    row, method = CcusageSessionAdapter().select_session(
        {"sessions": [{"agent": "claude", "period": "p1", "totalCost": 1.0, "inputTokens": 10, "modelsUsed": ["m"]}]},
        "claude",
        "",
    )
    if row.get("period") != "p1" or method != "latest_agent_session":
        fail("ccusage adapter must select the session row from host payload.")
    events = CcusageSessionAdapter().read_session_usage({"sessions": [row]}, AdapterContext(host="claude-code"))
    if not events or events[0].event_scope != "session" or events[0].cost.value is None:
        fail("ccusage adapter must yield a session-scoped canonical event with cost.")


def assert_registry_contracts():
    sys.path.insert(0, str(ROOT))
    from shared.observability.application.ports.adapters import SessionUsageAdapter, TranscriptUsageAdapter
    from shared.observability.composition.adapter_bootstrap import build_default_registry, build_experimental_registry

    default = build_default_registry()
    default_keys = set(default.registered())
    forbidden_defaults = {
        ("codex", "hook"),
        ("codex", "otel"),
        ("devin-cli", "devin_insights"),
        ("devin-web", "devin_consumption"),
    }
    leaked = sorted(default_keys.intersection(forbidden_defaults))
    if leaked:
        fail(f"Experimental passthrough adapters must not be in the default registry: {leaked}")

    transcript = default.resolve("claude-code", "host_transcript")
    if not isinstance(transcript, TranscriptUsageAdapter):
        fail("claude-code/host_transcript must implement TranscriptUsageAdapter.")
    ccusage = default.resolve("claude-code", "ccusage")
    if not isinstance(ccusage, SessionUsageAdapter):
        fail("claude-code/ccusage must implement SessionUsageAdapter.")

    experimental = build_experimental_registry()
    for key in forbidden_defaults:
        if key not in experimental.registered(include_experimental=True):
            fail(f"Experimental registry missing acknowledged passthrough adapter: {key}")
        if not experimental.is_experimental(*key):
            fail(f"Passthrough adapter must be marked experimental: {key}")


def assert_substitution():
    sys.path.insert(0, str(ROOT))
    from shared.observability.application.ports.adapters import AdapterRegistry
    from shared.observability.domain.models import AdapterCapabilities, AdapterContext

    class SyntheticCreditAdapter:
        def capabilities(self):
            return AdapterCapabilities(session_usage=True)

        def normalize_event(self, payload, context):
            from shared.observability.infrastructure.repositories.jsonl_event_repository import canonical_from_mapping
            return [canonical_from_mapping(payload)]

        def read_usage(self, source, context):
            return self.normalize_event(source, context)

    registry = AdapterRegistry()
    registry.register("synthetic", "credit", SyntheticCreditAdapter)
    adapter = registry.resolve("synthetic", "credit")
    events = adapter.read_usage(
        {
            "schema_version": "alfred.observability.v1",
            "event_id": "synthetic-credit-1",
            "event_type": "usage_attributed",
            "event_scope": "session",
            "ts": "2026-07-12T15:00:00Z",
            "credits": 12,
        },
        AdapterContext(host="synthetic"),
    )
    unit = events[0].usage.dimensions[0].unit if events and events[0].usage.dimensions else None
    unit_value = unit.value if hasattr(unit, "value") else str(unit)
    if unit_value != "credit":
        fail("SyntheticCreditAdapter substitution failed.")


def assert_domain_behaviors():
    sys.path.insert(0, str(ROOT))
    from shared.observability.domain.enums import Confidence, CostScope, UsageUnit
    from shared.observability.domain.models import Cost, ObservedTotal, Usage, UsageDimension
    from shared.observability.domain.services.artifact_classifier import classify_artifact
    from shared.observability.domain.services.forecast import CostForecastService
    from shared.observability.domain.services.usage_calculator import cache_reuse_ratio

    observed_zero = ObservedTotal(Decimal("0"), observed_count=1)
    unknown = ObservedTotal(Decimal("0"), observed_count=0)
    if not observed_zero.is_observed or unknown.is_observed:
        fail("ObservedTotal must distinguish observed zero from unavailable.")

    usage = Usage((
        UsageDimension(UsageUnit.TOKEN_INPUT, Decimal("10"), Confidence.EXACT, "test"),
        UsageDimension(UsageUnit.TOKEN_CACHE_CREATION, Decimal("10"), Confidence.EXACT, "test"),
        UsageDimension(UsageUnit.TOKEN_CACHE_READ, Decimal("30"), Confidence.EXACT, "test"),
    ))
    if cache_reuse_ratio(usage) != Decimal("0.6"):
        fail("cache_reuse_ratio must include input, cache creation, and cache read.")

    if classify_artifact("service_test.py") != "test":
        fail("Artifact classifier must classify tests before generic source code.")

    session_cost = Cost(Decimal("10.00"), "USD", "ccusage", CostScope.SESSION, Confidence.ESTIMATED, Decimal("100"), None)
    demand_cost = Cost(Decimal("2.00"), "USD", "rate_card", CostScope.DEMAND, Confidence.RATED, Decimal("100"), None)
    service = CostForecastService()
    if service.forecast(session_cost, 20, Decimal("80")).value is not None:
        fail("Forecast must not use session-scoped cost.")
    forecast = service.forecast(demand_cost, 20, Decimal("80"))
    if forecast.value != Decimal("10.00"):
        fail("Forecast must use demand-scoped covered cost.")


def main():
    assert_architecture()
    assert_commands_delegate()
    assert_real_adapters_not_stub()
    assert_adapter_roundtrip()
    assert_registry_contracts()
    assert_domain_behaviors()
    assert_substitution()
    print("Scripts architecture validation completed.")


if __name__ == "__main__":
    main()
