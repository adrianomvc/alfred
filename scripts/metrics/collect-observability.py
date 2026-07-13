#!/usr/bin/env python3
"""Collect Alfred observability JSONL events from a tree."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import find_observability_logs  # noqa: E402
from shared.common import iter_jsonl  # noqa: E402


def collect_events(root):
    events = []
    for file in find_observability_logs(root):
        for line_number, event, _raw in iter_jsonl(file):
            if event is None:
                raise SystemExit(f"Invalid JSONL in {file} at line {line_number}")
            event["_source_file"] = str(file)
            event["_source_line"] = line_number
            events.append(event)
    events.sort(key=lambda e: (str(e.get("ts", "")), e.get("sequence", 0)))
    return events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default="examples")
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    events = collect_events(root)

    if args.output_path:
        with open(args.output_path, "w", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event, separators=(",", ":")) + "\n")
        print(f"Wrote {len(events)} events to {args.output_path}")
    else:
        for event in events:
            print(
                f"{event.get('ts','')} | {event.get('initiative_id','')} | "
                f"{event.get('demand_id','')} | {event.get('event_type','')} | "
                f"{event.get('phase','')} | {event.get('lane','')} | "
                f"{event.get('status','')} | {event.get('_source_file','')} | "
                f"{event.get('_source_line','')}"
            )


if __name__ == "__main__":
    main()
