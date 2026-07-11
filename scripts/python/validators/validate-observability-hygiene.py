#!/usr/bin/env python3
"""Validate observability event hygiene (Layer 0).

Guards the rule that makes usage attribution possible: every example event must
carry a real, parseable ISO-8601 ``ts`` — never a placeholder — and a demand log
with more than one event must not stamp them all with an identical timestamp
(the placeholder pattern that breaks window/turn attribution). Also checks that
the hygiene contract text stays wired into the rules.
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import find_observability_logs, iter_jsonl  # noqa: E402


def parseable_iso(value):
    if not isinstance(value, str) or not value.strip():
        return False
    if "<" in value or ">" in value:
        return False
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        datetime.fromisoformat(text)
    except ValueError:
        return False
    return True


def check_log(path):
    errors = []
    timestamps = []
    for line_number, event, _ in iter_jsonl(path):
        if event is None:
            errors.append(f"{path.as_posix()}:{line_number} invalid JSON")
            continue
        ts = event.get("ts")
        if not parseable_iso(ts):
            errors.append(
                f"{path.as_posix()}:{line_number} placeholder or unparseable ts: {ts!r}"
            )
        else:
            timestamps.append(ts)
    if len(timestamps) > 1 and len(set(timestamps)) == 1:
        errors.append(
            f"{path.as_posix()} all {len(timestamps)} events share one ts "
            f"({timestamps[0]!r}); stamp real per-event timestamps"
        )
    return errors


def require_text(path, needle, errors):
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if needle not in text:
        errors.append(f"Missing hygiene wiring in {path.as_posix()}: {needle}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    errors = []
    logs = find_observability_logs(root / "examples")
    for log in logs:
        errors.extend(check_log(log))

    require_text(root / "metrics/metrics.md", "Event hygiene", errors)
    require_text(root / "metrics/metrics.md", "Refresh session totals at checkpoints", errors)
    require_text(root / "metrics/metrics.md", "interaction/request-granular sources", errors)
    require_text(root / "rules/common/session-continuity.md", "real ISO-8601", errors)

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(f"Observability hygiene validation failed: {len(errors)} error(s)")

    print(f"OK observability hygiene: {len(logs)} example log(s) checked")
    print("Observability hygiene validation completed.")


if __name__ == "__main__":
    main()
