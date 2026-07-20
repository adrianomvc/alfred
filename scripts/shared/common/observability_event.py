"""Canonical alfred.observability.v1 lifecycle events for CLI writers."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from uuid import uuid4

OBSERVABILITY_SCHEMA = "alfred.observability.v1"


def lifecycle_event(fields, stamp, event_type, action, step="", artifacts=None, extra=None):
    """Build a v1 lifecycle event from parsed state ``fields`` (metrics/metrics.md)."""
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    event = {
        "schema_version": OBSERVABILITY_SCHEMA,
        "alfred": stamp,
        "ts": now,
        "event_id": f"evt-cli-{uuid4().hex[:12]}",
        "trace_id": f"demand-{fields.get('id', '')}",
        "session_id": os.environ.get("ALFRED_SESSION_ID", "alfred-cli"),
        "interaction_id": None,
        "sequence": None,  # stamped by append_event from the target log
        "initiative_id": fields.get("initiative id", ""),
        "demand_id": fields.get("id", ""),
        "event_type": event_type,
        "event_scope": "step",
        "phase": fields.get("current phase", ""),
        "lane": fields.get("lane", ""),
        "actor_type": "cli",
        "actor_id": "alfred-cli",
        "agent": "alfred-cli",
        "action": action,
        "status": fields.get("status", ""),
        "step": step or fields.get("current step", ""),
        "artifacts_used": [
            {"path": path, "artifact_type": "demand_artifact", "operation": "update",
             "observed_by": "alfred_cli"}
            for path in (artifacts or ["001-state.md"])
        ],
    }
    if extra:
        event.update(extra)
    return event


def append_event(log_path, event):
    """Append one event to a JSONL log, stamping its per-log sequence."""
    log = Path(log_path)
    sequence = 1
    if log.exists():
        sequence = sum(1 for line in log.read_text(encoding="utf-8-sig").splitlines()
                       if line.strip()) + 1
    event["sequence"] = sequence
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event
