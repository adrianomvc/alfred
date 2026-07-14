import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

from shared.toolbar.state import get_first_field


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def active_demand_path(env: Mapping[str, str] | None = None) -> Path:
    values = env if env is not None else os.environ
    runtime_dir = values.get("ALFRED_RUNTIME_DIR")
    base = Path(runtime_dir).expanduser() if runtime_dir else Path.home() / ".alfred" / "runtime"
    return base / "active-demand.json"


def active_demand_payload(state_path, content: Sequence[str], env: Mapping[str, str] | None = None):
    values = env if env is not None else os.environ
    state = Path(state_path).resolve()
    obs_log = state.parent / "05-operation" / "011-observability-log.jsonl"
    return {
        "schema_version": "alfred.runtime.active-demand.v1",
        "updated_at": now_iso(),
        "state_path": str(state),
        "observability_log": str(obs_log),
        "alfred_run_id": get_first_field(content, ["alfred run id", "trace id"]),
        "initiative_id": get_first_field(content, ["initiative id", "id iniciativa"]),
        "demand_id": get_first_field(content, ["id", "demand id"]),
        "host": values.get("ALFRED_HOST", ""),
    }


def register_active_demand(state_path, content: Sequence[str], env: Mapping[str, str] | None = None):
    target = active_demand_path(env)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = active_demand_payload(state_path, content, env)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target
