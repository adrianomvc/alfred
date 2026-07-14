#!/usr/bin/env python3
"""Validate observability event hygiene (Layer 0).

Guards the rule that makes usage attribution possible: every example event must
carry a real, parseable ISO-8601 ``ts`` — never a placeholder — and a demand log
with more than one event must not stamp them all with an identical timestamp
(the placeholder pattern that breaks window/turn attribution). Also checks that
the hygiene contract text stays wired into the rules.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.common import find_observability_logs, iter_jsonl  # noqa: E402
from shared.validation import Severity, ValidationIssue, ValidationReport  # noqa: E402


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
    issues = []
    timestamps = []
    seen_lines = {}  # event_id -> set of exact compact signatures already logged
    for line_number, event, _ in iter_jsonl(path):
        if event is None:
            issues.append(issue(
                "observability_hygiene.invalid_json",
                f"{path.as_posix()}:{line_number} invalid JSON",
                path,
                line_number,
            ))
            continue
        # Append-once: an event_id may only reappear when its content changed
        # (e.g. an interaction_completed whose request set grew; read-time dedup
        # keeps the latest). An exact repeat is pure noise -- the duplication
        # that idempotent emission removes.
        event_id = event.get("event_id")
        if event_id:
            signature = json.dumps(event, sort_keys=True, separators=(",", ":"))
            prior = seen_lines.setdefault(event_id, set())
            if signature in prior:
                issues.append(issue(
                    "observability_hygiene.duplicate_event",
                    f"{path.as_posix()}:{line_number} exact-duplicate event_id {event_id!r}; log must be append-once",
                    path,
                    line_number,
                ))
            prior.add(signature)
        ts = event.get("ts")
        if not parseable_iso(ts):
            issues.append(issue(
                "observability_hygiene.invalid_ts",
                f"{path.as_posix()}:{line_number} placeholder or unparseable ts: {ts!r}",
                path,
                line_number,
            ))
        else:
            timestamps.append(ts)
        artifacts_used = event.get("artifacts_used")
        if artifacts_used is not None and not isinstance(artifacts_used, list):
            issues.append(issue(
                "observability_hygiene.artifacts_used_not_list",
                f"{path.as_posix()}:{line_number} artifacts_used must be a canonical list",
                path,
                line_number,
            ))
        if isinstance(artifacts_used, list):
            for index, item in enumerate(artifacts_used, start=1):
                if not isinstance(item, dict):
                    issues.append(issue(
                        "observability_hygiene.artifact_not_object",
                        f"{path.as_posix()}:{line_number} artifacts_used[{index}] must be an object",
                        path,
                        line_number,
                    ))
                    continue
                for key in ("artifact_type", "operation", "observed_by"):
                    if key not in item:
                        issues.append(issue(
                            "observability_hygiene.artifact_key_missing",
                            f"{path.as_posix()}:{line_number} artifacts_used[{index}] missing {key}",
                            path,
                            line_number,
                        ))
        if event.get("event_type") == "usage_attributed" and event.get("event_scope") == "request":
            if not event.get("request_id"):
                issues.append(issue(
                    "observability_hygiene.request_id_missing",
                    f"{path.as_posix()}:{line_number} request usage must include request_id",
                    path,
                    line_number,
                ))
            if event.get("cost_usd") is not None:
                issues.append(issue(
                    "observability_hygiene.request_cost_inline",
                    f"{path.as_posix()}:{line_number} request usage must not carry interaction cost",
                    path,
                    line_number,
                ))
        if event.get("event_type") == "usage_cost_attributed":
            if not event.get("parent_event_id"):
                issues.append(issue(
                    "observability_hygiene.parent_event_missing",
                    f"{path.as_posix()}:{line_number} usage_cost_attributed must include parent_event_id",
                    path,
                    line_number,
                ))
            if event.get("cost_usd") is None:
                issues.append(issue(
                    "observability_hygiene.cost_missing",
                    f"{path.as_posix()}:{line_number} usage_cost_attributed must include observed/derived cost",
                    path,
                    line_number,
                ))
        if event.get("duration_ms") == 0:
            issues.append(issue(
                "observability_hygiene.duration_zero",
                f"{path.as_posix()}:{line_number} duration_ms=0 requires observed duration; use null when unknown",
                path,
                line_number,
            ))
    if require_distinct_timestamps and len(timestamps) > 1 and len(set(timestamps)) == 1:
        issues.append(issue(
            "observability_hygiene.same_timestamp",
            f"{path.as_posix()} all {len(timestamps)} events share one ts "
            f"({timestamps[0]!r}); stamp real per-event timestamps",
            path,
        ))
    return issues


def issue(code, message, path=None, line=None):
    return ValidationIssue(
        code=code,
        severity=Severity.ERROR,
        message=message,
        path=None if path is None else str(path),
        line=line,
    )


def require_text(path, needle, errors):
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if needle not in text:
        errors.append(issue(
            "observability_hygiene.wiring_missing",
            f"Missing hygiene wiring in {path.as_posix()}: {needle}",
            path,
        ))


def validate_observability_hygiene(root) -> tuple[ValidationReport, int]:
    root = Path(root).resolve()
    issues = []
    logs = find_observability_logs(root / "examples")
    for log in logs:
        issues.extend(check_log(log))
    for rel in (
        "examples/connectors/usage-attribution-events.jsonl",
        "examples/connectors/usage-attribution-tokens-only.jsonl",
    ):
        path = root / rel
        if path.exists():
            issues.extend(check_log(path, require_distinct_timestamps=False))

    require_text(root / "metrics/metrics.md", "Event hygiene", issues)
    require_text(root / "metrics/metrics.md", "Refresh session totals at checkpoints", issues)
    require_text(root / "metrics/metrics.md", "interaction/request-granular sources", issues)
    require_text(root / "metrics/metrics.md", "usage_cost_attributed", issues)
    require_text(root / "metrics/metrics.md", "approved rate card", issues)
    require_text(root / "metrics/metrics.md", "No double counting", issues)
    require_text(root / "metrics/metrics.md", "cache_reuse_ratio", issues)
    require_text(root / "rules/common/session-continuity.md", "real ISO-8601", issues)
    return ValidationReport(tuple(issues)), len(logs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    report, log_count = validate_observability_hygiene(args.root)
    if not report.passed:
        for item in report.issues:
            print(f"ERROR {item.message}", file=sys.stderr)
        raise SystemExit(f"Observability hygiene validation failed: {len(report.issues)} error(s)")

    print(f"OK observability hygiene: {log_count} example log(s) checked")
    print("Observability hygiene validation completed.")


if __name__ == "__main__":
    main()
