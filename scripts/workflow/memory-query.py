#!/usr/bin/env python3
"""Bounded progressive-disclosure queries over HUB Markdown memory."""

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.common.memory_index import load_observations, searchable_text  # noqa: E402


def compact_line(item):
    stale = " stale" if is_stale(item) else ""
    return (f"{item['id']} | {item['type']}{stale} | {item['title']} | "
            f"trigger={item['trigger']} | ~{item['estimated_tokens']} tk")


def is_stale(item):
    source = item.get("source-ref")
    expected = item.get("source-hash")
    if not source or not expected:
        return False
    source_path = item["path"].parents[1] / source
    if not source_path.is_file():
        return True
    import hashlib
    actual = hashlib.sha256(source_path.read_bytes()).hexdigest()
    return actual != expected


def select(items, query, limit):
    terms = [term.lower() for term in query.split() if term]
    matches = [item for item in items if all(term in searchable_text(item) for term in terms)]
    return matches[:limit]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    startup = sub.add_parser("startup")
    startup.add_argument("--budget", type=int, default=1000)
    search = sub.add_parser("search")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=10)
    timeline = sub.add_parser("timeline")
    timeline.add_argument("--id", required=True)
    timeline.add_argument("--before", type=int, default=2)
    timeline.add_argument("--after", type=int, default=2)
    get = sub.add_parser("get")
    get.add_argument("--id", action="append", required=True)
    args = parser.parse_args()
    try:
        items = load_observations(Path(args.root).resolve())
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if args.command == "startup":
        used = 0
        ordered = sorted(
            items,
            key=lambda item: (
                item["type"] != "gotcha",
                -date.fromisoformat(item["date"]).toordinal(),
                item["id"],
            ),
        )
        for item in ordered:
            cost = max(12, len(compact_line(item)) // 4)
            if used + cost > args.budget:
                continue
            print(compact_line(item)); used += cost
    elif args.command == "search":
        for item in select(items, args.query, max(1, args.limit)):
            print(compact_line(item))
    elif args.command == "timeline":
        ordered = sorted(items, key=lambda item: (item["date"], item["id"]))
        indexes = [index for index, item in enumerate(ordered) if item["id"] == args.id]
        if not indexes:
            raise SystemExit(f"Unknown memory id: {args.id}")
        anchor = indexes[0]
        for item in ordered[max(0, anchor - args.before):anchor + args.after + 1]:
            print(compact_line(item))
    else:
        by_id = {item["id"]: item for item in items}
        for item_id in args.id:
            if item_id not in by_id:
                raise SystemExit(f"Unknown memory id: {item_id}")
            print(by_id[item_id]["path"].read_text(encoding="utf-8-sig").rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
