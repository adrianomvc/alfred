#!/usr/bin/env python3
"""Resolve the model-policy decision for a demand step.

Thin driver over ``shared.model_policy``. Reads lane/phase from a demand
``001-state.md`` (or explicit flags) and prints the tier, concrete model, effort,
and task budget the step must run at — the value the toolbar shows and Alfred
declares on a switch. Source of truth stays ``core/model-policy.md``.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import read_lines  # noqa: E402
from shared.common.markdown_fields import get_field  # noqa: E402
from shared.model_policy import model_advisory, resolve_model_policy  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", "-StatePath", dest="state_path", default="")
    parser.add_argument("--lane", "-Lane", dest="lane", default="")
    parser.add_argument("--phase", "-Phase", dest="phase", default="")
    parser.add_argument("--actual-model", "-ActualModel", dest="actual_model", default="",
                        help="model currently running; used to build the switch advisory")
    parser.add_argument("--json", "-Json", dest="as_json", action="store_true", default=False)
    args = parser.parse_args()

    lane, phase, actual = args.lane, args.phase, args.actual_model
    if args.state_path:
        content = read_lines(args.state_path)
        lane = lane or get_field(content, ["lane", "modo"])
        phase = phase or get_field(content, ["current phase", "fase atual"])
        actual = actual or get_field(content, ["model", "current model", "modelo", "running model"])

    decision = resolve_model_policy(lane, phase)
    if decision is None:
        raise SystemExit(
            f"Cannot resolve model policy from lane={lane!r} phase={phase!r}; "
            "keep the host default and record which model ran (D3)."
        )
    advisory = model_advisory(actual, lane, phase)

    if args.as_json:
        print(json.dumps({
            "tier": decision.tier,
            "model": decision.model,
            "effort": decision.effort,
            "task_budget": decision.task_budget,
            "lane": decision.lane,
            "phase": decision.phase,
            "reason": decision.reason,
            "advisory": advisory,
        }, separators=(",", ":")))
    else:
        budget = f", task budget >= {decision.task_budget}" if decision.task_budget else ""
        print(f"{decision.phase}/{decision.lane}: {decision.model} (tier {decision.tier}, "
              f"effort {decision.effort}{budget}) - {decision.reason}")
        if advisory:
            print(advisory)


if __name__ == "__main__":
    main()
