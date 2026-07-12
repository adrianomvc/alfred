from typing import Callable, Mapping, Protocol, Sequence

from observability.domain.models import AdapterCapabilities, AdapterContext, CanonicalEvent


class HookEventAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def normalize_hook_event(self, payload: Mapping[str, object], context: AdapterContext) -> list[CanonicalEvent]: ...


class TranscriptUsageAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def read_transcript(self, source: object, context: AdapterContext) -> list[CanonicalEvent]: ...


class SessionUsageAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def read_session_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]: ...


class ObservabilityAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def normalize_event(self, payload: Mapping[str, object], context: AdapterContext) -> list[CanonicalEvent]: ...
    def read_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]: ...


class AdapterRegistry:
    def __init__(self) -> None:
        self._factories: dict[tuple[str, str], Callable[[], ObservabilityAdapter]] = {}

    def register(self, host: str, source_kind: str, factory: Callable[[], ObservabilityAdapter]) -> None:
        self._factories[(host, source_kind)] = factory

    def resolve(self, host: str, source_kind: str) -> ObservabilityAdapter:
        key = (host, source_kind)
        if key not in self._factories:
            raise KeyError(f"No observability adapter registered for {host}/{source_kind}")
        return self._factories[key]()

