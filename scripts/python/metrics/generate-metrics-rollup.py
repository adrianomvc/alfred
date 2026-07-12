#!/usr/bin/env python3
"""Turn observability JSONL into a decision-oriented Markdown metrics rollup."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import find_observability_logs, value_or  # noqa: E402
from metrics.observability import (  # noqa: E402
    cost_value,
    effective_events,
    normalize_artifacts_used,
    usage_tokens,
)

USAGE_EVENT = "usage_attributed"
COST_EVENT = "usage_cost_attributed"


def pct(part, total):
    if total == 0:
        return "n/a"
    return f"{(part / total) * 100:.1f}%"


def money(value):
    return "n/a" if value is None else f"US$ {value:.4f}"


def ratio(value):
    return "n/a" if value is None else f"{value * 100:.1f}%"


def group_by(events, key):
    groups = defaultdict(list)
    for event in events:
        groups[event.get(key)].append(event)
    return groups


def read_events(root):
    events = []
    for file in find_observability_logs(root):
        for line_number, raw in enumerate(file.read_text(encoding="utf-8-sig").splitlines(), start=1):
            if raw.strip() == "":
                continue
            event = json.loads(raw)
            event["_source_file"] = str(file)
            event["_source_line"] = line_number
            events.append(event)
    return events


def add_tokens(target, event):
    tokens = usage_tokens(event)
    for key in ("tokens_input", "tokens_output", "tokens_cache_creation", "tokens_cache_read", "total_tokens"):
        target[key] += tokens[key]


def cache_ratio(tokens):
    # cache_reuse_ratio = cache_read / (input + cache_creation + cache_read)
    denominator = tokens["tokens_input"] + tokens["tokens_cache_creation"] + tokens["tokens_cache_read"]
    if denominator == 0:
        return None
    return tokens["tokens_cache_read"] / denominator


def demand_key(event):
    return value_or(event.get("demand_id"), "unknown")


def artifact_key(item):
    return item.get("path_hash") or item.get("path") or "unknown"


def summarize(events):
    metric_events = effective_events(events)
    usage_events = [e for e in metric_events if e.get("event_type") == USAGE_EVENT]
    cost_events = [e for e in metric_events if e.get("event_type") == COST_EVENT]
    interaction_events = [e for e in metric_events if e.get("event_type") == "interaction_completed"]

    tokens = Counter()
    for event in usage_events:
        add_tokens(tokens, event)

    total_cost = sum(value for value in (cost_value(e) for e in cost_events) if value is not None)
    requests = {
        e.get("request_id") or tuple((e.get("input") or {}).get("request_ids") or [e.get("event_id")])
        for e in usage_events
    }
    requests.discard(None)
    interactions = {e.get("interaction_id") for e in metric_events if e.get("interaction_id")}

    quality = {
        "session_id": sum(1 for e in metric_events if e.get("session_id")),
        "interaction_id": sum(1 for e in metric_events if e.get("interaction_id")),
        "model": sum(1 for e in metric_events if e.get("model") or (e.get("output") or {}).get("model")),
        "usage_exact": sum(1 for e in usage_events if (e.get("token_confidence") or (e.get("output") or {}).get("token_confidence")) == "exact"),
        "cost": sum(1 for e in cost_events if cost_value(e) is not None),
        "artifacts": sum(1 for e in metric_events if normalize_artifacts_used(e.get("artifacts_used"), ts=e.get("ts"))),
        "outcome": sum(1 for e in metric_events if e.get("outcome")),
    }

    by_demand = defaultdict(lambda: {"events": [], "usage": [], "cost": [], "tokens": Counter(), "cost_usd": 0.0})
    by_phase = defaultdict(lambda: {"events": [], "usage": [], "cost": [], "tokens": Counter(), "cost_usd": 0.0})
    by_model = defaultdict(lambda: {"events": [], "usage": [], "cost": [], "tokens": Counter(), "cost_usd": 0.0})
    by_lane = defaultdict(lambda: {"events": [], "usage": [], "cost": [], "tokens": Counter(), "cost_usd": 0.0})

    for event in metric_events:
        groups = [
            by_demand[demand_key(event)],
            by_phase[value_or(event.get("phase"), "unknown")],
            by_lane[value_or(event.get("lane"), "unknown")],
            by_model[value_or(event.get("model") or (event.get("output") or {}).get("model"), "unknown")],
        ]
        for group in groups:
            group["events"].append(event)
        if event.get("event_type") == USAGE_EVENT:
            for group in groups:
                group["usage"].append(event)
                add_tokens(group["tokens"], event)
        if event.get("event_type") == COST_EVENT:
            value = cost_value(event)
            if value is not None:
                for group in groups:
                    group["cost"].append(event)
                    group["cost_usd"] += value

    artifacts = {}
    interaction_cost = defaultdict(float)
    for event in cost_events:
        if event.get("interaction_id") and cost_value(event) is not None:
            interaction_cost[event["interaction_id"]] += cost_value(event)

    for event in metric_events:
        for item in normalize_artifacts_used(event.get("artifacts_used"), observed_by=event.get("actor_id"), ts=event.get("ts")):
            key = artifact_key(item)
            stat = artifacts.setdefault(
                key,
                {
                    "path": item.get("path") or item.get("path_hash") or "unknown",
                    "artifact_type": item.get("artifact_type") or "unknown",
                    "interactions": set(),
                    "reads": 0,
                    "repeated_reads": 0,
                    "last_hash": None,
                    "phases": set(),
                    "models": set(),
                    "costs": [],
                    "size_bytes": [],
                },
            )
            if event.get("interaction_id"):
                stat["interactions"].add(event["interaction_id"])
            if item.get("operation") in ("read", "source_usage_export", "approved_rate_card"):
                stat["reads"] += 1
                if item.get("content_hash") and item["content_hash"] == stat["last_hash"]:
                    stat["repeated_reads"] += 1
                if item.get("content_hash"):
                    stat["last_hash"] = item["content_hash"]
            if event.get("phase"):
                stat["phases"].add(event["phase"])
            model = event.get("model") or (event.get("output") or {}).get("model")
            if model:
                stat["models"].add(model)
            if event.get("interaction_id") and event["interaction_id"] in interaction_cost:
                stat["costs"].append(interaction_cost[event["interaction_id"]])
            if item.get("size_bytes") is not None:
                stat["size_bytes"].append(item["size_bytes"])

    return {
        "events": events,
        "metric_events": metric_events,
        "usage_events": usage_events,
        "cost_events": cost_events,
        "interaction_events": interaction_events,
        "tokens": tokens,
        "total_cost": total_cost,
        "requests": requests,
        "interactions": interactions,
        "quality": quality,
        "by_demand": by_demand,
        "by_phase": by_phase,
        "by_model": by_model,
        "by_lane": by_lane,
        "artifacts": artifacts,
    }


def table_group(lines, title, groups, key_label):
    lines.append("")
    lines.append(f"## {title}")
    lines.append(f"| {key_label} | Events | Usage events | Cost events | Cost | Input | Cache created | Cache reused | Output | Cache reuse |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for name in sorted(groups, key=lambda value: str(value)):
        group = groups[name]
        tokens = group["tokens"]
        lines.append(
            f"| {value_or(name, 'unknown')} | {len(group['events'])} | {len(group['usage'])} | {len(group['cost'])} | "
            f"{money(group['cost_usd'])} | {tokens['tokens_input']} | {tokens['tokens_cache_creation']} | "
            f"{tokens['tokens_cache_read']} | {tokens['tokens_output']} | {ratio(cache_ratio(tokens))} |"
        )


def render(summary, root_arg, root):
    tokens = summary["tokens"]
    metric_events = summary["metric_events"]
    lines = []
    lines.append("# Generated Metrics Rollup")
    lines.append("")
    lines.append(f"Generated from observability JSONL under `{root_arg}` = `{root}`.")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- events: {len(metric_events)} effective / {len(summary['events'])} raw")
    lines.append(f"- demands: {len(summary['by_demand'])}")
    lines.append(f"- interactions observed: {len(summary['interactions'])}")
    lines.append(f"- requests observed: {len(summary['requests'])}")
    lines.append(f"- usage events: {len(summary['usage_events'])}")
    lines.append(f"- cost events: {len(summary['cost_events'])}")
    lines.append(f"- tokens input: {tokens['tokens_input']}")
    lines.append(f"- tokens cache creation: {tokens['tokens_cache_creation']}")
    lines.append(f"- tokens cache read: {tokens['tokens_cache_read']}")
    lines.append(f"- tokens output: {tokens['tokens_output']}")
    lines.append(f"- tokens processed: {tokens['total_tokens']}")
    lines.append(f"- cache reuse ratio: {ratio(cache_ratio(tokens))}")
    lines.append(f"- cost usd: {money(summary['total_cost'])}")

    table_group(lines, "By Demand", summary["by_demand"], "Demand")
    table_group(lines, "By Phase", summary["by_phase"], "Phase")
    table_group(lines, "By Lane", summary["by_lane"], "Lane")
    table_group(lines, "By Model", summary["by_model"], "Model")

    lines.append("")
    lines.append("## By Artifact")
    lines.append("| Artifact | Type | Interactions | Reads | Repeated unchanged reads | Avg size | Phases | Models | Avg interaction cost |")
    lines.append("|---|---|---:|---:|---:|---:|---|---|---:|")
    for _, stat in sorted(summary["artifacts"].items(), key=lambda item: item[1]["path"]):
        avg_size = "n/a" if not stat["size_bytes"] else f"{sum(stat['size_bytes']) / len(stat['size_bytes']):.0f}"
        avg_cost = None if not stat["costs"] else sum(stat["costs"]) / len(stat["costs"])
        lines.append(
            f"| `{stat['path']}` | {stat['artifact_type']} | {len(stat['interactions'])} | {stat['reads']} | "
            f"{stat['repeated_reads']} | {avg_size} | {', '.join(sorted(stat['phases'])) or 'n/a'} | "
            f"{', '.join(sorted(stat['models'])) or 'n/a'} | {money(avg_cost)} |"
        )

    total = len(metric_events)
    quality = summary["quality"]
    lines.append("")
    lines.append("## Data Quality")
    lines.append(f"- events with session id: {quality['session_id']} / {total} ({pct(quality['session_id'], total)})")
    lines.append(f"- events with interaction id: {quality['interaction_id']} / {total} ({pct(quality['interaction_id'], total)})")
    lines.append(f"- events with model: {quality['model']} / {total} ({pct(quality['model'], total)})")
    lines.append(f"- usage events with exact tokens: {quality['usage_exact']} / {len(summary['usage_events'])} ({pct(quality['usage_exact'], len(summary['usage_events']))})")
    lines.append(f"- cost events with cost: {quality['cost']} / {len(summary['cost_events'])} ({pct(quality['cost'], len(summary['cost_events']))})")
    lines.append(f"- events with artifact metadata: {quality['artifacts']} / {total} ({pct(quality['artifacts'], total)})")
    lines.append(f"- events with outcome: {quality['outcome']} / {total} ({pct(quality['outcome'], total)})")

    lines.append("")
    lines.append("## Gaps")
    if not summary["usage_events"]:
        lines.append("- no exact interaction/request usage events were collected")
    if not summary["cost_events"]:
        lines.append("- no separate interaction cost events were collected")
    legacy_cost = sum(1 for e in metric_events if e.get("event_type") == USAGE_EVENT and cost_value(e) is not None)
    if legacy_cost:
        lines.append(f"- legacy usage events with inline cost ignored for cost totals: {legacy_cost}")
    if quality["model"] < total:
        lines.append(f"- events without model: {total - quality['model']}")
    if not summary["artifacts"]:
        lines.append("- no artifact lineage was observed")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default="examples")
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    events = read_events(root)
    rendered = render(summarize(events), args.root, root)

    if args.output_path:
        Path(args.output_path).write_text(rendered, encoding="utf-8")
        print(f"Wrote metrics rollup to {args.output_path}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
