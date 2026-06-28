#!/usr/bin/env python3
"""Render the Alfred process toolbar from a demand state file.

Python mirror of ``scripts/powershell/render-toolbar.ps1``.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import get_field, read_lines  # noqa: E402


def get_first_field(lines, names):
    return get_field(lines, names)


def get_checklist_status(lines, phase):
    pattern = re.compile(r"^\s*-\s+\[(x|X| )\]\s+" + re.escape(phase) + r"\b")
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1)
    return " "


def shorten(value, maximum=64):
    if value is None:
        return ""
    if len(value) <= maximum:
        return value
    return value[: maximum - 3] + "..."


def render(state_path, model="default", cost="n/a"):
    if not Path(state_path).exists():
        raise SystemExit(f"State file not found: {state_path}")

    content = read_lines(state_path)

    demand_id = get_field(content, "id") or "unknown"
    sigla = get_field(content, "sigla") or "unknown"
    lane = get_first_field(content, ["lane", "modo"]) or "unknown"
    phase = get_first_field(content, ["current phase", "fase atual"]) or "unknown"
    step = get_first_field(content, ["current step", "etapa atual"]) or "unknown"
    nxt = get_first_field(content, ["next step", "proximo passo", "próximo passo"]) or "unknown"
    checkpoint = get_field(content, "checkpoint") or "n/a"

    time_mode = get_first_field(content, ["tempo", "time mode"])
    checklist_text = "\n".join(
        line for line in content if re.match(r"^\s*-\s+\[[xX ]\]", line)
    )
    is_execution_first = (
        "execution-first" in phase.lower()
        or "execution-first" in time_mode.lower()
        or "execution-first stabilization" in checklist_text.lower()
    )

    if is_execution_first:
        phases = [
            "Execution-first stabilization",
            "Inception posterior",
            "Design posterior",
            "Validate posterior",
            "Operation / post-mortem",
        ]
    else:
        phases = ["Inception", "Design", "Execution", "Validate", "Operation"]

    completed = 0
    phase_parts = []
    for item in phases:
        status = get_checklist_status(content, item)
        if status in ("x", "X"):
            completed += 1
            marker = "x"
        elif item.lower() == phase.lower():
            marker = ">"
        else:
            marker = " "
        phase_parts.append(f"{item} [{marker}]")

    progress = min(100, round((completed / 5) * 100))
    track = " -> ".join(phase_parts)

    lines = []
    if lane.lower() == "fast":
        lines.append(
            f"ALFRED | SIGLA:{sigla} | #{demand_id} | FAST | {phase} | "
            f"model: {model} | cost: {cost} | next: {shorten(nxt, 48)}"
        )
        return lines

    header = f"+-- ALFRED ------------------------------- SIGLA:{sigla} | #{demand_id} --+"
    footer = "+" + ("-" * max(64, len(header) - 2)) + "+"

    lines.append(header)
    lines.append(f"| Lane: {lane.upper()} | Model: {model} | Progress: {progress}% |")
    lines.append(f"| Cost: {cost} |")
    lines.append(f"| {track} |")
    lines.append(f"| Step : {shorten(step, 72)} |")
    lines.append(f"| HITL : {shorten(checkpoint, 72)} |")
    lines.append(f"| Next : {shorten(nxt, 72)} |")
    lines.append(footer)
    return lines


def main():
    parser = argparse.ArgumentParser(description="Render the Alfred process toolbar.")
    parser.add_argument("--state-path", "-StatePath", dest="state_path", required=True)
    parser.add_argument("--model", "-Model", dest="model", default="default")
    parser.add_argument("--cost", "-Cost", dest="cost", default="n/a")
    args = parser.parse_args()

    for line in render(args.state_path, args.model, args.cost):
        print(line)


if __name__ == "__main__":
    main()
