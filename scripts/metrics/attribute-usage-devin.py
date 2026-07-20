#!/usr/bin/env python3
"""Attribute exact DEVIN CLI token usage to a demand, from the local transcript.

Devin's ACU is only reachable through the web UI and the interactive `/usage`,
so Alfred recorded Devin usage as "nao coletado" and the plan carried the
Consumption API as a blocker. Tokens do not need any of that: the session
transcript holds exact per-step `prompt_tokens`/`completion_tokens`, which
reconcile with `final_metrics`.

What this writes: one `usage_attributed` event per step, tokens exact,
de-duplicated by step id, with interaction ids derived from user boundaries.

What this refuses to write: cost. The transcript has no ACU and no USD, and
Devin does not bill per token, so no coefficient could turn these tokens into
ACU without inventing one. Cost stays null until an approved rate card supplies
a price for a measured ACU figure (`apply-usage-rate-card.py`).
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.common import read_state_fields, write_state_fields  # noqa: E402
from shared.common.observability_event import OBSERVABILITY_SCHEMA, append_event  # noqa: E402
from shared.observability.infrastructure.adapters.devin.transcript import (  # noqa: E402
    parse_requests,
    session_id,
    session_totals,
)


def existing_request_ids(log_path):
    """Dedup key: re-running over the same transcript must not double-count."""
    seen = set()
    if not log_path.exists():
        return seen
    for line in log_path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("request_id"):
            seen.add(event["request_id"])
    return seen


def usage_event(fields, request):
    return {
        "schema_version": OBSERVABILITY_SCHEMA,
        "ts": request["ts"],
        "event_id": f"evt-devin-{request['request_id']}",
        "event_type": "usage_attributed",
        "event_scope": "request",
        "trace_id": f"demand-{fields.get('id', '')}",
        "session_id": request["session_id"],
        "interaction_id": request["interaction_id"] or None,
        "request_id": request["request_id"],
        "sequence": None,
        "initiative_id": fields.get("initiative id", ""),
        "demand_id": fields.get("id", ""),
        "phase": fields.get("current phase", ""),
        "lane": fields.get("lane", ""),
        "actor_type": "host",
        "actor_id": "devin-cli",
        "agent": "devin-cli",
        "action": "usage_attributed",
        "model": request["model"],
        "tokens_input": request["tokens_input"],
        "tokens_output": request["tokens_output"],
        "tokens_cache_read": request["tokens_cache_read"],
        "tokens_cache_creation": request["tokens_cache_creation"],
        # Devin exposes no per-request cost; absent stays absent, never 0.
        "cost_usd": None,
        "token_confidence": "exact",
        "correlation_method": "devin_transcript_step",
        "artifacts_used": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-path", "-StatePath", dest="state_path", required=True)
    parser.add_argument("--transcript-path", "-TranscriptPath", dest="transcript_path",
                        required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    state = Path(args.state_path).resolve()
    transcript = Path(args.transcript_path).resolve()
    if not state.is_file():
        print(f"State nao encontrado: {state}")
        return 2
    if not transcript.is_file():
        print(f"Transcript nao encontrado: {transcript}")
        return 2

    fields = read_state_fields(state)
    requests = parse_requests(transcript)
    if not requests:
        print("Transcript sem steps com metrics; nada a atribuir.")
        return 0

    log = state.parent / "05-operation" / "011-observability-log.jsonl"
    already = existing_request_ids(log)
    new = [item for item in requests if item["request_id"] not in already]
    totals = session_totals(transcript)
    tokens_in = sum(item["tokens_input"] for item in new)
    tokens_out = sum(item["tokens_output"] for item in new)

    if args.dry_run:
        print(f"Atribuiria {len(new)} de {len(requests)} steps "
              f"({tokens_in} input / {tokens_out} output). Custo: nao coletado.")
        return 0

    for item in new:
        append_event(log, usage_event(fields, item))

    write_state_fields(state, {
        "usage session id": session_id(transcript),
        "usage-cost": "devin transcript (tokens exatos)",
        "cost source": "devin_transcript",
        "cost confidence": "exact",
        "cost granularity": "request",
    }, section="Progress")

    print(f"{len(new)} steps atribuidos ({tokens_in} input / {tokens_out} output). "
          f"Sessao reporta {totals.get('total_prompt_tokens')} / "
          f"{totals.get('total_completion_tokens')}. Custo: nao coletado "
          "(Devin nao expoe ACU/USD localmente).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
