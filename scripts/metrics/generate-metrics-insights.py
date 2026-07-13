#!/usr/bin/env python3
"""Generate human-reviewable observability insights from Alfred JSONL events."""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import find_observability_logs  # noqa: E402
from shared.common import iter_jsonl  # noqa: E402
from metrics.observability import cost_value, effective_events, normalize_artifacts_used, usage_tokens  # noqa: E402


def read_events(root):
    events = []
    for file in find_observability_logs(root):
        for line_number, event, _raw in iter_jsonl(file):
            if event is None:
                raise SystemExit(f"Invalid JSONL in {file} at line {line_number}")
            event["_source_file"] = str(file)
            event["_source_line"] = line_number
            events.append(event)
    return effective_events(events)


def insight_block(title, observation, evidence, likely_cause, proposed_adjustment,
                  expected_effect, risk, confidence, pilot):
    return [
        f"## {title}",
        f"- Observation: {observation}",
        f"- Evidence: {evidence}",
        f"- Likely cause: {likely_cause}",
        f"- Proposed adjustment: {proposed_adjustment}",
        f"- Expected effect: {expected_effect}",
        f"- Risk/trade-off: {risk}",
        f"- Confidence: {confidence}",
        f"- Pilot recommendation: {pilot}",
        "- Human decision: pending",
        "",
    ]


def generate(events):
    lines = ["# Generated Metrics Insights", ""]
    artifact_reads = defaultdict(list)
    cache_ratios = []
    terminal_events = []

    for event in events:
        if event.get("event_type") == "usage_attributed":
            tokens = usage_tokens(event)
            if tokens["cache_reuse_ratio"] is not None:
                cache_ratios.append((event, tokens["cache_reuse_ratio"]))
        for item in normalize_artifacts_used(event.get("artifacts_used"), ts=event.get("ts")):
            if item.get("operation") == "read":
                key = item.get("path_hash") or item.get("path")
                artifact_reads[key].append((event, item))
        if (event.get("metadata") or {}).get("rtk_used") is False:
            terminal_events.append(event)

    repeated = [(key, rows) for key, rows in artifact_reads.items() if len(rows) > 1]
    if repeated:
        key, rows = sorted(repeated, key=lambda item: len(item[1]), reverse=True)[0]
        lines.extend(
            insight_block(
                "Insight 1 - Repeated Artifact Reads",
                f"`{key}` was read {len(rows)} times in the observed window.",
                ", ".join(f"{event.get('event_id')}:{item.get('content_hash') or 'no-hash'}" for event, item in rows[:5]),
                "The same artifact may be reloaded instead of using a stable snapshot until it changes.",
                "Pilot caching artifact metadata until an `artifact_changed` event or content hash change.",
                "Fewer repeated reads and lower context growth without hiding changed files.",
                "A stale snapshot is possible if artifact changes are not observed.",
                "medium",
                "Run on 5+ Standard demands before changing rules.",
            )
        )

    if cache_ratios:
        avg = sum(value for _, value in cache_ratios) / len(cache_ratios)
        if avg < 0.30:
            lines.extend(
                insight_block(
                    "Insight 2 - Low Cache Reuse",
                    f"Average cache reuse ratio was {avg * 100:.1f}%.",
                    ", ".join(event.get("event_id", "unknown") for event, _ in cache_ratios[:5]),
                    "Volatile context may be loaded before stable framework context, or prompts may be too unique.",
                    "Review prompt-caching-policy ordering and compare stable-prefix loading in a pilot.",
                    "Higher cache reuse without reducing acceptance criteria.",
                    "Over-optimizing context order can hide necessary demand-specific data.",
                    "medium",
                    "Pilot on a demand with repeated sessions.",
                )
            )

    if terminal_events:
        lines.extend(
            insight_block(
                "Insight 3 - Terminal Output Without Reduction",
                f"{len(terminal_events)} event(s) recorded terminal output without RTK/filter reduction.",
                ", ".join(event.get("event_id", "unknown") for event in terminal_events[:5]),
                "Commands may be emitting more context than necessary.",
                "Reinforce terminal-token-policy or install the RTK hook where supported.",
                "Lower terminal context volume while preserving drill-down evidence.",
                "Filtering can hide an important line if the command is scoped poorly.",
                "low",
                "Start with read-only commands and compare raw vs emitted bytes.",
            )
        )

    if len(lines) == 2:
        lines.extend(
            insight_block(
                "Insight 1 - No Actionable Pattern Yet",
                "No repeated artifact, cache, or terminal pattern crossed the pilot heuristics.",
                f"events analyzed: {len(events)}",
                "The sample may be too small or lacks usage/artifact metadata.",
                "Collect more telemetry before changing policies.",
                "Avoids premature governance changes.",
                "Delays optimization until enough evidence exists.",
                "high",
                "Collect at least 5 demands before ratifying a policy change.",
            )
        )

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default="examples")
    parser.add_argument("--output-path", "-OutputPath", dest="output_path", default="")
    args = parser.parse_args()

    rendered = generate(read_events(Path(args.root).resolve()))
    if args.output_path:
        Path(args.output_path).write_text(rendered, encoding="utf-8")
        print(f"Wrote metrics insights to {args.output_path}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
