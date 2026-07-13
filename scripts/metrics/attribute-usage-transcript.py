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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import read_state_fields  # noqa: E402
from metrics.observability import canonical_artifact, now_iso  # noqa: E402
from shared.common import iter_jsonl  # noqa: E402
from shared.observability.application.use_cases.attribute_transcript_usage import (  # noqa: E402
    AttributeTranscriptUsage,
    AttributeTranscriptUsageCommand,
    TranscriptAttributionContext,
)
from shared.observability.infrastructure.adapters.claude.transcript import (  # noqa: E402
    ClaudeTranscriptAdapter,
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


def already_attributed_request_ids(path):
    seen = set()
    if not path or not Path(path).exists():
        return seen
    for _line_number, event, _raw in iter_jsonl(path):
        if event is None:
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
    for _line_number, event, _raw in iter_jsonl(path):
        if event is None:
            continue
        if event.get("event_type") == "usage_attributed" and event.get("event_scope") == "request":
            events.append(event)
    return events


def load_anchor_events(path):
    events = []
    if not path or not Path(path).exists():
        return events
    for _line_number, event, _raw in iter_jsonl(path):
        if event is None:
            continue
        if event.get("event_type") in ("usage_attributed", "usage_cost_attributed", "interaction_completed"):
            continue
        ts = parse_ts(event.get("ts"))
        if ts is None:
            continue
        events.append({"ts": ts, "event_id": event.get("event_id"), "phase": event.get("phase"), "lane": event.get("lane")})
    events.sort(key=lambda e: e["ts"])
    return events


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

    existing_requests = existing_usage_events(output_path) if output_path and (args.granularity == "interaction" or args.emit_interactions) else []
    result = AttributeTranscriptUsage(artifact_builder=canonical_artifact, now=now_iso).execute(
        AttributeTranscriptUsageCommand(
            requests=requests,
            anchors=anchors,
            existing_request_events=existing_requests,
            context=TranscriptAttributionContext(
                transcript_path=str(args.transcript_path),
                state_fields=state_fields,
                rate_card=rate_card,
                granularity=args.granularity,
                emit_interactions=args.emit_interactions,
                run_id=args.run_id,
                phase=args.phase,
                session_id=args.session_id,
            ),
        )
    )
    if result.missing_rate_card_model:
        raise SystemExit(f"Rate card has no rates for model: {result.missing_rate_card_model}")
    output_events = list(result.events)

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
