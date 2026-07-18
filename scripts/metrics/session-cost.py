#!/usr/bin/env python3
"""Compute session/demand cost from a pasted DEVIN CLI `/usage` reading.

The DEVIN CLI does not expose ACU/token usage to scripts, and the agent cannot
run `/usage` itself, so this is a **calculator**, not an autonomous reader: a
human runs `/usage`, pastes the text, and this computes the session and demand
consumption as a delta from baselines stored in the demand `state`, for the
toolbar and the budget monitor.

`/usage` reports plan-dependent units:
- paid: `ACUs consumed: 129.42 of 180.00` (cumulative for the billing cycle);
- self-serve/Free: `Quota used: 98% (remaining: 2%)`.

Cost in USD is only produced when an approved rate card supplies `acu.usd_per_acu`
(Devin publishes no ACU->USD rate; never invent one — D10). With no `/usage` text
and no rate card, the result is `unmeasurable` and nothing is written.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.common import read_state_fields, write_state_fields  # noqa: E402

ACU_RE = re.compile(r"([\d.]+)\s+of\s+([\d.]+)")
# Quota appears as "Quota used: 98%" or "98% used"; capture the *used* percent,
# not the "remaining" one.
QUOTA_RES = (
    re.compile(r"used:?\s*(\d+(?:\.\d+)?)\s*%", re.IGNORECASE),
    re.compile(r"(\d+(?:\.\d+)?)\s*%\s*used", re.IGNORECASE),
)


def parse_usage(text):
    """Return (unit, consumed, total) from a `/usage` string, or None."""
    if not text:
        return None
    acu = ACU_RE.search(text)
    if acu:
        return ("acu", float(acu.group(1)), float(acu.group(2)))
    for pattern in QUOTA_RES:
        quota = pattern.search(text)
        if quota:
            return ("quota-%", float(quota.group(1)), 100.0)
    return None


def to_float(value):
    try:
        return float(str(value).strip().split()[0])
    except (ValueError, IndexError, AttributeError):
        return None


def usd_per_acu(rate_card_path):
    if not rate_card_path:
        return None
    try:
        data = json.loads(Path(rate_card_path).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    acu = data.get("acu") or {}
    return acu.get("usd_per_acu")


def build_result(fields, parsed, rate_card_path):
    unit, consumed, total = parsed
    available_pct = round((total - consumed) / total * 100, 1) if total else None

    session_base = to_float(fields.get("usage acu session baseline", ""))
    demand_base = to_float(fields.get("usage acu demand baseline", ""))
    session_acu = round(consumed - session_base, 2) if session_base is not None else None
    demand_acu = round(consumed - demand_base, 2) if demand_base is not None else None

    result = {
        "unit": unit,
        "cycle_consumed": consumed,
        "cycle_total": total,
        "available_pct": available_pct,
        "session": session_acu,
        "demand": demand_acu,
        "confidence": "estimated",
        "source": "host_usage_command",
    }

    rate = usd_per_acu(rate_card_path) if unit == "acu" else None
    if rate is not None:
        result["usd_per_acu"] = rate
        if demand_acu is not None:
            result["demand_usd"] = round(demand_acu * rate, 4)
        if session_acu is not None:
            result["session_usd"] = round(session_acu * rate, 4)

    limit = to_float(fields.get("budget limit", ""))
    if limit and demand_acu is not None:
        result["budget_limit"] = limit
        result["budget_pct"] = round(demand_acu / limit * 100, 1)
    return result


def state_updates(result, set_baseline, scope):
    updates = {
        "usage acu cycle": f"{result['cycle_consumed']}/{result['cycle_total']}",
        "usage acu total": result["cycle_total"],
        "cost source": result["source"],
        "cost confidence": result["confidence"],
    }
    if set_baseline:
        updates[f"usage acu {scope} baseline"] = result["cycle_consumed"]
    if result.get("session") is not None:
        updates["session acu"] = result["session"]
    if result.get("demand") is not None:
        updates["demand acu"] = result["demand"]
    if "demand_usd" in result:
        updates["cost usd"] = result["demand_usd"]
    return updates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", "-StatePath", dest="state_path", required=True)
    parser.add_argument("--usage-text", "-UsageText", dest="usage_text", default="")
    parser.add_argument("--scope", choices=["session", "demand"], default="demand")
    parser.add_argument("--set-baseline", "-SetBaseline", dest="set_baseline", action="store_true")
    parser.add_argument("--rate-card", "-RateCard", dest="rate_card", default="")
    parser.add_argument("--json", dest="as_json", action="store_true")
    args = parser.parse_args()

    state_path = Path(args.state_path)
    parsed = parse_usage(args.usage_text)
    if parsed is None:
        out = {"status": "unmeasurable",
               "reason": "no parseable /usage text; run `/usage` in the DEVIN CLI and pass --usage-text"}
        print(json.dumps(out) if args.as_json else f"unmeasurable: {out['reason']}")
        return 0

    fields = read_state_fields(state_path)
    result = build_result(fields, parsed, args.rate_card)
    write_state_fields(state_path, state_updates(result, args.set_baseline, args.scope))

    if args.as_json:
        print(json.dumps(result))
    else:
        avail = f"{result['available_pct']}% disponivel" if result["available_pct"] is not None else "n/a"
        line = f"Ciclo: {result['cycle_consumed']}/{result['cycle_total']} {result['unit']} - {avail}"
        if result.get("session") is not None:
            line += f" | Sessao: {result['session']}"
        if result.get("demand") is not None:
            line += f" | Demanda: {result['demand']}"
            if "budget_pct" in result:
                line += f" ({result['budget_pct']}% do orcamento)"
        if "demand_usd" in result:
            line += f" | ~US$ {result['demand_usd']} (estimado)"
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
