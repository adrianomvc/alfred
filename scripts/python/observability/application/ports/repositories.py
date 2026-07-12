from pathlib import Path
from typing import Protocol, Sequence

from observability.domain.models import CanonicalEvent, SummaryKey, UsageSummary


class EventRepository(Protocol):
    def append(self, events: Sequence[CanonicalEvent]) -> None: ...
    def read_all(self) -> list[CanonicalEvent]: ...


class UsageSummaryRepository(Protocol):
    def save(self, key: SummaryKey, summary: UsageSummary) -> Path: ...
    def load(self, key: SummaryKey) -> UsageSummary | None: ...

