"""Token/cost readers over legacy ``alfred.observability.v1`` event dicts.

Pure helpers moved from ``metrics/observability.py``. They read loosely-typed
event dicts (not the CanonicalEvent model) and keep exact backward compatibility
with the rollup/insights commands.
"""


def token_value(event, key):
    output = event.get("output") or {}
    value = output.get(key)
    if value is None:
        value = event.get(key)
    return value if value is not None else None


def token_int(event, key):
    value = token_value(event, key)
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def usage_tokens(event):
    tokens = {
        "tokens_input": token_int(event, "tokens_input"),
        "tokens_output": token_int(event, "tokens_output"),
        "tokens_cache_creation": token_int(event, "tokens_cache_creation"),
        "tokens_cache_read": token_int(event, "tokens_cache_read"),
    }
    tokens["total_tokens"] = sum(tokens.values())
    denominator = tokens["tokens_input"] + tokens["tokens_cache_creation"] + tokens["tokens_cache_read"]
    tokens["cache_reuse_ratio"] = None if denominator == 0 else tokens["tokens_cache_read"] / denominator
    return tokens


def semantic_event_key(event):
    event_type = event.get("event_type")
    if event_type == "usage_attributed":
        return (
            event_type,
            event.get("session_id"),
            event.get("request_id") or tuple((event.get("input") or {}).get("request_ids") or []),
        )
    if event_type == "usage_cost_attributed":
        metadata = event.get("metadata") or {}
        return (event_type, event.get("parent_event_id"), metadata.get("rate_card_hash"))
    return (event_type, event.get("event_id"))


def cost_value(event):
    value = (event.get("output") or {}).get("cost_usd")
    if value is None:
        value = event.get("cost_usd")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
