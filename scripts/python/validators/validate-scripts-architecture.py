#!/usr/bin/env python3
"""Validate SOLID boundaries in the Python helper scripts."""

import ast
import sys
from decimal import Decimal
from pathlib import Path

PYTHON_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "shared"
OBS = PACKAGE / "observability"
ENTRYPOINT_DIRS = ("workflow", "metrics", "validators", "adapters")


def imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    output = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            output.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            output.append(node.module or "")
    return output


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
        if not (PYTHON_ROOT / dirname).exists():
            fail(f"Missing scripts entrypoint directory: {dirname}")
    toolbar = PYTHON_ROOT / "workflow" / "render-toolbar.py"
    toolbar_imports = imports(toolbar)
    for forbidden in ("ccusage", "attribute-usage-transcript", "claude-code-usage-hook"):
        if any(forbidden in item for item in toolbar_imports):
            fail(f"Toolbar imports forbidden runtime source: {forbidden}")


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
    assert_domain_behaviors()
    assert_substitution()
    print("Scripts architecture validation completed.")


if __name__ == "__main__":
    main()
