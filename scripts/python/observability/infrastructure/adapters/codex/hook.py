from typing import Mapping

from observability.domain.models import AdapterCapabilities, AdapterContext, CanonicalEvent
from observability.infrastructure.adapters.generic.jsonl import GenericJsonlAdapter


class CodexHookAdapter:
    def __init__(self, mapper: GenericJsonlAdapter | None = None) -> None:
        self._mapper = mapper or GenericJsonlAdapter()

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(request_tokens=True, session_usage=False, cost=False, artifacts=True, tools=True)

    def normalize_event(self, payload: Mapping[str, object], context: AdapterContext) -> list[CanonicalEvent]:
        return self._mapper.normalize_event(payload, context)

    def read_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]:
        return self._mapper.read_usage(source, context)

