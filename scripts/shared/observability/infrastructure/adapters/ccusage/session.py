"""ccusage session-total parsing (host format -> selected session row).

Owns the ccusage JSON shape knowledge that used to live in
``import-ccusage.py``: row extraction across payload variants, agent/session
selection, and model-name flattening. Subprocess/file acquisition and Alfred
snapshot assembly stay in the command driver. ccusage reports a *session* total,
never an interaction event -- capabilities reflect that.
"""

from decimal import Decimal
from typing import Mapping

from shared.observability.domain.enums import Confidence, CostScope, UsageUnit
from shared.observability.domain.models import (
    AdapterCapabilities,
    AdapterContext,
    CanonicalEvent,
    Cost,
    Usage,
    UsageDimension,
)


class NoSessionMatch(Exception):
    """Raised when no ccusage row matches the requested filters."""


def session_rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ["session", "sessions", "rows", "data"]:
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def last_activity(row):
    metadata = row.get("metadata") or {}
    return metadata.get("lastActivity") or ""


def models(row):
    used = row.get("modelsUsed")
    if isinstance(used, list) and used:
        return ",".join(str(item) for item in used)
    breakdowns = row.get("modelBreakdowns")
    if isinstance(breakdowns, list):
        names = [item.get("modelName") for item in breakdowns if item.get("modelName")]
        if names:
            return ",".join(names)
    return None


class CcusageSessionAdapter:
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(request_tokens=False, session_usage=True, cost=True, artifacts=False, tools=False)

    def select_session(self, payload, agent, session_id):
        """Return (row, selection_method). Raises NoSessionMatch on no match."""
        candidates = []
        for row in session_rows(payload):
            if agent and row.get("agent") != agent:
                continue
            if session_id and row.get("period") != session_id:
                continue
            candidates.append(row)
        if not candidates:
            raise NoSessionMatch("No ccusage session matched the requested filters.")
        if session_id:
            return candidates[0], "session_id"
        candidates.sort(key=last_activity, reverse=True)
        return candidates[0], "latest_agent_session"

    def read_session_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]:
        """Protocol conformance: the selected session row as one canonical event."""
        if not isinstance(source, Mapping):
            return []
        row, _method = self.select_session(source, None, None)
        return [self._to_canonical(row, context)]

    def _to_canonical(self, row: Mapping[str, object], context: AdapterContext) -> CanonicalEvent:
        dimensions = []
        for key, unit in (
            ("inputTokens", UsageUnit.TOKEN_INPUT),
            ("outputTokens", UsageUnit.TOKEN_OUTPUT),
            ("cacheCreationTokens", UsageUnit.TOKEN_CACHE_CREATION),
            ("cacheReadTokens", UsageUnit.TOKEN_CACHE_READ),
        ):
            value = row.get(key)
            if value is not None:
                dimensions.append(UsageDimension(unit=unit, value=Decimal(str(value)), confidence=Confidence.ESTIMATED, source="ccusage"))
        total_cost = row.get("totalCost")
        cost = Cost(
            Decimal(str(total_cost)) if total_cost is not None else None,
            "USD",
            "ccusage",
            CostScope.SESSION,
            Confidence.ESTIMATED if total_cost is not None else Confidence.UNAVAILABLE,
        )
        return CanonicalEvent(
            schema_version="alfred.usage-session.v1",
            event_id=f"usage-ccusage-{row.get('period', 'session')}",
            event_type="session_usage_snapshot",
            event_scope="session",
            timestamp=None,
            host=context.host,
            source_kind="ccusage",
            session_id=str(row.get("period")) if row.get("period") is not None else None,
            model=models(row),
            usage=Usage(tuple(dimensions)),
            cost=cost,
            raw=dict(row),
        )
