#!/usr/bin/env python3
"""Normalize a pasted Devin ``/usage`` reading into ``alfred.usage.v2`` state."""

import argparse
import math
import re
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.common import read_state_fields, write_state_fields  # noqa: E402
from shared.observability.infrastructure.rate_cards.json_rate_card_repository import (  # noqa: E402
    load_approved_acu_usd_rate,
)

NUMBER = r"(?:\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)"
ACU_RE = re.compile(rf"ACUs?\s+consumed\s*:\s*({NUMBER})\s+of\s+({NUMBER})", re.IGNORECASE)
QUOTA_RES = (
    re.compile(rf"Quota\s+used\s*:\s*({NUMBER})\s*%", re.IGNORECASE),
    re.compile(rf"({NUMBER})\s*%\s*used", re.IGNORECASE),
)
VALID_UNITS = {"acu", "quota_percent", "usd", "tokens"}


def parse_number(raw):
    """Parse common decimal formats and reject a lone ambiguous thousands group."""
    value = str(raw).strip()
    if not value or not re.fullmatch(NUMBER, value):
        raise ValueError(f"invalid numeric value: {raw!r}")
    if "," in value and "." in value:
        decimal = "," if value.rfind(",") > value.rfind(".") else "."
        thousands = "." if decimal == "," else ","
        value = value.replace(thousands, "").replace(decimal, ".")
    elif "," in value:
        if value.count(",") == 1 and len(value.split(",")[1]) == 3:
            raise ValueError(f"ambiguous numeric value: {raw!r}")
        value = value.replace(".", "").replace(",", ".")
    elif value.count(".") > 1:
        groups = value.split(".")
        value = "".join(groups[:-1]) + "." + groups[-1]
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite numeric value: {raw!r}")
    return number


def parse_usage(text):
    """Return ``(unit, current, limit)`` for documented Devin usage formats."""
    if not text:
        return None
    acu = ACU_RE.search(text)
    if acu:
        try:
            return "acu", parse_number(acu.group(1)), parse_number(acu.group(2))
        except ValueError:
            return None
    for pattern in QUOTA_RES:
        quota = pattern.search(text)
        if quota:
            try:
                return "quota_percent", parse_number(quota.group(1)), 100.0
            except ValueError:
                return None
    return None


def to_float(value):
    try:
        number = float(str(value).strip().split()[0])
        return number if math.isfinite(number) else None
    except (ValueError, IndexError, AttributeError):
        return None


def _baseline(fields, scope):
    return to_float(fields.get(f"usage {scope} baseline", fields.get(f"usage acu {scope} baseline", "")))


def build_result(fields, parsed, rate_card_path=None, observed_at=None, cycle_reset_at=None):
    unit, current, limit = parsed
    observed_at = observed_at or datetime.now(timezone.utc).isoformat()
    available_pct = round((limit - current) / limit * 100, 1) if limit and current <= limit else None
    previous_reset = fields.get("usage cycle reset at", "")
    reset_changed = bool(cycle_reset_at and previous_reset and cycle_reset_at != previous_reset)

    deltas = {}
    reset_detected = reset_changed
    for scope in ("session", "demand"):
        baseline = _baseline(fields, scope)
        if baseline is None:
            deltas[scope] = None
        elif current < baseline or reset_changed:
            deltas[scope] = None
            reset_detected = True
        else:
            deltas[scope] = round(current - baseline, 2)

    result = {
        "schema": "alfred.usage.v2", "unit": unit, "current": current, "limit": limit,
        "available_pct": available_pct, "session": deltas["session"], "demand": deltas["demand"],
        "observed_at": observed_at, "cycle_reset_at": cycle_reset_at,
        "reset_detected": reset_detected, "confidence": "estimated", "source": "host_usage_command",
    }
    rate = load_approved_acu_usd_rate(rate_card_path, observed_at) if unit == "acu" else None
    if rate is not None:
        result["usd_per_acu"] = rate
        for scope in ("session", "demand"):
            if deltas[scope] is not None:
                result[f"{scope}_usd"] = round(deltas[scope] * rate, 4)

    budget_unit = (fields.get("budget unit", "") or "acu").strip().lower()
    budget_limit = to_float(fields.get("budget limit", ""))
    budget_value = result.get("demand_usd") if budget_unit == "usd" else result["demand"] if budget_unit == unit else None
    if budget_limit and budget_limit > 0 and budget_value is not None:
        result.update(budget_unit=budget_unit, budget_limit=budget_limit,
                      budget_pct=round(budget_value / budget_limit * 100, 1))
    return result


def display_text(result):
    labels = {"acu": "ACU", "quota_percent": "quota %", "usd": "USD", "tokens": "tokens"}
    parts = [f"{result['current']}/{result['limit']} {labels[result['unit']]}" ]
    if result.get("available_pct") is not None:
        parts.append(f"{result['available_pct']}% disp")
    if result.get("demand") is not None:
        demand = f"demanda {result['demand']}"
        if "budget_pct" in result:
            demand += f" ({result['budget_pct']}% orc)"
        parts.append(demand)
    elif result.get("reset_detected"):
        parts.append("novo ciclo · redefina o baseline")
    return " · ".join(parts)


def state_updates(result, set_baseline, scope):
    updates = {
        "usage schema": result["schema"], "usage unit": result["unit"],
        "usage current": result["current"], "usage limit": result["limit"],
        "usage source": result["source"], "usage confidence": result["confidence"],
        "usage observed at": result["observed_at"], "cost source": result["source"],
        "cost confidence": result["confidence"],
    }
    if result.get("cycle_reset_at"):
        updates["usage cycle reset at"] = result["cycle_reset_at"]
    if set_baseline:
        updates[f"usage {scope} baseline"] = result["current"]
    if result.get("demand") is not None:
        updates["usage demand consumed"] = result["demand"]
    if "demand_usd" in result:
        updates["cost usd"] = result["demand_usd"]
        updates["cost granularity"] = "demand"
    return updates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", "-StatePath", dest="state_path", required=True)
    parser.add_argument("--usage-text", "-UsageText", dest="usage_text", default="")
    parser.add_argument("--scope", choices=["session", "demand"], default="demand")
    parser.add_argument("--set-baseline", "-SetBaseline", action="store_true", dest="set_baseline")
    parser.add_argument("--rate-card", "-RateCard", dest="rate_card", default="")
    parser.add_argument("--observed-at", dest="observed_at", default="")
    parser.add_argument("--cycle-reset-at", dest="cycle_reset_at", default="")
    parser.add_argument("--json", dest="as_json", action="store_true")
    args = parser.parse_args()
    parsed = parse_usage(args.usage_text)
    if parsed is None:
        out = {"status": "unmeasurable", "reason": "no unambiguous /usage reading; run /usage and paste its complete output"}
        print(json.dumps(out) if args.as_json else f"unmeasurable: {out['reason']}")
        return 0
    state_path = Path(args.state_path)
    result = build_result(read_state_fields(state_path), parsed, args.rate_card,
                          args.observed_at or None, args.cycle_reset_at or None)
    write_state_fields(state_path, state_updates(result, args.set_baseline, args.scope))
    print(json.dumps(result) if args.as_json else display_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
