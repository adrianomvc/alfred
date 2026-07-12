from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Mapping, Optional, Sequence

from .enums import Confidence, CostScope, UsageUnit


@dataclass(frozen=True)
class ObservedTotal:
    value: Decimal = Decimal("0")
    observed_count: int = 0

    @property
    def is_observed(self) -> bool:
        return self.observed_count > 0

    def add(self, value: Decimal | int | float | str | None) -> "ObservedTotal":
        if value is None:
            return self
        return ObservedTotal(self.value + Decimal(str(value)), self.observed_count + 1)


@dataclass(frozen=True)
class UsageDimension:
    unit: UsageUnit | str
    value: Decimal
    confidence: Confidence = Confidence.UNAVAILABLE
    source: str | None = None


@dataclass(frozen=True)
class Usage:
    dimensions: tuple[UsageDimension, ...] = ()

    def total_for(self, unit: UsageUnit | str) -> ObservedTotal:
        total = ObservedTotal()
        for item in self.dimensions:
            if item.unit == unit:
                total = total.add(item.value)
        return total


@dataclass(frozen=True)
class Cost:
    value: Decimal | None = None
    currency: str | None = None
    source: str | None = None
    scope: CostScope | None = None
    confidence: Confidence = Confidence.UNAVAILABLE
    coverage_percent: Decimal | None = None
    observed_at: datetime | None = None

    @property
    def is_available(self) -> bool:
        return self.value is not None


@dataclass(frozen=True)
class CostCandidate:
    cost: Cost
    priority: int
    reason: str


@dataclass(frozen=True)
class ArtifactUsage:
    path: str | None
    path_hash: str | None = None
    artifact_type: str = "unknown"
    operation: str = "read"
    selection_reason: str | None = None
    observed_by: str | None = None
    confidence: Confidence = Confidence.UNAVAILABLE
    size_bytes: int | None = None
    lines_read: int | None = None
    content_hash: str | None = None


@dataclass(frozen=True)
class AdapterCapabilities:
    request_tokens: bool = False
    session_usage: bool = False
    cost: bool = False
    artifacts: bool = False
    tools: bool = False


@dataclass(frozen=True)
class CapabilityGap:
    capability: str
    status: str
    reason: str


@dataclass(frozen=True)
class CanonicalEvent:
    schema_version: str
    event_id: str
    event_type: str
    event_scope: str | None
    timestamp: datetime | None
    provider: str | None = None
    host: str | None = None
    adapter: str | None = None
    source_kind: str | None = None
    session_id: str | None = None
    interaction_id: str | None = None
    request_id: str | None = None
    alfred_run_id: str | None = None
    initiative_id: str | None = None
    demand_id: str | None = None
    phase: str | None = None
    lane: str | None = None
    model: str | None = None
    usage: Usage = field(default_factory=Usage)
    cost: Cost = field(default_factory=Cost)
    artifacts_used: tuple[ArtifactUsage, ...] = ()
    raw: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class UsageSummary:
    schema_version: str
    provider: str | None
    host: str | None
    adapter: str | None
    updated_at: datetime
    session_usage: Usage
    session_cost: Cost
    demand_usage: Usage
    demand_cost: Cost
    cache_reuse_ratio: Decimal | None
    gaps: tuple[str, ...] = ()


@dataclass(frozen=True)
class SummaryKey:
    state_path: str


@dataclass(frozen=True)
class AdapterContext:
    host: str
    provider: str | None = None
    run_id: str | None = None
    state_path: str | None = None
