from typing import Mapping

from shared.observability.domain.models import AdapterCapabilities, AdapterContext, CanonicalEvent
from shared.observability.infrastructure.adapters.generic.jsonl import GenericJsonlAdapter


class DevinInsightsAdapter:
    def __init__(self, mapper: GenericJsonlAdapter | None = None) -> None:
        self._mapper = mapper or GenericJsonlAdapter()

    def capabilities(self) -> AdapterCapabilities:
        # request_tokens is True since the local session transcript exposes exact
        # per-step tokens (see adapters/devin/transcript.py). cost stays False:
        # Devin publishes ACU only through the web UI and never per request.
        return AdapterCapabilities(request_tokens=True, session_usage=True, cost=False, artifacts=True, tools=False)

    def normalize_event(self, payload: Mapping[str, object], context: AdapterContext) -> list[CanonicalEvent]:
        return self._mapper.normalize_event(payload, context)

    def read_usage(self, source: object, context: AdapterContext) -> list[CanonicalEvent]:
        return self._mapper.read_usage(source, context)

