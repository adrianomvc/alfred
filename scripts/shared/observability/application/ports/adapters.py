from typing import Callable, Mapping, Protocol, runtime_checkable

from shared.observability.domain.models import AdapterCapabilities, AdapterContext, CanonicalEvent


@runtime_checkable
class HookEventAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def normalize_hook_event(self, payload: Mapping[str, object], context: AdapterContext) -> list[CanonicalEvent]: ...


@runtime_checkable
class TranscriptUsageAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def read_transcript(self, source: object, context: AdapterContext) -> list[CanonicalEvent]: ...


@runtime_checkable
class SessionUsageAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def read_session_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]: ...


@runtime_checkable
class ObservabilityAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def normalize_event(self, payload: Mapping[str, object], context: AdapterContext) -> list[CanonicalEvent]: ...
    def read_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]: ...


class AdapterRegistry:
    def __init__(self) -> None:
        self._factories: dict[tuple[str, str], Callable[[], object]] = {}
        self._experimental: set[tuple[str, str]] = set()

    def register(self, host: str, source_kind: str, factory: Callable[[], object], *, experimental: bool = False) -> None:
        key = (host, source_kind)
        self._factories[key] = factory
        if experimental:
            self._experimental.add(key)

    def resolve(self, host: str, source_kind: str) -> object:
        key = (host, source_kind)
        if key not in self._factories:
            raise KeyError(f"No observability adapter registered for {host}/{source_kind}")
        return self._factories[key]()

    def registered(self, *, include_experimental: bool = False) -> tuple[tuple[str, str], ...]:
        keys = self._factories.keys() if include_experimental else (key for key in self._factories if key not in self._experimental)
        return tuple(sorted(keys))

    def is_experimental(self, host: str, source_kind: str) -> bool:
        return (host, source_kind) in self._experimental
