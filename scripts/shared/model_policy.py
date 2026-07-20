"""Model-policy resolver: turn a demand step into the tier/model/effort it must
run at.

Source of truth is ``core/model-policy.md`` (declared, versioned, human-readable).
This module mirrors that table so the runtime can *apply* the policy — resolve the
concrete model to show in the toolbar and to declare on a switch.
``validators/validate-model-policy.py`` checks that this mirror stays in sync with
the markdown, closing the gap between "policy written" and "policy applied".

Rule: final tier = max(floor(lane), adjustment(phase)), highest wins — except
Operate, the one documented floor exception, which may drop to ``medium`` even in
SAFE. Effort is the second, host-optional axis. Tier -> concrete model is
host-specific (Claude host default here); other hosts remap on adoption (D46).
"""

from dataclasses import dataclass

# Abstract tiers, lowest to highest.
TIERS = ("cheap", "medium", "strong")

# Floor per lane (risk) — never go below. model-policy.md "Floor per lane".
FLOOR_BY_LANE = {"fast": "cheap", "standard": "medium", "safe": "strong"}

# Claude host tier -> concrete model (owner default; configurable per host).
CLAUDE_TIER_MODEL = {
    "cheap": "claude-haiku-4-5",
    "medium": "claude-sonnet-5",
    "strong": "claude-opus-4-8",
}
# core/model-policy.md "DEVIN CLI concrete map". Without it every host resolved to
# a Claude model name, so a Devin session was told to target `claude-opus-4-8` —
# a model the DEVIN CLI cannot run.
DEVIN_TIER_MODEL = {
    "cheap": "swe-1-6-fast",
    "medium": "adaptive",
    "strong": "opus",
}
TIER_MODEL_BY_HOST = {
    "claude-code": CLAUDE_TIER_MODEL,
    "devin-cli": DEVIN_TIER_MODEL,
}

# Per-phase tier adjustment, already resolved by lane (model-policy.md
# "Adjustment per step"). Combined with the floor via max, except Operate.
PHASE_ADJUST = {
    "inception": {"fast": "strong", "standard": "medium", "safe": "strong"},
    "design": {"fast": "strong", "standard": "strong", "safe": "strong"},
    "execution": {"fast": "medium", "standard": "medium", "safe": "strong"},
    "validate": {"fast": "medium", "standard": "medium", "safe": "strong"},
    "operation": {"fast": "cheap", "standard": "medium", "safe": "medium"},
}

# Effort per step (model-policy.md "Effort per step"). Host-optional second axis.
EFFORT = {
    "inception": {"fast": "high", "standard": "high", "safe": "xhigh"},
    "design": {"fast": "high", "standard": "xhigh", "safe": "xhigh"},
    "execution": {"fast": "medium", "standard": "high", "safe": "xhigh"},
    "validate": {"fast": "medium", "standard": "high", "safe": "xhigh"},
    "operation": {"fast": "low", "standard": "low", "safe": "medium"},
}

# Execution task budget floor (model-policy.md "Task budget on Execution").
EXECUTION_TASK_BUDGET = 20000

_PHASE_ALIASES = {
    "operation": "operation",
    "operate": "operation",
    "operations": "operation",
    "operação": "operation",
    "operacao": "operation",
    "inception": "inception",
    "design": "design",
    "execution": "execution",
    "execucao": "execution",
    "execução": "execution",
    "validate": "validate",
    "validation": "validate",
    "validacao": "validate",
    "validação": "validate",
}

_LANE_ALIASES = {"fast": "fast", "standard": "standard", "padrão": "standard", "padrao": "standard", "safe": "safe"}


@dataclass(frozen=True)
class ModelDecision:
    tier: str
    model: str
    effort: str
    task_budget: int | None
    lane: str
    phase: str
    reason: str


def normalize_lane(lane):
    return _LANE_ALIASES.get(str(lane or "").strip().lower())


def normalize_phase(phase):
    key = str(phase or "").strip().lower()
    if key in _PHASE_ALIASES:
        return _PHASE_ALIASES[key]
    # tolerate "1 inception", "phase: design", etc.
    for token, canonical in _PHASE_ALIASES.items():
        if token in key:
            return canonical
    return None


