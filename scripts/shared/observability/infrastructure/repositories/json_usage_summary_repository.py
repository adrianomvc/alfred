import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from shared.observability.domain.enums import Confidence, CostScope, UsageUnit
from shared.observability.domain.models import Cost, SummaryKey, Usage, UsageDimension, UsageSummary


def summary_path(key: SummaryKey) -> Path:
    return Path(key.state_path).with_name("001-usage-summary.json")


def cost_to_json(cost: Cost) -> dict[str, object]:
    return {
        "value": None if cost.value is None else str(cost.value),
        "currency": cost.currency,
        "source": cost.source,
        "scope": None if cost.scope is None else cost.scope.value,
        "confidence": cost.confidence.value,
        "coverage_percent": None if cost.coverage_percent is None else str(cost.coverage_percent),
    }


def usage_to_json(usage: Usage) -> dict[str, object]:
    return {
        "dimensions": [
            {"unit": str(item.unit.value if hasattr(item.unit, "value") else item.unit), "value": str(item.value), "confidence": item.confidence.value, "source": item.source}
            for item in usage.dimensions
        ]
    }


class JsonUsageSummaryRepository:
    def save(self, key: SummaryKey, summary: UsageSummary) -> Path:
        path = summary_path(key)
        payload = {
            "schema_version": summary.schema_version,
            "provider": summary.provider,
            "host": summary.host,
            "adapter": summary.adapter,
            "updated_at": summary.updated_at.isoformat().replace("+00:00", "Z"),
            "session": {"usage": usage_to_json(summary.session_usage), "cost": cost_to_json(summary.session_cost)},
            "demand": {"usage": usage_to_json(summary.demand_usage), "cost": cost_to_json(summary.demand_cost)},
            "cache_reuse_ratio": None if summary.cache_reuse_ratio is None else str(summary.cache_reuse_ratio),
            "gaps": list(summary.gaps),
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def load(self, key: SummaryKey) -> UsageSummary | None:
        path = summary_path(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        return UsageSummary(
            schema_version=payload.get("schema_version", "alfred.usage-summary.v1"),
            provider=payload.get("provider"),
            host=payload.get("host"),
            adapter=payload.get("adapter"),
            updated_at=datetime.fromisoformat(str(payload.get("updated_at")).replace("Z", "+00:00")),
            session_usage=_usage_from_json((payload.get("session") or {}).get("usage") or {}),
            session_cost=_cost_from_json((payload.get("session") or {}).get("cost") or {}),
            demand_usage=_usage_from_json((payload.get("demand") or {}).get("usage") or {}),
            demand_cost=_cost_from_json((payload.get("demand") or {}).get("cost") or {}),
            cache_reuse_ratio=Decimal(str(payload["cache_reuse_ratio"])) if payload.get("cache_reuse_ratio") is not None else None,
            gaps=tuple(payload.get("gaps") or ()),
        )


def _usage_from_json(payload: dict[str, object]) -> Usage:
    dimensions = []
    for item in payload.get("dimensions") or []:
        dimensions.append(UsageDimension(item.get("unit"), Decimal(str(item.get("value"))), Confidence(item.get("confidence", "unavailable")), item.get("source")))
    return Usage(tuple(dimensions))


def _cost_from_json(payload: dict[str, object]) -> Cost:
    scope = CostScope(payload["scope"]) if payload.get("scope") else None
    value = Decimal(str(payload["value"])) if payload.get("value") is not None else None
    coverage = Decimal(str(payload["coverage_percent"])) if payload.get("coverage_percent") is not None else None
    return Cost(value, payload.get("currency"), payload.get("source"), scope, Confidence(payload.get("confidence", "unavailable")), coverage)


class NoopUsageSummaryRepository:
    def save(self, key: SummaryKey, summary: UsageSummary) -> Path:
        return summary_path(key)

    def load(self, key: SummaryKey) -> UsageSummary | None:
        return None
