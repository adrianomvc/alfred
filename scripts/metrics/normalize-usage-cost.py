#!/usr/bin/env python3
"""Map host usage exports into append-only Alfred observability events."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import value_or  # noqa: E402
from metrics.observability import canonical_artifact  # noqa: E402


def framework_version():
    version_path = Path.cwd() / "VERSION"
    if version_path.exists():
        return version_path.read_text(encoding="utf-8-sig").splitlines()[0].strip()
    return "unknown"


def base_event(record, input_full_path, line_number, version):
    event_id = f"usage-{record.get('event_id') or line_number}"
    return {
        "schema_version": "alfred.observability.v1",
        "alfred": {
            "version": version,
            "framework_ref": "local",
            "framework_commit": None,
            "schema_version": "alfred.observability.v1",
        },
        "ts": value_or(record.get("ts"), "unknown"),
        "event_id": event_id,
        "event_scope": value_or(record.get("event_scope"), "request"),
        "trace_id": value_or(record.get("trace_id"), "unknown"),
        "session_id": value_or(record.get("session_id"), "unknown"),
        "interaction_id": record.get("interaction_id"),
        "request_id": record.get("request_id"),
        "sequence": line_number,
        "initiative_id": value_or(record.get("initiative_id"), "unknown"),
        "demand_id": value_or(record.get("demand_id"), "unknown"),
        "phase": value_or(record.get("phase"), "operation"),
        "lane": value_or(record.get("lane"), "unknown"),
        "actor_type": "system",
        "actor_id": "usage-cost-adapter",
        "status": "recorded",
        "step": {
            "id": "usage-cost",
            "name": "Usage and cost attribution",
            "sequence": line_number,
            "goal": "Normalize host usage into Alfred observability",
        },
        "artifacts_used": [
            canonical_artifact(str(input_full_path), "read", selection_reason="host_usage_export", observed_by="usage-cost-adapter")
        ],
        "duration_ms": record.get("duration_ms"),
        "tokens_input": record.get("tokens_input"),
        "tokens_output": record.get("tokens_output"),
        "tokens_cache_creation": record.get("tokens_cache_creation"),
        "tokens_cache_read": record.get("tokens_cache_read"),
        "retry_count": record.get("retry_count"),
        "model": record.get("model"),
        "parent_event_id": record.get("parent_event_id"),
        "artifacts": [],
        "files_changed": None,
        "validation": {"source_record_parse": "ok"},
        "risk": None,
        "blocker": None,
        "error": None,
        "state_transition": None,
        "questions_open": [],
        "assumptions": [],
        "next": [],
    }


def usage_event(record, input_full_path, line_number, version):
    event = base_event(record, input_full_path, line_number, version)
    event.update(
        {
            "event_type": "usage_attributed",
            "action": "attribute_usage",
            "cost_usd": None,
            "token_confidence": value_or(record.get("token_confidence"), "exact" if record.get("tokens_input") is not None or record.get("tokens_output") is not None else "unavailable"),
            "input": {
                "source": value_or(record.get("source"), "host_usage_export"),
                "source_line": line_number,
            },
            "derivation": {
                "rules_applied": ["connectors/usage-cost.md", "metrics/metrics.md"],
                "method": "field mapping without rewriting previous events; cost is emitted separately when present",
            },
            "output": {
                "model": record.get("model"),
                "tokens_input": record.get("tokens_input"),
                "tokens_output": record.get("tokens_output"),
                "tokens_cache_creation": record.get("tokens_cache_creation"),
                "tokens_cache_read": record.get("tokens_cache_read"),
                "cost_usd": None,
                "cost_confidence": "unavailable",
            },
            "actions": [{"type": "normalize_usage", "status": "completed", "source_line": line_number}],
            "metric_impact": {"usage_attribution": "added"},
            "metadata": {"connector_type": "usage-cost", "source_kind": "host_usage_export"},
        }
    )
    return event


def cost_event(record, usage, input_full_path, line_number, version):
    if record.get("cost_usd") is None:
        return None
    event = base_event(record, input_full_path, line_number, version)
    event.update(
        {
            "event_id": f"usage-cost-{usage['event_id']}",
            "event_type": "usage_cost_attributed",
            "action": "attribute_interaction_cost",
            "cost_usd": record.get("cost_usd"),
            "input": {
                "source": value_or(record.get("source"), "host_usage_export"),
                "source_line": line_number,
                "parent_event_id": usage["event_id"],
            },
            "derivation": {
                "rules_applied": ["connectors/usage-cost.md", "metrics/metrics.md"],
                "method": "host export provided interaction/request cost; no session-total allocation",
            },
            "output": {
                "model": record.get("model"),
                "tokens_input": record.get("tokens_input"),
                "tokens_output": record.get("tokens_output"),
                "tokens_cache_creation": record.get("tokens_cache_creation"),
                "tokens_cache_read": record.get("tokens_cache_read"),
                "cost_usd": record.get("cost_usd"),
                "cost_confidence": value_or(record.get("cost_confidence"), "exact"),
            },
            "parent_event_id": usage["event_id"],
            "actions": [{"type": "normalize_cost", "status": "completed", "source_line": line_number}],
            "metric_impact": {"interaction_cost_attribution": "added"},
            "metadata": {"connector_type": "usage-cost", "source_kind": "host_usage_export", "cost_granularity": "interaction"},
        }
    )
    return event


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", "-InputPath", dest="input_path", required=True)
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    parser.add_argument("--append", "-Append", dest="append", action="store_true")
    args = parser.parse_args()

    input_full_path = Path(args.input_path).resolve()
    version = framework_version()
    events = []
    for line_number, raw in enumerate(input_full_path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if raw.strip() == "":
            continue
        record = json.loads(raw)
        usage = usage_event(record, input_full_path, line_number, version)
        events.append(json.dumps(usage, separators=(",", ":")))
        cost = cost_event(record, usage, input_full_path, line_number, version)
        if cost:
            events.append(json.dumps(cost, separators=(",", ":")))

    if args.output_path:
        mode = "a" if args.append else "w"
        with open(args.output_path, mode, encoding="utf-8") as handle:
            for line in events:
                handle.write(line + "\n")
        print(f"Wrote usage attribution events to {args.output_path}")
    else:
        for line in events:
            print(line)


if __name__ == "__main__":
    main()
