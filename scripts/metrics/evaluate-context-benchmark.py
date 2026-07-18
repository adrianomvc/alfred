#!/usr/bin/env python3
"""Evaluate provider JSONL against the bounded-read baseline."""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def evaluate(records):
    by_provider = defaultdict(list)
    baselines = {}
    for record in records:
        by_provider[record["provider"]].append(record)
        if record["provider"] == "baseline":
            baselines[record["case_id"]] = record
    results = {}
    for provider, rows in by_provider.items():
        if provider == "baseline":
            continue
        ratios, expected, found = [], set(), set()
        correct = True
        for row in rows:
            base = baselines.get(row["case_id"])
            if not base or not base.get("tokens"):
                continue
            ratios.append(float(row["tokens"]) / float(base["tokens"]))
            expected.update(f"{row['case_id']}:{item}" for item in row.get("expected_targets", []))
            found.update(f"{row['case_id']}:{item}" for item in row.get("found_targets", []))
            correct = correct and bool(row.get("correct")) and bool(row.get("complete", True))
        reduction = round((1 - statistics.median(ratios)) * 100, 1) if ratios else 0.0
        recall = round(len(expected & found) / len(expected) * 100, 1) if expected else 0.0
        results[provider] = {"cases": len(ratios), "median_token_reduction_pct": reduction,
                             "target_recall_pct": recall, "correct_and_complete": correct,
                             "eligible": len(ratios) >= 15 and reduction >= 30 and recall >= 95 and correct}
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    records = [json.loads(line) for line in Path(args.input).read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    result = evaluate(records)
    if args.as_json:
        print(json.dumps(result))
    else:
        for provider, metrics in result.items():
            print(f"{provider}: cases={metrics['cases']} reduction={metrics['median_token_reduction_pct']}% "
                  f"recall={metrics['target_recall_pct']}% eligible={metrics['eligible']}")
    return 0 if result and all(item["eligible"] for item in result.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
