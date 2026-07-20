"""Risk Mode scoring shared by the CLI and workflow helpers.

Single implementation of the objective checklist in ``core/risk-mode.md``:
each criterion scores 0/1/2, the lane comes from the greater axis, and hard
overrides only raise the lane. The AI proposes; the human confirms
(Standard/SAFE).
"""

RISK_CRITERIA = [
    ("reversibility", "Reversibility"),
    ("blast_radius", "Blast radius"),
    ("sensitive_data", "Sensitive/regulated data"),
    ("customer_impact", "Customer impact"),
    ("cost", "Cost / financial risk"),
]
COMPLEXITY_CRITERIA = [
    ("components", "Components affected"),
    ("novelty", "Technical novelty"),
    ("ambiguity", "Requirement ambiguity"),
    ("integrations", "Integrations"),
    ("effort", "Estimated effort"),
]
LANES = ["FAST", "Standard", "SAFE"]


def lane_from_score(score):
    if score <= 3:
        return "FAST"
    if score <= 6:
        return "Standard"
    return "SAFE"


def max_lane(a, b):
    return a if LANES.index(a) >= LANES.index(b) else b


def propose(risk_scores, complexity_scores, architectural_change=False, multi_squad=False):
    """Compute the proposed lane from per-criterion 0/1/2 scores.

    ``risk_scores``/``complexity_scores`` map criterion key -> 0|1|2. Returns a
    dict with both axis sums, the fired hard overrides, and the proposed lane.
    """
    risk = sum(risk_scores.get(key, 0) for key, _ in RISK_CRITERIA)
    complexity = sum(complexity_scores.get(key, 0) for key, _ in COMPLEXITY_CRITERIA)
    base_score = max(risk, complexity)
    lane = lane_from_score(base_score)

    overrides = []
    critical = [("sensitive_data", "sensitive/regulated data = 2"),
                ("reversibility", "hard/irreversible = 2"),
                ("customer_impact", "direct customer impact = 2")]
    fired = [text for key, text in critical if risk_scores.get(key, 0) == 2]
    if len(fired) >= 2:
        overrides.append("2+ critical risk criteria -> SAFE (" + "; ".join(fired) + ")")
        lane = max_lane(lane, "SAFE")
    elif len(fired) == 1:
        overrides.append(fired[0] + " -> minimum Standard")
        lane = max_lane(lane, "Standard")
    if architectural_change:
        overrides.append("architectural change -> SAFE")
        lane = max_lane(lane, "SAFE")
    if multi_squad:
        overrides.append("multi-squad -> SAFE")
        lane = max_lane(lane, "SAFE")

    return {"risk": risk, "complexity": complexity, "base_score": base_score,
            "lane": lane, "overrides": overrides}
