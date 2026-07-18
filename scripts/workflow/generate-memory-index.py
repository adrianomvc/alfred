#!/usr/bin/env python3
"""Generate the deterministic cross-demand memory index."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.common.memory_index import escape_cell, load_observations, parse_frontmatter  # noqa: E402,F401


def render_index(hub):
    rows = []
    for data in load_observations(hub):
        path = data["path"]
        rows.append([
            f"`{escape_cell(data['id'])}`", data["type"], escape_cell(data["title"]),
            escape_cell(data["trigger"]), escape_cell(data.get("tags")),
            escape_cell(data.get("files")), str(data["estimated_tokens"]),
            escape_cell(data["source-demand"]), escape_cell(data["date"]),
            f"[memory/{path.name}](memory/{path.name})",
        ])
    lines = [
        "# Memory Index", "",
        "> Generated from observation frontmatter. Do not edit the table by hand.", "",
        "Layer 1 shows what exists and its approximate retrieval cost. Search by trigger/tags, "
        "load details JIT, and open the original source before deciding or editing.", "",
        "## Observations",
        "| Id | Type | Title | Trigger | Tags | Files | ~Tokens | Demand | Date | Link |",
        "|---|---|---|---|---|---|---:|---|---|---|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.extend(["", "## Retrieval", "Use `memory-query.py search|timeline|get`; observations are pointers, not authority."])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", default=".")
    parser.add_argument("--index-name", default="005-memory.md")
    parser.add_argument("--check", "-Check", action="store_true")
    args = parser.parse_args()
    hub = Path(args.root).resolve()
    try:
        content = render_index(hub)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    target = hub / args.index_name
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    if args.check and current != content:
        raise SystemExit(f"Memory index drift: regenerate {target}")
    if not args.check:
        target.write_text(content, encoding="utf-8", newline="\n")
    print(f"OK memory index {target}" if args.check else f"Wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
