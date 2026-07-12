#!/usr/bin/env python3
"""Validate SOLID boundaries in the observability package."""

import ast
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBS = ROOT / "observability"


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
    assert_no_imports(OBS / "domain", ["observability.infrastructure", "subprocess", "os", "json"])
    assert_no_imports(OBS / "application", ["observability.infrastructure", "subprocess", "os"])
    assert_no_imports(OBS / "presentation", ["observability.infrastructure", "subprocess", "os"])
    toolbar = ROOT / "workflow" / "render-toolbar.py"
    toolbar_imports = imports(toolbar)
    for forbidden in ("ccusage", "attribute-usage-transcript", "claude-code-usage-hook"):
        if any(forbidden in item for item in toolbar_imports):
            fail(f"Toolbar imports forbidden runtime source: {forbidden}")


def assert_substitution():
    sys.path.insert(0, str(ROOT))
    from observability.application.ports.adapters import AdapterRegistry
    from observability.domain.models import AdapterCapabilities, AdapterContext

    class SyntheticCreditAdapter:
        def capabilities(self):
            return AdapterCapabilities(session_usage=True)

        def normalize_event(self, payload, context):
            from observability.infrastructure.repositories.jsonl_event_repository import canonical_from_mapping
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
    from observability.domain.enums import Confidence, CostScope, UsageUnit
    from observability.domain.models import Cost, ObservedTotal, Usage, UsageDimension
    from observability.domain.services.artifact_classifier import classify_artifact
    from observability.domain.services.forecast import CostForecastService
    from observability.domain.services.usage_calculator import cache_reuse_ratio

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
    print("Observability architecture validation completed.")


if __name__ == "__main__":
    main()
