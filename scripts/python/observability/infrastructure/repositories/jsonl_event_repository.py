import json
from datetime import datetime
from pathlib import Path
from typing import Mapping, Sequence

from observability.domain.models import CanonicalEvent
from observability.domain.services.usage_calculator import usage_from_legacy_event
from observability.domain.services.cost_calculator import cost_from_value
from observability.domain.enums import Confidence, CostScope


def parse_ts(value: object) -> datetime | None:
    if not value:
        return None
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def canonical_from_mapping(event: Mapping[str, object]) -> CanonicalEvent:
    cost_scope = CostScope.DEMAND if event.get("event_type") == "usage_cost_attributed" else None
    cost = cost_from_value(
        event.get("cost_usd"),
        source=str((event.get("metadata") or {}).get("source_kind") or event.get("cost_source") or "") or None
        if isinstance(event.get("metadata"), Mapping) else str(event.get("cost_source") or "") or None,
        scope=cost_scope or CostScope.REQUEST,
        confidence=Confidence(str(event.get("cost_confidence") or (event.get("output") or {}).get("cost_confidence") or "unavailable"))
        if str(event.get("cost_confidence") or (event.get("output") or {}).get("cost_confidence") or "unavailable") in {item.value for item in Confidence}
        else Confidence.UNAVAILABLE,
    )
    return CanonicalEvent(
        schema_version=str(event.get("schema_version") or "alfred.observability.v1"),
        event_id=str(event.get("event_id") or ""),
        event_type=str(event.get("event_type") or ""),
        event_scope=event.get("event_scope") if isinstance(event.get("event_scope"), str) else None,
        timestamp=parse_ts(event.get("ts")),
        provider=event.get("provider") if isinstance(event.get("provider"), str) else None,
        host=event.get("host") if isinstance(event.get("host"), str) else None,
        adapter=event.get("adapter") if isinstance(event.get("adapter"), str) else None,
        source_kind=(event.get("metadata") or {}).get("source_kind") if isinstance(event.get("metadata"), Mapping) else None,
        session_id=event.get("session_id") if isinstance(event.get("session_id"), str) else None,
        interaction_id=event.get("interaction_id") if isinstance(event.get("interaction_id"), str) else None,
        request_id=event.get("request_id") if isinstance(event.get("request_id"), str) else None,
        alfred_run_id=event.get("alfred_run_id") if isinstance(event.get("alfred_run_id"), str) else None,
        initiative_id=event.get("initiative_id") if isinstance(event.get("initiative_id"), str) else None,
        demand_id=event.get("demand_id") if isinstance(event.get("demand_id"), str) else None,
        phase=event.get("phase") if isinstance(event.get("phase"), str) else None,
        lane=event.get("lane") if isinstance(event.get("lane"), str) else None,
        model=event.get("model") if isinstance(event.get("model"), str) else None,
        usage=usage_from_legacy_event(event),
        cost=cost,
        raw=event,
    )


class JsonlEventRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def append(self, events: Sequence[CanonicalEvent]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event.raw, separators=(",", ":")) + "\n")

    def read_all(self) -> list[CanonicalEvent]:
        if not self._path.exists():
            return []
        output = []
        for raw in self._path.read_text(encoding="utf-8-sig").splitlines():
            if raw.strip():
                output.append(canonical_from_mapping(json.loads(raw)))
        return output

