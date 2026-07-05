#!/usr/bin/env python3
"""Propose a Risk Mode lane from the objective checklist (core/risk-mode.md).

Python mirror of ``scripts/powershell/workflow/classify-risk.ps1``. Optional helper
(D3): the checklist in ``core/risk-mode.md`` is the source of truth and Alfred
still classifies manually when this cannot run. The AI proposes, the human
confirms (Standard/SAFE) — this helper only computes and explains the proposal.

Each criterion scores 0/1/2 (see the tables in ``core/risk-mode.md``).
Output: the two axis sums, fired hard overrides, the proposed lane, and a
pt-BR block ready to paste into ``01-inception/004-risk.md``.
"""

import argparse
import sys

RISK_CRITERIA = [
    ("reversibility", "Reversibility"),
    ("blast_radius", "Blast radius"),
    ("sensitive_data", "Sensitive/regulated data"),
    ("customer_impact", "Customer impact"),
    ("cost", "Cost / financial risk"),
]
COMPLEXITY_CRITERIA = [
    ("components", "Components affected"),
    ("novelty", "Technical novelty"),
    ("ambiguity", "Requirement ambiguity"),
    ("integrations", "Integrations"),
    ("effort", "Estimated effort"),
]
LANES = ["FAST", "Standard", "SAFE"]


def score_arg(value):
    number = int(value)
    if number not in (0, 1, 2):
        raise argparse.ArgumentTypeError("criterion scores must be 0, 1, or 2")
    return number


def lane_from_score(score):
    if score <= 3:
        return "FAST"
    if score <= 6:
        return "Standard"
    return "SAFE"


def max_lane(a, b):
    return a if LANES.index(a) >= LANES.index(b) else b


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key, label in RISK_CRITERIA + COMPLEXITY_CRITERIA:
        parser.add_argument(
            "--" + key.replace("_", "-"), dest=key, type=score_arg, required=True,
            help=f"{label} (0/1/2)")
    parser.add_argument("--architectural-change", action="store_true",
                        help="hard override: architectural change -> SAFE")
    parser.add_argument("--multi-squad", action="store_true",
                        help="hard override: multi-squad -> SAFE")
    args = parser.parse_args()

    risk = sum(getattr(args, key) for key, _ in RISK_CRITERIA)
    complexity = sum(getattr(args, key) for key, _ in COMPLEXITY_CRITERIA)
    base_score = max(risk, complexity)
    lane = lane_from_score(base_score)

    overrides = []
    critical = [("sensitive_data", "sensitive/regulated data = 2"),
                ("reversibility", "hard/irreversible = 2"),
                ("customer_impact", "direct customer impact = 2")]
    fired = [text for key, text in critical if getattr(args, key) == 2]
    if len(fired) >= 2:
        overrides.append("2+ critical risk criteria -> SAFE (" + "; ".join(fired) + ")")
        lane = max_lane(lane, "SAFE")
    elif len(fired) == 1:
        overrides.append(fired[0] + " -> minimum Standard")
        lane = max_lane(lane, "Standard")
    if args.architectural_change:
        overrides.append("architectural change -> SAFE")
        lane = max_lane(lane, "SAFE")
    if args.multi_squad:
        overrides.append("multi-squad -> SAFE")
        lane = max_lane(lane, "SAFE")

    print(f"risk axis      : {risk}/10")
    print(f"complexity axis: {complexity}/10")
    print(f"base score     : {base_score} -> {lane_from_score(base_score)}")
    for item in overrides:
        print(f"hard override  : {item}")
    print(f"PROPOSED LANE  : {lane}  (AI proposes, human confirms - Standard/SAFE)")
    if lane == "SAFE":
        print("anti-SAFE brake: record the justification (which override/score fired)"
              " in 02-design/006-decisions.md or it drops to Standard.")

    print("\n--- paste into 01-inception/004-risk.md (pt-BR) ---")
    print("## Classificacao")
    print(f"- score de risco: {risk}/10")
    print(f"- score de complexidade: {complexity}/10")
    print(f"- modo proposto: {lane}")
    print("- modo confirmado: <humano confirma>")
    print("\n## Overrides")
    if overrides:
        for item in overrides:
            print(f"- {item}")
    else:
        print("- nenhum")
    return 0


if __name__ == "__main__":
    sys.exit(main())
