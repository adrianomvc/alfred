"""Event deduplication over legacy event dicts (infrastructure).

Moved from ``metrics/observability.py``. Lives in infrastructure because the
canonical semantic key is serialized with ``json`` for unkeyed events; the
domain layer stays free of json/os.
"""

import json

from shared.observability.domain.services.legacy_usage import semantic_event_key


def effective_events(events):
    """Deduplicate by event_id and semantic key, keeping the latest occurrence."""
    keyed = {}
    unkeyed = []
    for index, event in enumerate(events):
        event_id = event.get("event_id")
        semantic = semantic_event_key(event)
        key = ("event_id", event_id) if event_id else ("semantic", json.dumps(semantic, sort_keys=True, default=str))
        keyed[key] = (index, event)
        if not event_id and key[0] != "semantic":
            unkeyed.append((index, event))
    merged = [*keyed.values(), *unkeyed]
    return [event for _, event in sorted(merged, key=lambda item: item[0])]
