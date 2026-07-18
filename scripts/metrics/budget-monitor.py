#!/usr/bin/env python3
"""Compare a demand's consumption against its budget and report a decision.

Reads the demand `state`: the consumed amount (`demand acu`, written by
`session-cost.py`), the `budget limit`, `budget near threshold`, and
`budget on limit`. Emits a status (within｜near｜exceeded｜unmeasurable), the
percent consumed, and a delivery-vs-budget report (phases completed). The
`budget-policy` rule turns this into a decision: near -> propose accelerating
(skip optional sub-activities); exceeded -> report delivered vs budget and
pause/stop. This script never decides or blocks — it measures.

No fresh consumption reading (`demand acu` absent) -> `unmeasurable`; ask the
human to run `/usage` and `session-cost.py` first. Never invents a number (D10).
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.common import read_state_fields, write_state_fields  # noqa: E402

CHECK_RE = re.compile(r"^\s*-\s+\[(x|X)\]")


def to_float(value):
    try:
        return float(str(value).strip().split()[0])
    except (ValueError, IndexError, AttributeError):
        return None


def phases_done(state_path):
    """(completed, total) demand phases from the state checklist."""
    text = Path(state_path).read_text(encoding="utf-8-sig") if Path(state_path).exists() else ""
    checklist = [ln for ln in text.splitlines() if re.match(r"^\s*-\s+\[[xX ]\]", ln)]
    done = sum(1 for ln in checklist if CHECK_RE.match(ln))
    return done, (len(checklist) or 5)


def evaluate(state_path):
    fields = read_state_fields(state_path)
    limit = to_float(fields.get("budget limit", ""))
    consumed = to_float(fields.get("demand acu", fields.get("budget consumed", "")))
    near = to_float(fields.get("budget near threshold", "")) or 80.0
    on_limit = fields.get("budget on limit", "pause-and-ask") or "pause-and-ask"
    unit = fields.get("budget unit", "acu") or "acu"
    done, total = phases_done(state_path)

    if limit is None:
        return {"status": "no-budget", "reason": "no `budget limit` set for this demand",
                "delivered_phases": f"{done}/{total}"}
    if consumed is None:
        return {"status": "unmeasurable",
                "reason": "no `demand acu`; run /usage then session-cost.py first",
                "budget_limit": limit, "delivered_phases": f"{done}/{total}"}

    pct = round(consumed / limit * 100, 1) if limit else None
    if pct is None:
        status = "unmeasurable"
    elif pct >= 100:
        status = "exceeded"
    elif pct >= near:
        status = "near"
    else:
        status = "within"

    return {
        "status": status,
        "unit": unit,
        "budget_limit": limit,
        "consumed": consumed,
        "remaining": round(limit - consumed, 2),
        "pct": pct,
        "near_threshold": near,
        "on_limit": on_limit,
        "delivered_phases": f"{done}/{total}",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", "-StatePath", dest="state_path", required=True)
    parser.add_argument("--json", dest="as_json", action="store_true")
    args = parser.parse_args()

    result = evaluate(args.state_path)
    if "pct" in result:
        write_state_fields(args.state_path, {"budget status": result["status"],
                                             "budget consumed": result["consumed"]},
                           section="Budget")

    if args.as_json:
        print(json.dumps(result))
    elif result["status"] in ("no-budget", "unmeasurable"):
        print(f"{result['status']}: {result.get('reason', '')} (entregue {result['delivered_phases']})")
    else:
        print(f"Orcamento: {result['consumed']}/{result['budget_limit']} {result['unit']} "
              f"({result['pct']}%) · {result['status']} · entregue fases {result['delivered_phases']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
