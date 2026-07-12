from decimal import Decimal
from typing import Mapping

from observability.application.ports.clock import Clock
from observability.application.ports.repositories import EventRepository, UsageSummaryRepository
from observability.domain.enums import Confidence, CostScope
from observability.domain.models import CostCandidate, SummaryKey, UsageSummary
from observability.domain.services.cost_calculator import CostResolver, cost_from_value
from observability.domain.services.usage_calculator import cache_reuse_ratio, sum_usage


SESSION_COST_PRIORITY = {
    "official_billing": 1,
    "devin_api": 1,
    "host_cost_command": 2,
    "ccusage": 3,
    "usage_rate_card": 4,
    "manual_allocation": 5,
}


def confidence_from_text(value: object) -> Confidence:
    text = str(value or "unavailable").strip().lower()
    return Confidence(text) if text in {item.value for item in Confidence} else Confidence.UNAVAILABLE


class ReconcileUsageSummary:
    def __init__(
        self,
        event_repository: EventRepository,
        summary_repository: UsageSummaryRepository,
        cost_resolver: CostResolver,
        clock: Clock,
    ) -> None:
        self._events = event_repository
        self._summaries = summary_repository
        self._cost_resolver = cost_resolver
        self._clock = clock

    def execute(self, key: SummaryKey, state_fields: Mapping[str, str]) -> UsageSummary:
        events = self._events.read_all()
        usage_events = [item for item in events if item.event_type == "usage_attributed"]
        cost_events = [item for item in events if item.event_type == "usage_cost_attributed" and item.cost.value is not None]
        demand_usage = sum_usage(item.usage for item in usage_events)
        demand_cost = self._cost_resolver.resolve_demand_cost([
            CostCandidate(item.cost, 2, "usage_cost_attributed") for item in cost_events
        ])
        session_cost = self._cost_resolver.resolve_session_cost(self._session_candidates(state_fields))
        summary = UsageSummary(
            schema_version="alfred.usage-summary.v1",
            provider=state_fields.get("provider"),
            host=state_fields.get("host"),
            adapter=state_fields.get("adapter") or state_fields.get("cost source"),
            updated_at=self._clock.now(),
            session_usage=sum_usage(()),
            session_cost=session_cost,
            demand_usage=demand_usage,
            demand_cost=demand_cost,
            cache_reuse_ratio=cache_reuse_ratio(demand_usage),
            gaps=tuple(self._gaps(demand_usage, demand_cost, session_cost)),
        )
        self._summaries.save(key, summary)
        return summary

    def _session_candidates(self, state_fields: Mapping[str, str]) -> list[CostCandidate]:
        source = str(state_fields.get("cost source") or state_fields.get("usage-cost") or "").strip()
        granularity = str(state_fields.get("cost granularity") or "").strip().lower()
        if granularity == "demand":
            return []
        scope = CostScope.SESSION
        confidence = confidence_from_text(state_fields.get("cost confidence"))
        cost = cost_from_value(
            state_fields.get("cost usd"),
            source=source or None,
            scope=scope,
            confidence=confidence,
            coverage_percent=Decimal("100") if state_fields.get("cost usd") else None,
        )
        priority = SESSION_COST_PRIORITY.get(source, 99)
        return [CostCandidate(cost, priority, "state_cost_field")]

    def _gaps(self, usage, demand_cost, session_cost):
        if not usage.dimensions:
            yield "usage not collected"
        if demand_cost.value is None:
            yield "demand cost unavailable"
        if session_cost.value is None:
            yield "session cost unavailable"
