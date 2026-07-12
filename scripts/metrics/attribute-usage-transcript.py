#!/usr/bin/env python3
"""Attribute Claude Code transcript usage to Alfred request/interaction events.

Claude Code transcripts expose exact model usage on assistant records with a
stable ``requestId``. Human turns are user records with ``promptId`` when the
host can provide it. This helper keeps those concepts separate:

- ``request``: one real model API request.
- ``interaction``: one human prompt plus the requests/tools that follow it.
- ``session``: the host session.

The legacy ``--granularity turn`` flag is still accepted as an alias for
``request`` for compatibility. Cost remains ``null`` unless an approved rate
card is supplied; ccusage session totals are never allocated into requests.
In policy terms, ccusage/session totals are not allocated across interactions.
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import read_state_fields, value_or  # noqa: E402
from metrics.observability import canonical_artifact, now_iso, usage_tokens  # noqa: E402
from shared.observability.domain.services.rate_card import ModelRate, price_usage_usd  # noqa: E402
from shared.observability.infrastructure.adapters.claude.transcript import (  # noqa: E402
    ClaudeTranscriptAdapter,
    iso,
    parse_ts,
)
from shared.observability.infrastructure.adapters.claude.transcript_cursor import TranscriptCursor  # noqa: E402
from shared.observability.infrastructure.rate_cards.json_rate_card_repository import (  # noqa: E402
    JsonRateCardRepository,
    RateCardError,
)


def load_rate_card(path):
    """Load the approved rate card as the legacy dict shape the event assembly
    reads. Empty path means no rate card (cost stays null). Pricing math lives in
    the shared domain service."""
    if not path:
        return None
    try:
        repo = JsonRateCardRepository(path)
    except RateCardError as error:
        raise SystemExit(str(error))
    meta = repo.metadata()
    return {
        "_repo": repo,
        "_hash": repo.hash,
        "source": meta["source"],
        "currency": meta["currency"],
        "confidence": meta["confidence"],
        "effective_from": meta["effective_from"],
        "approved_by": meta["approved_by"],
    }


def rates_for(model, rate_card):
    if not rate_card:
        return None
    return rate_card["_repo"].raw_rates_for(model)


def calculate_cost(tokens, rates):
    return price_usage_usd(tokens, ModelRate.from_mapping(rates))


def already_attributed_request_ids(path):
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
        request_id = event.get("request_id")
        if request_id:
            seen.add(request_id)
        for item in (event.get("input") or {}).get("request_ids") or []:
            seen.add(item)
    return seen


def existing_usage_events(path):
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
        if event.get("event_type") == "usage_attributed" and event.get("event_scope") == "request":
            events.append(event)
    return events


def load_anchor_events(path):
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
        if event.get("event_type") in ("usage_attributed", "usage_cost_attributed", "interaction_completed"):
            continue
        ts = parse_ts(event.get("ts"))
        if ts is None:
            continue
        events.append({"ts": ts, "event_id": event.get("event_id"), "phase": event.get("phase"), "lane": event.get("lane")})
    events.sort(key=lambda e: e["ts"])
    return events


def enclosing_event(request_ts, events):
    anchor = events[0] if events else None
    for event in events:
        if event["ts"] <= request_ts:
            anchor = event
        else:
            break
    return anchor


def default_output_path(state_path):
    if not state_path:
        return None
    candidate = state_path.parent / "05-operation" / "011-observability-log.jsonl"
    return candidate if candidate.exists() else None


def phase_lane(args, state_fields, anchor):
    phase = value_or(args.phase, value_or((anchor or {}).get("phase"), value_or(state_fields.get("current phase"), "operation")))
    lane = value_or((anchor or {}).get("lane"), value_or(state_fields.get("lane"), value_or(state_fields.get("modo"), "unknown")))
    return phase, lane


def make_request_event(request, args, state_fields, anchor, rate_card, sequence):
    tokens = {
        "tokens_input": request["tokens_input"],
        "tokens_output": request["tokens_output"],
        "tokens_cache_creation": request["tokens_cache_creation"],
        "tokens_cache_read": request["tokens_cache_read"],
    }
    tokens["total_tokens"] = sum(tokens.values())
    cost = None
    confidence = "unavailable"
    rates = rates_for(request.get("model"), rate_card)
    if rate_card and not rates:
        raise SystemExit(f"Rate card has no rates for model: {request.get('model') or 'unknown'}")
    if rates:
        cost = calculate_cost(tokens, rates)
        confidence = value_or(rate_card.get("confidence"), "rated")
    phase, lane = phase_lane(args, state_fields, anchor)
    anchor_ref = anchor.get("event_id") if anchor else None
    interaction_id = request.get("interaction_id")
    return {
        "schema_version": "alfred.observability.v1",
        "alfred": {
            "version": value_or(state_fields.get("framework version"), "unknown"),
            "framework_ref": value_or(state_fields.get("framework ref"), "local"),
            "framework_commit": value_or(state_fields.get("framework commit"), None),
            "schema_version": "alfred.observability.v1",
        },
        "ts": iso(request.get("ts")) or now_iso(),
        "event_id": f"usage-request-{request['request_id']}",
        "event_scope": "request",
        "trace_id": value_or(state_fields.get("alfred run id"), value_or(args.run_id, "unknown")),
        "session_id": value_or(args.session_id, value_or(request.get("session_id"), value_or(state_fields.get("usage session id"), "unknown"))),
        "interaction_id": interaction_id,
        "request_id": request["request_id"],
        "interaction_sequence": request.get("interaction_sequence"),
        "request_sequence": request.get("request_sequence"),
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
            "goal": "Attribute exact host transcript usage at request scope",
        },
        "artifacts_used": [
            canonical_artifact(str(args.transcript_path), "read", selection_reason="host_transcript_usage", observed_by="claude_hook", ts=iso(request.get("ts")))
        ],
        "duration_ms": None,
        "tokens_input": tokens["tokens_input"],
        "tokens_output": tokens["tokens_output"],
        "tokens_cache_creation": tokens["tokens_cache_creation"],
        "tokens_cache_read": tokens["tokens_cache_read"],
        "cost_usd": cost,
        "retry_count": None,
        "token_confidence": "exact",
        "interaction_confidence": request.get("interaction_confidence"),
        "correlation_method": request.get("correlation_method"),
        "input": {
            "source": "host_transcript",
            "source_kind": "host_transcript",
            "granularity": "request",
            "legacy_granularity_alias": "turn" if args.granularity == "turn" else None,
            "request_ids": [request["request_id"]],
            "anchor_event_id": anchor_ref,
        },
        "derivation": {
            "rules_applied": ["connectors/usage-cost.md", "metrics/metrics.md"],
            "method": "request-attribution: exact tokens from transcript requestId; interaction correlation from promptId/user boundary when available",
            "attribution": "derived",
        },
        "output": {
            "model": request.get("model"),
            **tokens,
            "cost_usd": cost,
            "currency": (rate_card or {}).get("currency"),
            "cost_confidence": confidence,
            "token_confidence": "exact",
        },
        "model": request.get("model"),
        "tool": "scripts/metrics/attribute-usage-transcript.py",
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
        "assumptions": [] if interaction_id else ["Host transcript did not expose an interaction id for this request."],
        "metric_impact": {"usage_attribution": "added"},
        "next": [],
        "metadata": {
            "connector_type": "usage-cost",
            "source_kind": "host_transcript",
            "granularity": "request",
            "cost_source_kind": "usage_rate_card" if rates else None,
            "rate_card_source": (rate_card or {}).get("source"),
            "rate_card_effective_from": (rate_card or {}).get("effective_from"),
            "rate_card_approved_by": (rate_card or {}).get("approved_by"),
            "rate_card_hash": (rate_card or {}).get("_hash"),
        },
    }


def event_to_request(event):
    output = event.get("output") or {}
    return {
        "interaction_id": event.get("interaction_id"),
        "session_id": event.get("session_id"),
        "request_id": event.get("request_id") or ((event.get("input") or {}).get("request_ids") or [None])[0],
        "model": event.get("model") or output.get("model"),
        "phase": event.get("phase"),
        "lane": event.get("lane"),
        "ts": parse_ts(event.get("ts")),
        "tokens_input": output.get("tokens_input") if output.get("tokens_input") is not None else event.get("tokens_input"),
        "tokens_output": output.get("tokens_output") if output.get("tokens_output") is not None else event.get("tokens_output"),
        "tokens_cache_creation": output.get("tokens_cache_creation"),
        "tokens_cache_read": output.get("tokens_cache_read"),
    }


def make_interaction_events(request_events, state_fields):
    by_interaction = defaultdict(list)
    for event in request_events:
        interaction_id = event.get("interaction_id")
        if interaction_id:
            by_interaction[interaction_id].append(event)
    events = []
    for index, (interaction_id, group) in enumerate(sorted(by_interaction.items()), start=1):
        group.sort(key=lambda e: e.get("ts") or "")
        first = group[0]
        tokens = Counter()
        models = set()
        phases = set()
        lanes = set()
        for event in group:
            current = usage_tokens(event)
            for key in ("tokens_input", "tokens_output", "tokens_cache_creation", "tokens_cache_read", "total_tokens"):
                tokens[key] += current[key]
            if event.get("model"):
                models.add(event["model"])
            if event.get("phase"):
                phases.add(event["phase"])
            if event.get("lane"):
                lanes.add(event["lane"])
        denominator = tokens["tokens_input"] + tokens["tokens_cache_creation"] + tokens["tokens_cache_read"]
        cache_ratio = None if denominator == 0 else tokens["tokens_cache_read"] / denominator
        events.append(
            {
                "schema_version": "alfred.observability.v1",
                "alfred": first.get("alfred") or {"schema_version": "alfred.observability.v1"},
                "ts": first.get("ts") or now_iso(),
                "event_id": f"interaction-completed-{interaction_id}",
                "event_scope": "interaction",
                "trace_id": first.get("trace_id"),
                "session_id": first.get("session_id"),
                "interaction_id": interaction_id,
                "request_id": None,
                "sequence": index,
                "initiative_id": first.get("initiative_id"),
                "demand_id": first.get("demand_id"),
                "event_type": "interaction_completed",
                "phase": first.get("phase"),
                "lane": first.get("lane"),
                "actor_type": "system",
                "actor_id": "usage-cost-transcript",
                "action": "aggregate_interaction_usage",
                "status": "recorded",
                "step": {"id": "usage-cost", "name": "Usage and cost attribution", "sequence": index, "goal": "Aggregate request usage by interaction"},
                "artifacts_used": [],
                "duration_ms": None,
                "tokens_input": None,
                "tokens_output": None,
                "tokens_cache_creation": None,
                "tokens_cache_read": None,
                "cost_usd": None,
                "retry_count": None,
                "request_count": len(group),
                "tool_call_count": None,
                "tool_failure_count": None,
                "usage": {
                    "tokens_input": tokens["tokens_input"],
                    "tokens_output": tokens["tokens_output"],
                    "tokens_cache_creation": tokens["tokens_cache_creation"],
                    "tokens_cache_read": tokens["tokens_cache_read"],
                    "total_tokens": tokens["total_tokens"],
                    "cache_reuse_ratio": cache_ratio,
                },
                "context": {
                    "unique_artifacts_read": None,
                    "framework_rules_read": None,
                    "skills_loaded": None,
                    "source_files_read": None,
                    "logs_read": None,
                    "repeated_reads": None,
                    "total_bytes_read": None,
                    "compression_used": None,
                    "rtk_used": None,
                },
                "outcome": None,
                "input": {"source": "usage_attributed_events", "request_ids": [e.get("request_id") for e in group]},
                "derivation": {"rules_applied": ["metrics/metrics.md"], "method": "sum effective request-scope usage events by interaction_id"},
                "output": {"models": sorted(models), "phases": sorted(phases), "lanes": sorted(lanes)},
                "model": ",".join(sorted(models)) if len(models) == 1 else None,
                "tool": "scripts/metrics/attribute-usage-transcript.py",
                "parent_event_id": None,
                "artifacts": [],
                "files_changed": [],
                "validation": {"source_request_events": len(group)},
                "risk": None,
                "blocker": None,
                "error": None,
                "state_transition": None,
                "actions": [{"type": "aggregate_interaction_usage", "status": "completed"}],
                "questions_open": [],
                "assumptions": [],
                "metric_impact": {"interaction_usage": "aggregated"},
                "next": [],
                "metadata": {
                    "connector_type": "usage-cost",
                    "source_kind": "derived_observability",
                    "correlation_method": "interaction_id",
                    "framework_version": state_fields.get("framework version"),
                },
            }
        )
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript-path", "-TranscriptPath", dest="transcript_path", required=True)
    parser.add_argument("--state-path", "-StatePath", dest="state_path", default="")
    parser.add_argument("--events-path", "-EventsPath", dest="events_path", default="")
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    parser.add_argument("--granularity", "-Granularity", dest="granularity", choices=["request", "turn", "window", "interaction"], default="request")
    parser.add_argument("--emit-interactions", "-EmitInteractions", dest="emit_interactions", action="store_true", default=False)
    parser.add_argument("--cursor-path", "-CursorPath", dest="cursor_path", default="")
    parser.add_argument("--no-cursor-update", "-NoCursorUpdate", dest="cursor_update", action="store_false", default=True)
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
            "Do not allocate ccusage/session totals into interactions; use --rate-card-path."
        )

    state_path = Path(args.state_path).resolve() if args.state_path else None
    state_fields = read_state_fields(state_path) if state_path else {}
    rate_card = load_rate_card(args.rate_card_path)
    output_path = Path(args.output_path).resolve() if args.output_path else default_output_path(state_path)
    requests, _tools, _start_offset, end_offset = ClaudeTranscriptAdapter().load_requests(args.transcript_path, args.cursor_path)

    since = parse_ts(args.since) if args.since else None
    if since is not None:
        requests = [r for r in requests if r["ts"] >= since]

    if args.append and output_path:
        seen = already_attributed_request_ids(output_path)
        requests = [r for r in requests if r["request_id"] not in seen]

    if not requests:
        if args.cursor_path and args.cursor_update:
            TranscriptCursor().write(args.cursor_path, args.transcript_path, end_offset)
        print("No new transcript requests to attribute.")
        return

    events_path = args.events_path or (str(output_path) if output_path else "")
    anchors = load_anchor_events(events_path) if events_path else []

    request_events = []
    for index, request in enumerate(requests, start=1):
        anchor = enclosing_event(request["ts"], anchors)
        request_events.append(make_request_event(request, args, state_fields, anchor, rate_card, index))

    output_events = []
    if args.granularity in ("request", "turn", "window"):
        output_events.extend(request_events)
    if args.granularity == "interaction" or args.emit_interactions:
        aggregate_input = []
        if output_path:
            aggregate_input.extend(existing_usage_events(output_path))
        aggregate_input.extend(request_events)
        output_events.extend(make_interaction_events(aggregate_input, state_fields))

    lines = [json.dumps(event, separators=(",", ":")) for event in output_events]
    if output_path and args.append:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
        print(f"Appended {len(lines)} attribution events to {output_path}")
    else:
        for line in lines:
            print(line)

    if args.cursor_path and args.cursor_update:
        TranscriptCursor().write(args.cursor_path, args.transcript_path, end_offset, requests[-1].get("request_id"))


if __name__ == "__main__":
    main()
