from decimal import Decimal
from typing import Sequence

from ..enums import Confidence, CostScope
from ..models import Cost, CostCandidate


class CostResolver:
    """Select one cost source by precedence; never sums alternative sources."""

    def resolve_session_cost(self, candidates: Sequence[CostCandidate]) -> Cost:
        return self._resolve(candidates, CostScope.SESSION)

    def resolve_demand_cost(self, candidates: Sequence[CostCandidate]) -> Cost:
        return self._resolve(candidates, CostScope.DEMAND)

    def _resolve(self, candidates: Sequence[CostCandidate], scope: CostScope) -> Cost:
        applicable = [item for item in candidates if item.cost.scope == scope and item.cost.value is not None]
        if not applicable:
            return Cost(scope=scope, confidence=Confidence.UNAVAILABLE)
        return sorted(applicable, key=lambda item: item.priority)[0].cost


def cost_from_value(value: object, *, source: str | None, scope: CostScope,
                    confidence: Confidence, currency: str = "USD",
                    coverage_percent: Decimal | None = None) -> Cost:
    if value is None or str(value).strip() == "":
        return Cost(source=source, scope=scope, confidence=Confidence.UNAVAILABLE)
    try:
        amount = Decimal(str(value))
    except Exception:
        return Cost(source=source, scope=scope, confidence=Confidence.UNAVAILABLE)
    return Cost(amount, currency, source, scope, confidence, coverage_percent)

