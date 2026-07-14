import re
from dataclasses import dataclass
from typing import Sequence

from shared.common.markdown_fields import get_field


DEFAULT_PHASES = ("Inception", "Design", "Execution", "Validate", "Operation")
EXECUTION_FIRST_PHASES = (
    "Execution-first stabilization",
    "Inception posterior",
    "Design posterior",
    "Validate posterior",
    "Operation / post-mortem",
)


@dataclass(frozen=True)
class ToolbarState:
    demand_id: str
    sigla: str
    lane: str
    phase: str
    step: str
    next_step: str
    checkpoint: str
    model: str
    usage_cost: str
    state_cost_usd: str
    framework_version: str
    framework_commit: str
    app_commit: str
    phases: tuple[str, ...]
    markers: tuple[tuple[str, str], ...]
    progress: int


def get_first_field(lines: Sequence[str], names) -> str:
    return get_field(lines, names)


def get_checklist_status(lines: Sequence[str], phase: str) -> str:
    pattern = re.compile(r"^\s*-\s+\[(x|X| )\]\s+" + re.escape(phase) + r"\b")
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1)
    return " "


def parse_toolbar_state(content: Sequence[str]) -> ToolbarState:
    demand_id = get_field(content, "id") or "unknown"
    sigla = get_field(content, "sigla") or "unknown"
    lane = get_first_field(content, ["lane", "modo"]) or "unknown"
    phase = get_first_field(content, ["current phase", "fase atual"]) or "unknown"
    step = get_first_field(content, ["current step", "etapa atual"]) or "unknown"
    nxt = get_first_field(content, ["next step", "proximo passo", "próximo passo"]) or "unknown"
    checkpoint = get_field(content, "checkpoint") or "n/a"
    model = get_first_field(content, ["model", "current model", "modelo", "running model"])
    usage_cost = get_first_field(content, ["usage-cost", "usage cost", "custo", "cost"])
    state_cost_usd = get_first_field(content, ["cost usd", "cost_usd", "custo usd"])
    framework_version = get_first_field(content, ["framework version", "versao framework", "versão framework"])
    framework_commit = get_first_field(content, ["framework commit"])
    app_commit = get_first_field(content, ["app commit", "current app commit", "captured app commit"])
    phases = execution_phases(content, phase)
    markers, progress = progress_markers(content, phase, phases)
    return ToolbarState(
        demand_id=demand_id,
        sigla=sigla,
        lane=lane,
        phase=phase,
        step=step,
        next_step=nxt,
        checkpoint=checkpoint,
        model=model,
        usage_cost=usage_cost,
        state_cost_usd=state_cost_usd,
        framework_version=framework_version,
        framework_commit=framework_commit,
        app_commit=app_commit,
        phases=phases,
        markers=markers,
        progress=progress,
    )


def execution_phases(content: Sequence[str], phase: str) -> tuple[str, ...]:
    time_mode = get_first_field(content, ["tempo", "time mode"])
    checklist_text = "\n".join(
        line for line in content if re.match(r"^\s*-\s+\[[xX ]\]", line)
    )
    is_execution_first = (
        "execution-first" in phase.lower()
        or "execution-first" in time_mode.lower()
        or "execution-first stabilization" in checklist_text.lower()
    )
    return EXECUTION_FIRST_PHASES if is_execution_first else DEFAULT_PHASES


def progress_markers(content: Sequence[str], phase: str, phases: Sequence[str]) -> tuple[tuple[tuple[str, str], ...], int]:
    completed = 0
    markers = []
    for item in phases:
        status = get_checklist_status(content, item)
        if status in ("x", "X"):
            completed += 1
            marker = "x"
        elif item.lower() == phase.lower():
            marker = ">"
        else:
            marker = " "
        markers.append((item, marker))
    progress = min(100, round((completed / 5) * 100))
    return tuple(markers), progress
