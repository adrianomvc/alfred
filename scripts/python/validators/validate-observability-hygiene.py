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


def check_log(path, require_distinct_timestamps=True):
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
        artifacts_used = event.get("artifacts_used")
        if artifacts_used is not None and not isinstance(artifacts_used, list):
            errors.append(f"{path.as_posix()}:{line_number} artifacts_used must be a canonical list")
        if isinstance(artifacts_used, list):
            for index, item in enumerate(artifacts_used, start=1):
                if not isinstance(item, dict):
                    errors.append(f"{path.as_posix()}:{line_number} artifacts_used[{index}] must be an object")
                    continue
                for key in ("artifact_type", "operation", "observed_by"):
                    if key not in item:
                        errors.append(f"{path.as_posix()}:{line_number} artifacts_used[{index}] missing {key}")
        if event.get("event_type") == "usage_attributed" and event.get("event_scope") == "request":
            if not event.get("request_id"):
                errors.append(f"{path.as_posix()}:{line_number} request usage must include request_id")
            if event.get("cost_usd") is not None:
                errors.append(f"{path.as_posix()}:{line_number} request usage must not carry interaction cost")
        if event.get("event_type") == "usage_cost_attributed":
            if not event.get("parent_event_id"):
                errors.append(f"{path.as_posix()}:{line_number} usage_cost_attributed must include parent_event_id")
            if event.get("cost_usd") is None:
                errors.append(f"{path.as_posix()}:{line_number} usage_cost_attributed must include observed/derived cost")
        if event.get("duration_ms") == 0:
            errors.append(f"{path.as_posix()}:{line_number} duration_ms=0 requires observed duration; use null when unknown")
    if require_distinct_timestamps and len(timestamps) > 1 and len(set(timestamps)) == 1:
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
    for rel in (
        "examples/connectors/usage-attribution-events.jsonl",
        "examples/connectors/usage-attribution-tokens-only.jsonl",
    ):
        path = root / rel
        if path.exists():
            errors.extend(check_log(path, require_distinct_timestamps=False))

    require_text(root / "metrics/metrics.md", "Event hygiene", errors)
    require_text(root / "metrics/metrics.md", "Refresh session totals at checkpoints", errors)
    require_text(root / "metrics/metrics.md", "interaction/request-granular sources", errors)
    require_text(root / "metrics/metrics.md", "usage_cost_attributed", errors)
    require_text(root / "metrics/metrics.md", "approved rate card", errors)
    require_text(root / "metrics/metrics.md", "No double counting", errors)
    require_text(root / "metrics/metrics.md", "cache_reuse_ratio", errors)
    require_text(root / "rules/common/session-continuity.md", "real ISO-8601", errors)

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        raise SystemExit(f"Observability hygiene validation failed: {len(errors)} error(s)")

    print(f"OK observability hygiene: {len(logs)} example log(s) checked")
    print("Observability hygiene validation completed.")


if __name__ == "__main__":
    main()
