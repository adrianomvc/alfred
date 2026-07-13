from collections.abc import Mapping
from dataclasses import dataclass
from typing import Callable


ArtifactBuilder = Callable[..., dict[str, object]]
Clock = Callable[[], str]


def _value_or(value, fallback):
    if value is None:
        return fallback
    if isinstance(value, str) and not value.strip():
        return fallback
    return value


@dataclass(frozen=True)
class ImportCcusageSessionCommand:
    row: Mapping[str, object]
    state_fields: Mapping[str, str]
    selection_method: str
    source_path: str
    run_id: str
    phase: str
    host: str
    model: str
    last_activity: str


@dataclass(frozen=True)
class ImportCcusageSessionResult:
    snapshot: dict[str, object]
    state_updates: dict[str, str]


class ImportCcusageSession:
    def __init__(self, *, artifact_builder: ArtifactBuilder, now: Clock) -> None:
        self._artifact_builder = artifact_builder
        self._now = now

    def execute(self, command: ImportCcusageSessionCommand) -> ImportCcusageSessionResult:
        ts = _value_or(command.last_activity, self._now())
        snapshot = self._make_snapshot(command, ts)
        updates = self._make_state_updates(command)
        return ImportCcusageSessionResult(snapshot=snapshot, state_updates=updates)

    def _make_snapshot(self, command: ImportCcusageSessionCommand, ts: str) -> dict[str, object]:
        row = command.row
        state_fields = command.state_fields
        total_cost = row.get("totalCost")
        event_id = f"usage-ccusage-{row.get('period', 'session')}"
        metadata = row.get("metadata") or {}

        return {
            "schema_version": "alfred.usage-session.v1",
            "alfred": {
                "version": _value_or(state_fields.get("framework version"), "unknown"),
                "framework_ref": _value_or(state_fields.get("framework ref"), "local"),
                "framework_commit": _value_or(state_fields.get("framework commit"), None),
                "schema_version": "alfred.usage-session.v1",
            },
            "ts": ts,
            "snapshot_id": event_id,
            "trace_id": _value_or(state_fields.get("alfred run id"), _value_or(command.run_id, "unknown")),
            "session_id": _value_or(row.get("period"), "unknown"),
            "interaction_id": "unknown",
            "sequence": 1,
            "initiative_id": _value_or(state_fields.get("initiative id"), "unknown"),
            "demand_id": _value_or(state_fields.get("id"), "unknown"),
            "record_type": "session_usage_snapshot",
            "phase": _value_or(command.phase, _value_or(state_fields.get("current phase"), "operation")),
            "lane": _value_or(state_fields.get("lane"), _value_or(state_fields.get("modo"), "unknown")),
            "actor_type": "system",
            "actor_id": "usage-cost-ccusage",
            "action": "capture_session_usage",
            "status": "recorded",
            "step": {
                "id": "usage-cost",
                "name": "Usage and cost attribution",
                "sequence": 1,
                "goal": "Import ccusage session usage into Alfred state for toolbar display",
            },
            "artifacts_used": [
                self._artifact_builder(
                    command.source_path,
                    "read",
                    selection_reason="source_usage_export",
                    observed_by="usage-cost-ccusage",
                    ts=ts,
                )
            ],
            "duration_ms": None,
            "tokens_input": row.get("inputTokens"),
            "tokens_output": row.get("outputTokens"),
            "cost_usd": total_cost,
            "retry_count": None,
            "input": {
                "source": "ccusage",
                "source_kind": "ccusage",
                "selection_method": command.selection_method,
                "agent": row.get("agent"),
                "last_activity": metadata.get("lastActivity") if isinstance(metadata, Mapping) else None,
            },
            "derivation": {
                "rules_applied": ["connectors/usage-cost.md", "metrics/metrics.md"],
                "method": "ccusage session JSON import; session total only, not an interaction observability event",
            },
            "output": {
                "model": command.model,
                "tokens_input": row.get("inputTokens"),
                "tokens_output": row.get("outputTokens"),
                "tokens_cache_creation": row.get("cacheCreationTokens"),
                "tokens_cache_read": row.get("cacheReadTokens"),
                "total_tokens": row.get("totalTokens"),
                "cost_usd": total_cost,
                "cost_confidence": "estimated",
            },
            "model": command.model,
            "tool": "scripts/metrics/import-ccusage.py",
            "parent_event_id": None,
            "artifacts": [],
            "files_changed": [],
            "validation": {
                "source_record_parse": "ok",
                "selection_method": command.selection_method,
            },
            "risk": None,
            "blocker": None,
            "error": None,
            "state_transition": None,
            "actions": [{"type": "import_ccusage_session_total", "status": "completed"}],
            "questions_open": [],
            "assumptions": [],
            "metric_impact": {"session_cost_state": "captured"},
            "next": [],
            "metadata": {
                "connector_type": "usage-cost",
                "source_kind": "ccusage",
                "agent": row.get("agent"),
                "granularity": "session",
            },
        }

    def _make_state_updates(self, command: ImportCcusageSessionCommand) -> dict[str, str]:
        updates = {
            "usage-cost": "ccusage automatic",
            "cost source": "ccusage",
            "cost usd": str(command.row.get("totalCost")),
            "cost confidence": "estimated",
            "cost granularity": "session",
            "host": command.host,
            "usage session id": str(command.row.get("period")),
            "usage imported at": self._now(),
        }
        if command.run_id:
            updates["alfred run id"] = command.run_id
        return updates
