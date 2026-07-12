from typing import Mapping

from observability.domain.models import AdapterCapabilities, AdapterContext, CanonicalEvent
from observability.infrastructure.repositories.jsonl_event_repository import canonical_from_mapping


class GenericJsonlAdapter:
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(request_tokens=True, session_usage=True, cost=True, artifacts=True, tools=False)

    def normalize_event(self, payload: Mapping[str, object], context: AdapterContext) -> list[CanonicalEvent]:
        return [canonical_from_mapping(payload)]

    def read_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]:
        if isinstance(source, Mapping):
            return self.normalize_event(source, context)
        return []

