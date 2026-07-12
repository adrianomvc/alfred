from dataclasses import dataclass
from decimal import Decimal

from ..enums import CostScope
from ..models import Cost


@dataclass(frozen=True)
class CostForecast:
    value: Decimal | None
    reason: str | None = None


class CostForecastService:
    def forecast(self, demand_cost: Cost, progress_percent: int,
                 minimum_coverage_percent: Decimal = Decimal("80")) -> CostForecast:
        if demand_cost.scope != CostScope.DEMAND or demand_cost.value is None:
            return CostForecast(None, "demand cost unavailable")
        if progress_percent <= 0 or progress_percent >= 100:
            return CostForecast(None, "progress outside forecast range")
        coverage = demand_cost.coverage_percent
        if coverage is not None and coverage < minimum_coverage_percent:
            return CostForecast(None, "coverage below threshold")
        return CostForecast(demand_cost.value * Decimal("100") / Decimal(progress_percent))

