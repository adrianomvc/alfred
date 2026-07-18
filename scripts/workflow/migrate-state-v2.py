#!/usr/bin/env python3
"""Migrate legacy ACU state fields to ``alfred.usage.v2``."""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

LEGACY = {
    "usage acu cycle", "usage acu total", "usage acu display",
    "usage acu session baseline", "usage acu demand baseline", "session acu", "demand acu",
}


def fields(lines):
    result = {}
    for line in lines:
        match = re.match(r"^\s*-\s+([^:]+):\s*(.*)$", line)
        if match:
            result[match.group(1).strip().lower()] = match.group(2).strip()
    return result


def migrate_content(content, forced_unit=None):
    lines = content.splitlines()
    current = fields(lines)
    present = LEGACY.intersection(current)
    if not present:
        return content if content.endswith("\n") else content + "\n", [], []
    unit = forced_unit
    cycle = current.get("usage acu cycle", "")
    cycle_values = cycle.split("/", 1) if "/" in cycle else []
    try:
        ambiguous_hundred = len(cycle_values) == 2 and float(cycle_values[1].strip()) == 100.0
    except ValueError:
        ambiguous_hundred = False
    if unit is None and ambiguous_hundred:
        return content if content.endswith("\n") else content + "\n", [], [
            "legacy cycle limit is 100; pass --unit acu or --unit quota_percent"
        ]
    unit = unit or "acu"
    updates = {"usage schema": "alfred.usage.v2", "usage unit": unit}
    mapping = {
        "usage acu total": "usage limit", "usage acu session baseline": "usage session baseline",
        "usage acu demand baseline": "usage demand baseline", "session acu": "usage session consumed",
        "demand acu": "usage demand consumed",
    }
    for old, new in mapping.items():
        if current.get(old):
            updates[new] = current[old]
    if len(cycle_values) == 2:
        updates["usage current"] = cycle_values[0].strip()
        updates.setdefault("usage limit", cycle_values[1].strip())

    output = []
    inserted = False
    for line in lines:
        match = re.match(r"^(\s*-\s+)([^:]+):(.*)$", line)
        key = match.group(2).strip().lower() if match else ""
        if key in LEGACY:
            if not inserted:
                output.extend(f"- {name}: {value}" for name, value in updates.items())
                inserted = True
            continue
        if key in updates:
            if not inserted:
                output.extend(f"- {name}: {value}" for name, value in updates.items())
                inserted = True
            continue
        output.append(line)
    if not inserted:
        output.extend(f"- {name}: {value}" for name, value in updates.items())
    return "\n".join(output) + "\n", sorted(present), []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", required=True)
    parser.add_argument("--unit", choices=["acu", "quota_percent"])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    path = Path(args.state_path)
    original = path.read_text(encoding="utf-8-sig")
    migrated, legacy, errors = migrate_content(original, args.unit)
    result = {"state_path": str(path), "legacy_fields": legacy, "errors": errors,
              "changed": migrated != original}
    if errors:
        print(json.dumps(result) if args.as_json else "ERROR " + "; ".join(errors))
        return 2
    if result["changed"]:
        result["diff"] = "\n".join(difflib.unified_diff(
            original.splitlines(), migrated.splitlines(), fromfile=str(path), tofile=str(path) + " (v2)", lineterm=""))
        if args.write:
            path.write_text(migrated, encoding="utf-8", newline="\n")
    if args.as_json:
        print(json.dumps(result))
    elif result.get("diff"):
        print(result["diff"])
    else:
        print("OK state already uses alfred.usage.v2")
    return 1 if args.check and result["changed"] else 0


if __name__ == "__main__":
    sys.exit(main())
