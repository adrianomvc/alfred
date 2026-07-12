"""Pure rate-card pricing.

Unifies the two legacy ``calculate_cost`` copies (attribute-usage-transcript and
apply-usage-rate-card) into one domain service. Host/source loading of the rate
card file is infrastructure; the math here is pure and deterministic.

Numeric contract: preserve the legacy result exactly -- float arithmetic with
``round(total / 1_000_000, 8)`` -- so emitted ``cost_usd`` stays byte-identical.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping

from ..enums import Confidence, CostScope
from ..models import Cost


@dataclass(frozen=True)
class ModelRate:
    """Per-1M-token rates for a single model. Values are exact as declared."""

    input_per_1m: Decimal = Decimal("0")
    output_per_1m: Decimal = Decimal("0")
    cache_creation_per_1m: Decimal = Decimal("0")
    cache_read_per_1m: Decimal = Decimal("0")

    @classmethod
    def from_mapping(cls, rates: Mapping[str, object] | None) -> "ModelRate | None":
        if not rates:
            return None
        return cls(
            input_per_1m=_rate(rates.get("input_per_1m")),
            output_per_1m=_rate(rates.get("output_per_1m")),
            cache_creation_per_1m=_rate(rates.get("cache_creation_per_1m")),
            cache_read_per_1m=_rate(rates.get("cache_read_per_1m")),
        )


def _rate(value: object) -> Decimal:
    if value is None or str(value).strip() == "":
        return Decimal("0")
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def price_usage_usd(tokens: Mapping[str, object], rate: ModelRate) -> float:
    """Return the interaction cost in USD, matching the legacy algorithm.

    ``tokens`` uses the legacy keys (tokens_input/output/cache_creation/cache_read).
    Float math and 8-decimal rounding are intentional to preserve output bytes.
    """
    total = (
        _count(tokens.get("tokens_input")) * float(rate.input_per_1m)
        + _count(tokens.get("tokens_output")) * float(rate.output_per_1m)
        + _count(tokens.get("tokens_cache_creation")) * float(rate.cache_creation_per_1m)
        + _count(tokens.get("tokens_cache_read")) * float(rate.cache_read_per_1m)
    )
    return round(total / 1_000_000, 8)


def price_usage(tokens: Mapping[str, object], rate: ModelRate,
                *, source: str | None = None, scope: CostScope = CostScope.INTERACTION,
                currency: str = "USD", coverage_percent: Decimal | None = Decimal("100")) -> Cost:
    """Domain-typed pricing for reconcile/read-side consumers."""
    amount = price_usage_usd(tokens, rate)
    return Cost(Decimal(str(amount)), currency, source, scope, Confidence.RATED, coverage_percent)


def _count(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
