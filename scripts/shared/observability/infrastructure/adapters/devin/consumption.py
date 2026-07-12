from typing import Mapping

from shared.observability.domain.models import AdapterCapabilities, AdapterContext, CanonicalEvent
from shared.observability.infrastructure.adapters.generic.jsonl import GenericJsonlAdapter


class DevinConsumptionAdapter:
    def __init__(self, mapper: GenericJsonlAdapter | None = None) -> None:
        self._mapper = mapper or GenericJsonlAdapter()

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(request_tokens=False, session_usage=True, cost=True, artifacts=False, tools=False)

    def normalize_event(self, payload: Mapping[str, object], context: AdapterContext) -> list[CanonicalEvent]:
        return self._mapper.normalize_event(payload, context)

    def read_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]:
        return self._mapper.read_usage(source, context)

