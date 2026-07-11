#!/usr/bin/env python3
"""Append interaction cost events from exact usage plus an approved rate card."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_rate_card(path):
    path = Path(path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if payload.get("schema_version") != "alfred.usage-rate-card.v1":
        raise SystemExit("Unsupported rate card schema_version.")
    if not payload.get("models"):
        raise SystemExit("Rate card has no models.")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    payload["_path"] = str(path)
    payload["_hash"] = digest
    return payload


def event_tokens(event):
    output = event.get("output") or {}
    return {
        "tokens_input": int(output.get("tokens_input") or event.get("tokens_input") or 0),
        "tokens_output": int(output.get("tokens_output") or event.get("tokens_output") or 0),
        "tokens_cache_creation": int(output.get("tokens_cache_creation") or event.get("tokens_cache_creation") or 0),
        "tokens_cache_read": int(output.get("tokens_cache_read") or event.get("tokens_cache_read") or 0),
    }


def rate_for(event, rate_card):
    model = event.get("model") or (event.get("output") or {}).get("model")
    rates = rate_card.get("models", {}).get(model)
    return model, rates


def calculate_cost(tokens, rates):
    total = (
        tokens["tokens_input"] * float(rates.get("input_per_1m") or 0)
        + tokens["tokens_output"] * float(rates.get("output_per_1m") or 0)
        + tokens["tokens_cache_creation"] * float(rates.get("cache_creation_per_1m") or 0)
        + tokens["tokens_cache_read"] * float(rates.get("cache_read_per_1m") or 0)
    )
    return round(total / 1_000_000, 8)


def iter_jsonl(path):
    for raw in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not raw.strip():
            continue
        yield json.loads(raw)


def existing_cost_keys(path):
    keys = set()
    if not path or not Path(path).exists():
        return keys
    for event in iter_jsonl(path):
        if event.get("event_type") != "usage_cost_attributed":
            continue
        metadata = event.get("metadata") or {}
        keys.add((event.get("parent_event_id"), metadata.get("rate_card_hash")))
    return keys


def make_cost_event(usage_event, tokens, cost, model, rates, rate_card, sequence):
    parent = usage_event.get("event_id")
    short_hash = rate_card["_hash"][:8]
    return {
        "schema_version": "alfred.observability.v1",
        "alfred": usage_event.get("alfred") or {"schema_version": "alfred.observability.v1"},
        "ts": now_iso(),
        "event_id": f"usage-cost-{parent}-{short_hash}",
        "trace_id": usage_event.get("trace_id"),
        "session_id": usage_event.get("session_id"),
        "interaction_id": usage_event.get("interaction_id"),
        "sequence": sequence,
        "initiative_id": usage_event.get("initiative_id"),
        "demand_id": usage_event.get("demand_id"),
        "event_type": "usage_cost_attributed",
        "phase": usage_event.get("phase"),
        "lane": usage_event.get("lane"),
        "actor_type": "system",
        "actor_id": "usage-rate-card",
        "action": "attribute_interaction_cost",
        "status": "recorded",
        "step": {
            "id": "usage-cost",
            "name": "Usage and cost attribution",
            "sequence": sequence,
            "goal": "Compute interaction cost from exact usage and an approved rate card",
        },
        "artifacts_used": [
            {"path": rate_card["_path"], "role": "approved_rate_card", "action": "read"},
            {"path": parent, "role": "parent_usage_event", "action": "reference"},
        ],
        "duration_ms": None,
        "tokens_input": tokens["tokens_input"],
        "tokens_output": tokens["tokens_output"],
        "cost_usd": cost,
        "retry_count": 0,
        "input": {
            "source": "usage_attributed_event",
            "source_kind": "usage_rate_card",
            "parent_event_id": parent,
            "rate_card_source": rate_card.get("source"),
        },
        "derivation": {
            "rules_applied": [
                "connectors/usage-cost.md",
                "connectors/usage-rate-card.md",
                "metrics/metrics.md",
            ],
            "method": "interaction cost = exact usage units multiplied by approved per-model rate card; no session-total allocation",
            "attribution": "derived",
        },
        "output": {
            "model": model,
            "tokens_input": tokens["tokens_input"],
            "tokens_output": tokens["tokens_output"],
            "tokens_cache_creation": tokens["tokens_cache_creation"],
            "tokens_cache_read": tokens["tokens_cache_read"],
            "cost_usd": cost,
            "currency": rate_card.get("currency", "USD"),
            "cost_confidence": rate_card.get("confidence", "rated"),
            "token_confidence": (usage_event.get("output") or {}).get("token_confidence", "exact"),
            "rates_per_1m": rates,
        },
        "model": model,
        "tool": "scripts/python/metrics/apply-usage-rate-card.py",
        "parent_event_id": parent,
        "artifacts": [],
        "files_changed": [],
        "validation": {"rate_card_parse": "ok", "source_usage_event": "ok"},
        "risk": None,
        "blocker": None,
        "error": None,
        "state_transition": None,
        "actions": [{"type": "attribute_interaction_cost", "status": "completed"}],
        "questions_open": [],
        "assumptions": [],
        "metric_impact": {"interaction_cost_attribution": "added"},
        "next": [],
        "metadata": {
            "connector_type": "usage-rate-card",
            "source_kind": "usage_rate_card",
            "rate_card_source": rate_card.get("source"),
            "rate_card_effective_from": rate_card.get("effective_from"),
            "rate_card_approved_by": rate_card.get("approved_by"),
            "rate_card_currency": rate_card.get("currency", "USD"),
            "rate_card_hash": rate_card["_hash"],
            "cost_granularity": "interaction",
        },
    }


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

    lines = []
    skipped_missing_model = []
    skipped_existing = 0
    for event in iter_jsonl(input_path):
        if event.get("event_type") != "usage_attributed":
            continue
        model, rates = rate_for(event, rate_card)
        if not rates:
            skipped_missing_model.append(model or "unknown")
            continue
        key = (event.get("event_id"), rate_card["_hash"])
        if key in seen:
            skipped_existing += 1
            continue
        tokens = event_tokens(event)
        cost = calculate_cost(tokens, rates)
        cost_event = make_cost_event(event, tokens, cost, model, rates, rate_card, len(lines) + 1)
        lines.append(json.dumps(cost_event, separators=(",", ":")))

    if not lines:
        detail = ""
        if skipped_missing_model:
            detail = f" Missing rate card models: {', '.join(sorted(set(skipped_missing_model)))}."
        if skipped_existing:
            detail += f" Existing cost events skipped: {skipped_existing}."
        raise SystemExit(f"No interaction cost events generated.{detail}")

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
