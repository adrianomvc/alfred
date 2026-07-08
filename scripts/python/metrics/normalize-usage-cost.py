#!/usr/bin/env python3
"""Map host usage exports into append-only Alfred observability events.

Python mirror of ``scripts/powershell/metrics/normalize-usage-cost.ps1``.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import value_or  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", "-InputPath", dest="input_path", required=True)
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    parser.add_argument("--append", "-Append", dest="append", action="store_true")
    args = parser.parse_args()

    input_full_path = Path(args.input_path).resolve()

    framework_version = "unknown"
    version_path = Path.cwd() / "VERSION"
    if version_path.exists():
        framework_version = version_path.read_text(encoding="utf-8-sig").splitlines()[0].strip()

    events = []
    line_number = 0
    for raw in input_full_path.read_text(encoding="utf-8-sig").splitlines():
        line_number += 1
        if raw.strip() == "":
            continue
        record = json.loads(raw)
        event_id = f"usage-{line_number}"
        if record.get("event_id"):
            event_id = f"usage-{record['event_id']}"

        event = {
            "schema_version": "alfred.observability.v1",
            "alfred": {
                "version": framework_version,
                "framework_ref": "local",
                "framework_commit": None,
                "schema_version": "alfred.observability.v1",
            },
            "ts": value_or(record.get("ts"), "unknown"),
            "event_id": event_id,
            "trace_id": value_or(record.get("trace_id"), "unknown"),
            "session_id": value_or(record.get("session_id"), "unknown"),
            "interaction_id": value_or(record.get("interaction_id"), "unknown"),
            "sequence": line_number,
            "initiative_id": value_or(record.get("initiative_id"), "unknown"),
            "demand_id": value_or(record.get("demand_id"), "unknown"),
            "event_type": "usage_attributed",
            "phase": value_or(record.get("phase"), "operation"),
            "lane": value_or(record.get("lane"), "unknown"),
            "actor_type": "system",
            "actor_id": "usage-cost-adapter",
            "action": "attribute_usage",
            "status": "recorded",
            "step": {
                "id": "usage-cost",
                "name": "Usage and cost attribution",
                "sequence": line_number,
                "goal": "Normalize host usage into Alfred observability",
            },
            "artifacts_used": [
                {
                    "path": str(input_full_path),
                    "role": "source_usage_export",
                    "action": "read",
                }
            ],
            "duration_ms": None,
            "tokens_input": record.get("tokens_input"),
            "tokens_output": record.get("tokens_output"),
            "cost_usd": record.get("cost_usd"),
            "retry_count": 0,
            "input": {
                "source": value_or(record.get("source"), "host_usage_export"),
                "source_line": line_number,
            },
            "derivation": {
                "rules_applied": ["connectors/usage-cost.md", "metrics/metrics.md"],
                "method": "field mapping without rewriting previous events",
            },
            "output": {
                "model": record.get("model"),
                "tokens_input": record.get("tokens_input"),
                "tokens_output": record.get("tokens_output"),
                "cost_usd": record.get("cost_usd"),
            },
            "model": record.get("model"),
            "tool": "scripts/python/metrics/normalize-usage-cost.py",
            "parent_event_id": record.get("parent_event_id"),
            "artifacts": [],
            "files_changed": [],
            "validation": {"source_record_parse": "ok"},
            "risk": None,
            "blocker": None,
            "error": None,
            "state_transition": None,
            "actions": [
                {"type": "normalize", "status": "completed", "source_line": line_number}
            ],
            "questions_open": [],
            "assumptions": [],
            "metric_impact": {"usage_attribution": "added"},
            "next": [],
            "metadata": {"connector_type": "usage-cost"},
        }
        events.append(json.dumps(event, separators=(",", ":")))

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
