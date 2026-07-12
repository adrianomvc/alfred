from dataclasses import dataclass
from decimal import Decimal

from observability.domain.enums import CostScope, UsageUnit
from observability.domain.models import Cost, Usage, UsageSummary
from observability.domain.services.forecast import CostForecastService
from observability.domain.services.usage_calculator import total_tokens


@dataclass(frozen=True)
class ToolbarViewModel:
    demand_id: str
    sigla: str
    lane: str
    progress: int
    framework: str
    app_commit: str
    primary_usage_text: str
    session_cost_text: str | None
    demand_cost_text: str | None
    cost_gap_text: str | None
    forecast_text: str | None


def format_decimal(value: Decimal, places: int = 2) -> str:
    return f"{value:.{places}f}".replace(".", ",")


def format_cost(cost: Cost) -> str | None:
    if cost.value is None:
        return None
    currency = cost.currency or "USD"
    scope = cost.scope.value if cost.scope else "unknown"
    source = cost.source or "fonte desconhecida"
    confidence = cost.confidence.value
    return f"{currency} {format_decimal(cost.value)} · {scope} · {source} · {confidence}"


def format_usage(usage: Usage, cache_ratio: Decimal | None) -> str:
    tokens = total_tokens(usage)
    acu = usage.total_for(UsageUnit.ACU)
    credit = usage.total_for(UsageUnit.CREDIT)
    if acu.is_observed:
        return f"{format_decimal(acu.value)} ACU"
    if credit.is_observed:
        return f"{format_decimal(credit.value)} créditos"
    if tokens.is_observed:
        cache = "cache n/a" if cache_ratio is None else f"cache {format_decimal(cache_ratio * Decimal('100'), 0)}%"
        return f"{format_decimal(tokens.value / Decimal('1000'), 1)} mil tokens · {cache}"
    return "não coletado · adapter de uso não configurado"


class ToolbarViewModelBuilder:
    def __init__(self, forecast_service: CostForecastService | None = None) -> None:
        self._forecast = forecast_service or CostForecastService()

    def build(self, *, demand_id: str, sigla: str, lane: str, progress: int,
              framework: str, app_commit: str, summary: UsageSummary | None) -> ToolbarViewModel:
        if summary is None:
            return ToolbarViewModel(demand_id, sigla, lane, progress, framework, app_commit, "não coletado · adapter de uso não configurado", None, None, "fonte de custo não configurada", None)
        forecast = self._forecast.forecast(summary.demand_cost, progress, Decimal("80"))
        return ToolbarViewModel(
            demand_id=demand_id,
            sigla=sigla,
            lane=lane,
            progress=progress,
            framework=framework,
            app_commit=app_commit,
            primary_usage_text=format_usage(summary.demand_usage, summary.cache_reuse_ratio),
            session_cost_text=format_cost(summary.session_cost),
            demand_cost_text=format_cost(summary.demand_cost),
            cost_gap_text=_cost_gap(summary.gaps),
            forecast_text=None if forecast.value is None else f"~USD {format_decimal(forecast.value)}",
        )


def _cost_gap(gaps: tuple[str, ...]) -> str | None:
    if not gaps:
        return None
    if "demand cost unavailable" in gaps and "session cost unavailable" in gaps:
        return "fonte de custo não configurada"
    if "demand cost unavailable" in gaps:
        return "custo da demanda indisponível"
    return "; ".join(gaps)
