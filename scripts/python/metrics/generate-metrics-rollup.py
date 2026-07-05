#!/usr/bin/env python3
"""Turn observability JSONL into a Markdown metrics rollup.

Python mirror of ``scripts/powershell/metrics/generate-metrics-rollup.ps1``.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import find_observability_logs, value_or  # noqa: E402


def group_by(events, key):
    groups = defaultdict(list)
    for event in events:
        groups[event.get(key)].append(event)
    return groups


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default="examples")
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    root_prefix = str(root) + "\\"
    events = []
    for file in find_observability_logs(root):
        line_number = 0
        for raw in file.read_text(encoding="utf-8-sig").splitlines():
            line_number += 1
            if raw.strip() == "":
                continue
            event = json.loads(raw)
            event["_source_file"] = str(file)
            event["_source_line"] = line_number
            events.append(event)

    by_demand = group_by(events, "demand_id")
    by_lane = group_by(events, "lane")
    by_phase = group_by(events, "phase")

    total_tokens_input = sum(e["tokens_input"] for e in events if e.get("tokens_input") is not None)
    total_tokens_output = sum(e["tokens_output"] for e in events if e.get("tokens_output") is not None)
    total_cost = sum(e["cost_usd"] for e in events if e.get("cost_usd") is not None)

    lines = []
    lines.append("# Generated Metrics Rollup")
    lines.append("")
    lines.append(f"Generated from observability JSONL under `{args.root}` = `{root}`.")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- events: {len(events)}")
    lines.append(f"- demands: {len(by_demand)}")
    lines.append(f"- tokens input: {total_tokens_input}")
    lines.append(f"- tokens output: {total_tokens_output}")
    lines.append(f"- cost usd: {total_cost}")
    lines.append("")
    lines.append("## By Demand")
    lines.append("| Demand | Initiative | Lane | Events | Last phase | Last status | Source |")
    lines.append("|---|---|---|---:|---|---|---|")

    for name in sorted(by_demand, key=lambda v: str(v)):
        group = by_demand[name]
        ordered = sorted(group, key=lambda e: (str(e.get("ts", "")), e.get("_source_file", ""), e.get("_source_line", 0)))
        last = ordered[-1]
        first = ordered[0]
        source = str(last.get("_source_file", "")).replace(root_prefix, "")
        lines.append(
            f"| {value_or(name, 'unknown')} | {value_or(first.get('initiative_id'), 'unknown')} | "
            f"{value_or(last.get('lane'), 'unknown')} | {len(group)} | "
            f"{value_or(last.get('phase'), 'unknown')} | {value_or(last.get('status'), 'unknown')} | "
            f"`{source}` |"
        )

    lines.append("")
    lines.append("## By Lane")
    lines.append("| Lane | Events |")
    lines.append("|---|---:|")
    for name in sorted(by_lane, key=lambda v: str(v)):
        lines.append(f"| {value_or(name, 'unknown')} | {len(by_lane[name])} |")

    lines.append("")
    lines.append("## By Phase")
    lines.append("| Phase | Events |")
    lines.append("|---|---:|")
    for name in sorted(by_phase, key=lambda v: str(v)):
        lines.append(f"| {value_or(name, 'unknown')} | {len(by_phase[name])} |")

    lines.append("")
    lines.append("## Gaps")
    if total_tokens_input == 0 and total_tokens_output == 0:
        lines.append("- tokens are not automatically collected in these events")
    if total_cost == 0:
        lines.append("- cost is not automatically collected in these events")
    missing_model = sum(1 for e in events if not e.get("model"))
    if missing_model > 0:
        lines.append(f"- events without model: {missing_model}")

    rendered = "\n".join(lines)

    if args.output_path:
        Path(args.output_path).write_text(rendered, encoding="utf-8")
        print(f"Wrote metrics rollup to {args.output_path}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