def higher_tier(a, b):
    return a if TIERS.index(a) >= TIERS.index(b) else b


def resolve_model_policy(lane, phase, tier_model=None):
    """Resolve the model decision for a step, or None when lane/phase are unknown
    (caller keeps the host default and records what ran, per D3)."""
    lane_key = normalize_lane(lane)
    phase_key = normalize_phase(phase)
    if lane_key is None or phase_key is None:
        return None
    tier_model = tier_model or CLAUDE_TIER_MODEL
    floor = FLOOR_BY_LANE[lane_key]
    adjust = PHASE_ADJUST[phase_key][lane_key]
    if phase_key == "operation":
        tier = adjust  # documented floor exception: Operate may sit below the lane floor
        reason = "Operate (mechanical; may run below the lane floor)"
    else:
        tier = higher_tier(floor, adjust)
        if phase_key == "design":
            reason = "Design pinned strong"
        elif tier == floor and floor != adjust:
            reason = f"{lane_key.upper()} floor"
        elif adjust == tier and adjust != floor:
            reason = f"{phase_key.capitalize()} raises to {tier}"
        else:
            reason = f"{lane_key.upper()} floor"
    return ModelDecision(
        tier=tier,
        model=tier_model.get(tier, tier),
        effort=EFFORT[phase_key][lane_key],
        task_budget=EXECUTION_TASK_BUDGET if phase_key == "execution" else None,
        lane=lane_key,
        phase=phase_key,
        reason=reason,
    )


def describe_model(actual_model, lane, phase, host=None):
    """Toolbar model string.

    Always shows the model **actually running** when known; the policy target is
    guidance shown alongside and flagged when it differs (e.g. the host could not
    switch, or the human overrode). When the actual model is unknown, the target
    is shown explicitly labelled as an unconfirmed target — never presented as if
    it were running. Returns None only when nothing is known (caller keeps
    "default")."""
    actual = str(actual_model or "").strip()
    if actual.lower() in ("", "default", "unknown"):
        actual = ""
    decision = resolve_model_policy(lane, phase, TIER_MODEL_BY_HOST.get(host or ""))
    if actual and decision:
        if actual == decision.model:
            return f"{actual} · {decision.tier} · esf {decision.effort}"
        # forced but not switched (or human override): show what is running, flag
        # the policy target compactly so the box does not truncate the mismatch.
        return f"{actual} (política: {decision.model})"
    if actual:
        return actual
    if decision:
        return f"{decision.model} · alvo {decision.tier} · esf {decision.effort} · não confirmado"
    return None


_PHASE_LABEL_PT = {
    "inception": "Inception",
    "design": "Design",
    "execution": "Execution",
    "validate": "Validate",
    "operation": "Operation",
}


def model_advisory(actual_model, lane, phase):
    """One-line pt-BR chat advisory for the model of a step, or None when already
    aligned / unresolvable.

    This is the *actionable* message (belongs in the chat interaction line at a
    phase transition, not permanently in the toolbar): it announces the target
    and invites the human to switch. The toolbar keeps only the compact state
    flag; here we tell the person what to do about it."""
    decision = resolve_model_policy(lane, phase)
    if decision is None:
        return None
    label = _PHASE_LABEL_PT.get(decision.phase, decision.phase.capitalize())
    actual = str(actual_model or "").strip()
    if actual.lower() in ("", "default", "unknown"):
        return (f"Esta etapa ({label}) pede `{decision.model}` (tier {decision.tier}, "
                f"esf {decision.effort}). Use `/model` para definir e eu registro o modelo em uso.")
    if actual == decision.model:
        return None  # already on the policy model — nothing to nudge
    return (f"Esta etapa ({label}) roda melhor em `{decision.model}` (tier {decision.tier}, "
            f"esf {decision.effort}). Você está em `{actual}` - use `/model` para alinhar, "
            f"ou siga assim que eu registro o modelo real.")
