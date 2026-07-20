"""DEVIN CLI transcript parsing (host format -> parsed step observations).

Devin bills in ACU and exposes ACU only through the web UI (Session Insights,
Consumption dashboards) and the interactive `/usage`. None of that is reachable
from a script, which is why Alfred recorded Devin usage as "nao coletado".

Tokens are a different story: the session transcript
(`cli/transcripts/<session>.json`) carries **exact** `prompt_tokens` and
`completion_tokens` per step, with a real timestamp and the model that ran. The
per-step values reconcile exactly with `final_metrics`, so this is measured
usage, not an estimate — no API and no credential involved.

Two limits are deliberate and must not be papered over:

- **No cost.** The transcript has no ACU and no USD. Cost stays ``None`` here;
  it becomes a number only through an approved rate card, downstream. Tokens are
  never converted into ACU: Devin does not bill per token, so any token->ACU
  coefficient would be invented and would read as if it had been measured.
- **Only at session end.** The transcript is written when the session closes,
  so attribution is post-hoc (the same shape as the Claude Stop-hook path).

Privacy: steps also carry `message`, `reasoning_content`, `tool_calls` and
`observation` — real session content. Only `step_id`, `timestamp`, `source`,
`model_name` and `metrics` are read here, because Alfred forwards telemetry to
the org destination.
"""

import json
from pathlib import Path

READ_FIELDS = ("step_id", "timestamp", "source", "model_name", "metrics")


def load_steps(transcript_path):
    """Return the transcript's steps reduced to the fields Alfred may read."""
    data = json.loads(Path(transcript_path).read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps")
    if not isinstance(steps, list):
        return []
    reduced = []
    for step in steps:
        if isinstance(step, dict):
            reduced.append({field: step.get(field) for field in READ_FIELDS})
    return reduced


def session_id(transcript_path):
    data = json.loads(Path(transcript_path).read_text(encoding="utf-8", errors="replace"))
    return str(data.get("session_id") or Path(transcript_path).stem)


def parse_requests(transcript_path):
    """Exact per-step usage, with interaction ids derived from user boundaries.

    ``source: user`` marks where a human turn starts, so every agent step that
    follows belongs to that interaction — the same derivation the Claude adapter
    uses when the host exposes no prompt id.
    """
    requests = []
    interaction = 0
    session = session_id(transcript_path)
    for step in load_steps(transcript_path):
        if step.get("source") == "user":
            interaction += 1
            continue
        metrics = step.get("metrics")
        if not isinstance(metrics, dict):
            continue
        prompt = metrics.get("prompt_tokens")
        completion = metrics.get("completion_tokens")
        if prompt is None and completion is None:
            continue
        requests.append({
            "session_id": session,
            # step_id is the natural dedup key: re-reading a transcript must not
            # double-count, exactly like requestId on the Claude side.
            "request_id": f"{session}#{step.get('step_id')}",
            "interaction_id": f"{session}#i{interaction}" if interaction else "",
            "ts": step.get("timestamp"),
            "model": step.get("model_name") or "",
            "tokens_input": int(prompt or 0),
            "tokens_output": int(completion or 0),
            # Devin reports no cache split; absent stays absent, never zero.
            "tokens_cache_read": None,
            "tokens_cache_creation": None,
            "cost_usd": None,
        })
    return requests


def session_totals(transcript_path):
    """`final_metrics` as reported by the host, for reconciliation."""
    data = json.loads(Path(transcript_path).read_text(encoding="utf-8", errors="replace"))
    totals = data.get("final_metrics")
    return totals if isinstance(totals, dict) else {}
