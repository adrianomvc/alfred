import re
from pathlib import Path

from shared.common import read_state_fields
from shared.observability.application.use_cases.reconcile_usage_summary import ReconcileUsageSummary
from shared.observability.domain.models import SummaryKey
from shared.observability.domain.services.cost_calculator import CostResolver
from shared.observability.infrastructure.repositories.json_usage_summary_repository import (
    JsonUsageSummaryRepository,
    NoopUsageSummaryRepository,
)
from shared.observability.infrastructure.repositories.jsonl_event_repository import JsonlEventRepository
from shared.observability.infrastructure.system_clock import SystemClock
from shared.toolbar.state import ToolbarState


def numeric_cost_text(value):
    text = str(value or "").strip()
    if not text:
        return ""
    match = re.search(r"(\d+(?:[.,]\d+)?)", text)
    if not match:
        return ""
    return match.group(1).replace(",", ".")


def toolbar_state_fields(state_path, toolbar_state: ToolbarState, cost="n/a", cost_usd=""):
    state_fields = read_state_fields(Path(state_path).resolve())
    if cost_usd and not state_fields.get("cost usd"):
        state_fields["cost usd"] = cost_usd
    cost_value = numeric_cost_text(cost)
    if cost_value and not state_fields.get("cost usd"):
        state_fields["cost usd"] = cost_value
    if (cost_usd or cost_value) and not state_fields.get("cost source"):
        state_fields.setdefault("cost source", "manual")
        state_fields.setdefault("cost confidence", "manual")
        state_fields.setdefault("cost granularity", "session")
    if toolbar_state.usage_cost:
        state_fields.setdefault("usage-cost", toolbar_state.usage_cost)
    return state_fields


def build_toolbar_summary(state_path, toolbar_state: ToolbarState, cost="n/a", cost_usd="", write_usage_summary=False):
    state = Path(state_path).resolve()
    state_fields = toolbar_state_fields(state, toolbar_state, cost, cost_usd)
    obs_log = state.parent / "05-operation" / "011-observability-log.jsonl"
    summary_repository = (
        JsonUsageSummaryRepository()
        if write_usage_summary and obs_log.exists()
        else NoopUsageSummaryRepository()
    )
    return ReconcileUsageSummary(
        JsonlEventRepository(obs_log),
        summary_repository,
        CostResolver(),
        SystemClock(),
    ).execute(SummaryKey(str(state)), state_fields)
