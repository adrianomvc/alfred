#!/usr/bin/env python3
"""Attribute host transcript usage to Alfred observability windows or turns.

Layers 1-2 of the usage-cost design. A Claude Code transcript records exact
token usage per API request (``requestId``); a single request spans several
JSONL lines that repeat the same ``usage`` object, so usage MUST be de-duplicated
by ``requestId`` before summing. This helper reads a transcript, de-dupes by
request, and emits append-only ``usage_attributed`` events:

- ``--granularity window`` (Layer 1): sum the requests whose timestamp falls in
  each window bounded by consecutive Alfred event timestamps, and attribute that
  bucket to the anchoring event. Depends on real, distinct event ``ts`` (Layer 0).
- ``--granularity turn`` (Layer 2): emit one event per request, tagged with the
  Alfred event whose window encloses it, carrying the exact ``requestId``/``uuid``.

Tokens are exact (from the transcript). Cost is NOT in the transcript: it stays
``null`` (``cost_confidence: unavailable``) unless an approved interaction
rate card is supplied with ``--rate-card-path``. A ccusage session total belongs
in ``001-state.md`` for toolbar display, not in interaction JSONL events.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_state_fields, value_or  # noqa: E402


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_ts(raw):
    if not raw:
        return None
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_transcript_requests(path):
    """Return requests de-duplicated by ``requestId``, sorted by start time.

    Each request keeps the earliest timestamp seen (start) and the final line's
    usage (complete). Only ``assistant`` lines carry usage.
    """
    requests = {}
    for raw in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "assistant":
            continue
        request_id = record.get("requestId") or record.get("uuid")
        message = record.get("message") or {}
        usage = message.get("usage") or {}
        ts = parse_ts(record.get("timestamp"))
        tokens = {
            "tokens_input": usage.get("input_tokens") or 0,
            "tokens_output": usage.get("output_tokens") or 0,
            "tokens_cache_creation": usage.get("cache_creation_input_tokens") or 0,
            "tokens_cache_read": usage.get("cache_read_input_tokens") or 0,
        }
        existing = requests.get(request_id)
        if existing is None:
            requests[request_id] = {
                "request_id": request_id,
                "uuid": record.get("uuid"),
                "ts": ts,
                "model": message.get("model"),
                **tokens,
            }
        else:
            if ts and (existing["ts"] is None or ts < existing["ts"]):
                existing["ts"] = ts
            # Final line of a request holds the complete usage.
            existing.update(tokens)
            existing["model"] = message.get("model") or existing["model"]
    ordered = [r for r in requests.values() if r["ts"] is not None]
    ordered.sort(key=lambda r: r["ts"])
    return ordered


def already_attributed_request_ids(path):
    """Collect request ids already emitted as transcript ``usage_attributed``.

    Lets the Stop hook re-run every turn without duplicating: a request keeps its
    stable ``usage-turn-<requestId>`` id, so previously attributed turns are
    skipped instead of appended twice.
    """
    seen = set()
    if not path or not Path(path).exists():
        return seen
    for raw in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("event_type") != "usage_attributed":
            continue
        for request_id in (event.get("input") or {}).get("request_ids") or []:
            seen.add(request_id)
    return seen


def load_events(path):
    """Return real Alfred work events (not prior attribution) with parsed ts."""
    events = []
    if not path or not Path(path).exists():
        return events
    for raw in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("event_type") == "usage_attributed":
            continue
        ts = parse_ts(event.get("ts"))
        if ts is None:
            continue
        events.append(
            {
                "ts": ts,
                "event_id": event.get("event_id"),
                "phase": event.get("phase"),
                "lane": event.get("lane"),
                "step": event.get("step"),
            }
        )
    events.sort(key=lambda e: e["ts"])
    return events


def total_tokens(bucket):
    return (
        bucket["tokens_input"]
        + bucket["tokens_output"]
        + bucket["tokens_cache_creation"]
        + bucket["tokens_cache_read"]
    )


def empty_tokens():
    return {
        "tokens_input": 0,
        "tokens_output": 0,
        "tokens_cache_creation": 0,
        "tokens_cache_read": 0,
    }


def load_rate_card(path):
    if not path:
        return None
    rate_card_path = Path(path).resolve()
    payload = json.loads(rate_card_path.read_text(encoding="utf-8-sig"))
    if payload.get("schema_version") != "alfred.usage-rate-card.v1":
        raise SystemExit("Unsupported rate card schema_version.")
    if not payload.get("models"):
        raise SystemExit("Rate card has no models.")
    payload["_path"] = str(rate_card_path)
    payload["_hash"] = hashlib.sha256(rate_card_path.read_bytes()).hexdigest()
    return payload


def rate_for_model(model, rate_card):
    if not rate_card:
        return None
    return (rate_card.get("models") or {}).get(model)


def calculate_cost(bucket, rates):
    total = (
        bucket["tokens_input"] * float(rates.get("input_per_1m") or 0)
        + bucket["tokens_output"] * float(rates.get("output_per_1m") or 0)
        + bucket["tokens_cache_creation"] * float(rates.get("cache_creation_per_1m") or 0)
        + bucket["tokens_cache_read"] * float(rates.get("cache_read_per_1m") or 0)
    )
    return round(total / 1_000_000, 8)


def add_tokens(target, request):
    for key in empty_tokens():
        target[key] += request[key]


def assign_windows(requests, events):
    """Bucket requests into windows anchored by consecutive events.

    Window i spans [events[i].ts, events[i+1].ts); the first window extends to
    -inf and the last to +inf so every request is captured exactly once.
    """
    if not events:
        # No boundaries: one window over the whole transcript.
        bucket = {"anchor": None, "start": None, "end": None, "model": None, **empty_tokens(), "request_ids": []}
        for request in requests:
            add_tokens(bucket, request)
            bucket["request_ids"].append(request["request_id"])
            bucket["model"] = request["model"] if bucket["model"] in (None, request["model"]) else "__mixed__"
        return [bucket] if requests else []

    buckets = []
    for index, event in enumerate(events):
        lower = None if index == 0 else event["ts"]
        upper = events[index + 1]["ts"] if index + 1 < len(events) else None
        buckets.append(
            {
                "anchor": event,
                "start": lower,
                "end": upper,
                "model": None,
                **empty_tokens(),
                "request_ids": [],
            }
        )

    for request in requests:
        ts = request["ts"]
        target = buckets[0]
        for bucket in buckets:
            lower = bucket["start"]
            upper = bucket["end"]
            if (lower is None or ts >= lower) and (upper is None or ts < upper):
                target = bucket
                break
        add_tokens(target, request)
        target["request_ids"].append(request["request_id"])
        target["model"] = request["model"] if target["model"] in (None, request["model"]) else "__mixed__"

    return [b for b in buckets if b["request_ids"]]


def enclosing_event(request_ts, events):
    """Last event with ts <= request_ts (else the first event)."""
    anchor = events[0] if events else None
    for event in events:
        if event["ts"] <= request_ts:
            anchor = event
        else:
            break
    return anchor


def make_event(bucket, args, state_fields, granularity, rate_card, sequence):
    anchor = bucket.get("anchor")
    tokens = total_tokens(bucket)

    cost = None
    confidence = "unavailable"
    cost_source = None
    model = bucket.get("model")
    rates = rate_for_model(model, rate_card)
    if rate_card and not rates:
        raise SystemExit(f"Rate card has no rates for model: {model or 'unknown'}")
    if rates:
        cost = calculate_cost(bucket, rates)
        confidence = value_or(rate_card.get("confidence"), "rated")
        cost_source = "usage_rate_card"

    method = f"{granularity}-attribution"
    if granularity == "turn":
        event_id = f"usage-turn-{bucket.get('request_ids', ['x'])[0]}"
        anchor_ref = anchor.get("event_id") if anchor else None
    else:
        anchor_id = anchor.get("event_id") if anchor else f"window-{sequence}"
        event_id = f"usage-window-{anchor_id}"
        anchor_ref = anchor.get("event_id") if anchor else None

    phase = value_or(
        args.phase,
        value_or((anchor or {}).get("phase"), value_or(state_fields.get("current phase"), "operation")),
    )
    lane = value_or((anchor or {}).get("lane"), value_or(state_fields.get("lane"), value_or(state_fields.get("modo"), "unknown")))

    return {
        "schema_version": "alfred.observability.v1",
        "alfred": {
            "version": value_or(state_fields.get("framework version"), "unknown"),
            "framework_ref": value_or(state_fields.get("framework ref"), "local"),
            "framework_commit": value_or(state_fields.get("framework commit"), None),
            "schema_version": "alfred.observability.v1",
        },
        "ts": _iso(bucket.get("start")) or now_iso(),
        "event_id": event_id,
        "trace_id": value_or(state_fields.get("alfred run id"), value_or(args.run_id, "unknown")),
        "session_id": value_or(args.session_id, value_or(state_fields.get("usage session id"), "unknown")),
        "interaction_id": value_or(bucket.get("uuid"), "unknown"),
        "sequence": sequence,
        "initiative_id": value_or(state_fields.get("initiative id"), "unknown"),
        "demand_id": value_or(state_fields.get("id"), "unknown"),
        "event_type": "usage_attributed",
        "phase": phase,
        "lane": lane,
        "actor_type": "system",
        "actor_id": "usage-cost-transcript",
        "action": "attribute_usage",
        "status": "recorded",
        "step": {
            "id": "usage-cost",
            "name": "Usage and cost attribution",
            "sequence": sequence,
            "goal": f"Attribute host transcript usage by {method}",
        },
        "artifacts_used": [
            {"path": str(args.transcript_path), "role": "source_usage_export", "action": "read"}
        ],
        "duration_ms": None,
        "tokens_input": bucket["tokens_input"],
        "tokens_output": bucket["tokens_output"],
        "cost_usd": cost,
        "retry_count": 0,
        "input": {
            "source": "host_transcript",
            "source_kind": "host_transcript",
            "granularity": granularity,
            "request_count": len(bucket.get("request_ids", [])),
            "request_ids": bucket.get("request_ids", []),
            "window_start": _iso(bucket.get("start")),
            "window_end": _iso(bucket.get("end")),
            "anchor_event_id": anchor_ref,
        },
        "derivation": {
            "rules_applied": ["connectors/usage-cost.md", "metrics/metrics.md"],
            "method": (
                f"{method}: tokens summed from transcript requests de-duplicated by requestId; "
                "cost is null unless --rate-card-path supplies an approved interaction rate card; "
                "ccusage/session totals are not allocated into interaction events"
            ),
            "attribution": "derived",
        },
        "output": {
            "model": model,
            "tokens_input": bucket["tokens_input"],
            "tokens_output": bucket["tokens_output"],
            "tokens_cache_creation": bucket["tokens_cache_creation"],
            "tokens_cache_read": bucket["tokens_cache_read"],
            "total_tokens": tokens,
            "cost_usd": cost,
            "currency": (rate_card or {}).get("currency"),
            "cost_confidence": confidence,
            "token_confidence": "exact",
        },
        "model": model,
        "tool": "scripts/python/metrics/attribute-usage-transcript.py",
        "parent_event_id": anchor_ref,
        "artifacts": [],
        "files_changed": [],
        "validation": {"source_record_parse": "ok", "dedup_by": "requestId"},
        "risk": None,
        "blocker": None,
        "error": None,
        "state_transition": None,
        "actions": [{"type": "attribute_usage", "status": "completed"}],
        "questions_open": [],
        "assumptions": [],
        "metric_impact": {"usage_attribution": "added"},
        "next": [],
        "metadata": {
            "connector_type": "usage-cost",
            "source_kind": "host_transcript",
            "granularity": granularity,
            "cost_source_kind": cost_source,
            "rate_card_source": (rate_card or {}).get("source"),
            "rate_card_effective_from": (rate_card or {}).get("effective_from"),
            "rate_card_approved_by": (rate_card or {}).get("approved_by"),
            "rate_card_hash": (rate_card or {}).get("_hash"),
        },
    }


def _iso(dt):
    if not isinstance(dt, datetime):
        return None
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_output_path(state_path):
    if not state_path:
        return None
    candidate = state_path.parent / "05-operation" / "011-observability-log.jsonl"
    return candidate if candidate.exists() else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript-path", "-TranscriptPath", dest="transcript_path", required=True)
    parser.add_argument("--state-path", "-StatePath", dest="state_path", default="")
    parser.add_argument("--events-path", "-EventsPath", dest="events_path", default="")
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    parser.add_argument("--granularity", "-Granularity", dest="granularity", choices=["window", "turn"], default="window")
    parser.add_argument("--allocate-cost", "-AllocateCost", dest="allocate_cost", action="store_true", default=False)
    parser.add_argument("--session-cost-usd", "-SessionCostUsd", dest="session_cost_usd", default="")
    parser.add_argument("--rate-card-path", "-RateCardPath", dest="rate_card_path", default="")
    parser.add_argument("--session-id", "-SessionId", dest="session_id", default="")
    parser.add_argument("--since", "-Since", dest="since", default="")
    parser.add_argument("--append", "-Append", dest="append", action="store_true", default=True)
    parser.add_argument("--no-append", "-NoAppend", dest="append", action="store_false")
    parser.add_argument("--run-id", "-RunId", dest="run_id", default=os.environ.get("ALFRED_RUN_ID", ""))
    parser.add_argument("--phase", "-Phase", dest="phase", default="")
    args = parser.parse_args()

    if args.allocate_cost or args.session_cost_usd:
        raise SystemExit(
            "--allocate-cost/--session-cost-usd are deprecated for interaction JSONL. "
            "Do not allocate ccusage/session totals into interactions; use --rate-card-path "
            "with exact transcript tokens or a host export that already has interaction cost."
        )

    state_path = Path(args.state_path).resolve() if args.state_path else None
    state_fields = read_state_fields(state_path) if state_path else {}
    rate_card = load_rate_card(args.rate_card_path)

    requests = load_transcript_requests(args.transcript_path)
    if not requests:
        raise SystemExit("No usage-bearing requests found in the transcript.")

    since = parse_ts(args.since) if args.since else None
    if since is not None:
        requests = [r for r in requests if r["ts"] >= since]

    output_path = Path(args.output_path).resolve() if args.output_path else default_output_path(state_path)

    # Idempotent incremental appends (Stop hook): skip requests already attributed.
    if args.granularity == "turn" and args.append and output_path:
        seen = already_attributed_request_ids(output_path)
        if seen:
            requests = [r for r in requests if r["request_id"] not in seen]

    if not requests:
        print("No new transcript requests to attribute.")
        return

    events_path = args.events_path or (str(default_output_path(state_path)) if state_path else "")
    events = load_events(events_path) if events_path else []

    if args.granularity == "window":
        buckets = assign_windows(requests, events)
    else:
        buckets = []
        for request in requests:
            anchor = enclosing_event(request["ts"], events)
            buckets.append(
                {
                    "anchor": anchor,
                    "start": request["ts"],
                    "end": request["ts"],
                    "uuid": request["uuid"],
                    "model": request["model"],
                    "request_ids": [request["request_id"]],
                    "tokens_input": request["tokens_input"],
                    "tokens_output": request["tokens_output"],
                    "tokens_cache_creation": request["tokens_cache_creation"],
                    "tokens_cache_read": request["tokens_cache_read"],
                }
            )

    lines = []
    for index, bucket in enumerate(buckets, start=1):
        event = make_event(bucket, args, state_fields, args.granularity, rate_card, index)
        lines.append(json.dumps(event, separators=(",", ":")))

    if output_path and args.append:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
        print(f"Appended {len(lines)} {args.granularity}-attribution events to {output_path}")
    else:
        for line in lines:
            print(line)


if __name__ == "__main__":
    main()
