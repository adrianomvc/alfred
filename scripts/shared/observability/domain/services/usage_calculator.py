from decimal import Decimal
from typing import Iterable, Mapping

from ..enums import Confidence, UsageUnit
from ..models import ObservedTotal, Usage, UsageDimension


TOKEN_KEYS = {
    "tokens_input": UsageUnit.TOKEN_INPUT,
    "tokens_output": UsageUnit.TOKEN_OUTPUT,
    "tokens_cache_creation": UsageUnit.TOKEN_CACHE_CREATION,
    "tokens_cache_read": UsageUnit.TOKEN_CACHE_READ,
}


def decimal_or_none(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def usage_from_legacy_event(event: Mapping[str, object]) -> Usage:
    output = event.get("output") if isinstance(event.get("output"), Mapping) else {}
    dimensions = []
    for key, unit in TOKEN_KEYS.items():
        value = output.get(key) if output.get(key) is not None else event.get(key)
        decimal = decimal_or_none(value)
        if decimal is not None:
            dimensions.append(UsageDimension(unit=unit, value=decimal, confidence=Confidence.EXACT, source="legacy_event"))
    for source_key, unit in (("total_acus", UsageUnit.ACU), ("credits", UsageUnit.CREDIT)):
        decimal = decimal_or_none(event.get(source_key))
        if decimal is not None:
            dimensions.append(UsageDimension(unit=unit, value=decimal, confidence=Confidence.EXACT, source="legacy_event"))
    return Usage(tuple(dimensions))


def sum_usage(usages: Iterable[Usage]) -> Usage:
    totals: dict[UsageUnit | str, ObservedTotal] = {}
    confidence: dict[UsageUnit | str, Confidence] = {}
    for usage in usages:
        for dimension in usage.dimensions:
            current = totals.get(dimension.unit, ObservedTotal())
            totals[dimension.unit] = current.add(dimension.value)
            confidence.setdefault(dimension.unit, dimension.confidence)
    return Usage(tuple(
        UsageDimension(unit=unit, value=total.value, confidence=confidence[unit], source="rollup")
        for unit, total in totals.items()
        if total.is_observed
    ))


def total_tokens(usage: Usage) -> ObservedTotal:
    total = ObservedTotal()
    for unit in (UsageUnit.TOKEN_INPUT, UsageUnit.TOKEN_OUTPUT, UsageUnit.TOKEN_CACHE_CREATION, UsageUnit.TOKEN_CACHE_READ):
        subtotal = usage.total_for(unit)
        if subtotal.is_observed:
            total = total.add(subtotal.value)
    return total


def cache_reuse_ratio(usage: Usage) -> Decimal | None:
    input_tokens = usage.total_for(UsageUnit.TOKEN_INPUT)
    cache_creation = usage.total_for(UsageUnit.TOKEN_CACHE_CREATION)
    cache_read = usage.total_for(UsageUnit.TOKEN_CACHE_READ)
    denominator = input_tokens.value + cache_creation.value + cache_read.value
    observed = input_tokens.is_observed or cache_creation.is_observed or cache_read.is_observed
    if not observed or denominator == 0:
        return None
    return cache_read.value / denominator

