#!/usr/bin/env python3
"""Append interaction cost events from exact usage plus an approved rate card.

Policy: no session-total allocation.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metrics.observability import canonical_artifact  # noqa: E402
from shared.common import iter_jsonl  # noqa: E402
from shared.observability.application.use_cases.apply_usage_rate_card import (  # noqa: E402
    ApplyUsageRateCard,
    ApplyUsageRateCardCommand,
    LoadedRateCard,
)
from shared.observability.infrastructure.rate_cards.json_rate_card_repository import (  # noqa: E402
    JsonRateCardRepository,
    RateCardError,
)


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_rate_card(path):
    """Load the approved rate card, exposing the legacy dict shape the cost
    event assembly reads (`_hash`, `_path`, metadata). Pricing math lives in the
    shared domain service."""
    try:
        repo = JsonRateCardRepository(path)
    except RateCardError as error:
        raise SystemExit(str(error))
    meta = repo.metadata()
    return LoadedRateCard(
        repository=repo,
        hash=repo.hash,
        path=repo.path,
        source=meta["source"],
        currency=meta["currency"],
        confidence=meta["confidence"],
        effective_from=meta["effective_from"],
        approved_by=meta["approved_by"],
    )


def iter_events(path):
    for line_number, event, _raw in iter_jsonl(path):
        if event is None:
            raise SystemExit(f"Invalid JSONL in {path} at line {line_number}")
        yield event


def existing_cost_keys(path):
    keys = set()
    if not path or not Path(path).exists():
        return keys
    for event in iter_events(path):
        if event.get("event_type") != "usage_cost_attributed":
            continue
        metadata = event.get("metadata") or {}
        keys.add((event.get("parent_event_id"), metadata.get("rate_card_hash")))
    return keys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", "-InputPath", dest="input_path", required=True)
    parser.add_argument("--rate-card-path", "-RateCardPath", dest="rate_card_path", required=True)
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    parser.add_argument("--append", "-Append", dest="append", action="store_true", default=True)
    parser.add_argument("--no-append", "-NoAppend", dest="append", action="store_false")
    args = parser.parse_args()

    input_path = Path(args.input_path).resolve()
    output_path = Path(args.output_path).resolve() if args.output_path else input_path
    rate_card = load_rate_card(args.rate_card_path)
    seen = existing_cost_keys(output_path) if args.append else set()

    result = ApplyUsageRateCard(artifact_builder=canonical_artifact, now=now_iso).execute(
        ApplyUsageRateCardCommand(tuple(iter_events(input_path)), seen, rate_card)
    )
    lines = [json.dumps(event, separators=(",", ":")) for event in result.events]

    if not lines:
        raise SystemExit(f"No interaction cost events generated.{result.empty_detail()}")

    if args.append:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
        print(f"Appended {len(lines)} interaction cost events to {output_path}")
    else:
        for line in lines:
            print(line)


if __name__ == "__main__":
    main()
