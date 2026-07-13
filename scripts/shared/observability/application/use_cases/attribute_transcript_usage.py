from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from shared.observability.domain.services.legacy_usage import usage_tokens
from shared.observability.domain.services.rate_card import ModelRate, price_usage_usd


ArtifactBuilder = Callable[..., dict[str, object]]
Clock = Callable[[], str]


def _value_or(value, fallback):
    if value is None:
        return fallback
    if isinstance(value, str) and not value.strip():
        return fallback
    return value


def _iso(value):
    if not isinstance(value, datetime):
        return None
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rates_for(model, rate_card):
    if not rate_card:
        return None
    return rate_card["_repo"].raw_rates_for(model)


def _calculate_cost(tokens, rates):
    return price_usage_usd(tokens, ModelRate.from_mapping(rates))


@dataclass(frozen=True)
class TranscriptAttributionContext:
    transcript_path: str
    state_fields: Mapping[str, str]
    rate_card: Mapping[str, object] | None
    granularity: str
    emit_interactions: bool
    run_id: str
    phase: str
    session_id: str


@dataclass(frozen=True)
class AttributeTranscriptUsageCommand:
    requests: Sequence[Mapping[str, object]]
    anchors: Sequence[Mapping[str, object]]
    existing_request_events: Sequence[Mapping[str, object]]
    context: TranscriptAttributionContext


@dataclass(frozen=True)
class AttributeTranscriptUsageResult:
    events: tuple[dict[str, object], ...]
    request_events: tuple[dict[str, object], ...]
    interaction_events: tuple[dict[str, object], ...]
    missing_rate_card_model: str | None = None


class AttributeTranscriptUsage:
    def __init__(self, *, artifact_builder: ArtifactBuilder, now: Clock) -> None:
        self._artifact_builder = artifact_builder
        self._now = now

    def execute(self, command: AttributeTranscriptUsageCommand) -> AttributeTranscriptUsageResult:
        request_events = []
        for index, request in enumerate(command.requests, start=1):
            anchor = enclosing_event(request["ts"], command.anchors)
            event, missing_model = self._make_request_event(request, command.context, anchor, index)
            if missing_model:
                return AttributeTranscriptUsageResult((), (), (), missing_model)
            request_events.append(event)

        output_events = []
        interaction_events = []
        context = command.context
        if context.granularity in ("request", "turn", "window"):
            output_events.extend(request_events)
        if context.granularity == "interaction" or context.emit_interactions:
            aggregate_input = [*command.existing_request_events, *request_events]
            interaction_events = self._make_interaction_events(aggregate_input, context.state_fields)
            output_events.extend(interaction_events)
        return AttributeTranscriptUsageResult(
            events=tuple(output_events),
            request_events=tuple(request_events),
            interaction_events=tuple(interaction_events),
        )

    def _phase_lane(self, context: TranscriptAttributionContext, anchor):
        state_fields = context.state_fields
        phase = _value_or(
            context.phase,
            _value_or((anchor or {}).get("phase"), _value_or(state_fields.get("current phase"), "operation")),
        )
        lane = _value_or((anchor or {}).get("lane"), _value_or(state_fields.get("lane"), _value_or(state_fields.get("modo"), "unknown")))
        return phase, lane

    def _make_request_event(self, request, context: TranscriptAttributionContext, anchor, sequence):
        tokens = {
            "tokens_input": request["tokens_input"],
            "tokens_output": request["tokens_output"],
            "tokens_cache_creation": request["tokens_cache_creation"],
            "tokens_cache_read": request["tokens_cache_read"],
        }
        tokens["total_tokens"] = sum(tokens.values())
        cost = None
        confidence = "unavailable"
        rates = _rates_for(request.get("model"), context.rate_card)
        if context.rate_card and not rates:
            return None, request.get("model") or "unknown"
        if rates:
            cost = _calculate_cost(tokens, rates)
            confidence = _value_or(context.rate_card.get("confidence"), "rated")
        phase, lane = self._phase_lane(context, anchor)
        anchor_ref = anchor.get("event_id") if anchor else None
        interaction_id = request.get("interaction_id")
        ts = _iso(request.get("ts"))
        return {
            "schema_version": "alfred.observability.v1",
            "alfred": {
                "version": _value_or(context.state_fields.get("framework version"), "unknown"),
                "framework_ref": _value_or(context.state_fields.get("framework ref"), "local"),
                "framework_commit": _value_or(context.state_fields.get("framework commit"), None),
                "schema_version": "alfred.observability.v1",
            },
            "ts": ts or self._now(),
            "event_id": f"usage-request-{request['request_id']}",
            "event_scope": "request",
            "trace_id": _value_or(context.state_fields.get("alfred run id"), _value_or(context.run_id, "unknown")),
            "session_id": _value_or(
                context.session_id,
                _value_or(request.get("session_id"), _value_or(context.state_fields.get("usage session id"), "unknown")),
            ),
            "interaction_id": interaction_id,
            "request_id": request["request_id"],
            "interaction_sequence": request.get("interaction_sequence"),
            "request_sequence": request.get("request_sequence"),
            "sequence": sequence,
            "initiative_id": _value_or(context.state_fields.get("initiative id"), "unknown"),
            "demand_id": _value_or(context.state_fields.get("id"), "unknown"),
            "event_type": "usage_attributed",
            "phase": phase,
            "lane": lane,
            "actor_type": "system",
            "actor_id": "usage-cost-transcript",
            "action": "attribute_usage",
            "status": "recorded",
            "step": {
                "id": "usage-cost",
                "name": "Usage and cost attribution",
                "sequence": sequence,
                "goal": "Attribute exact host transcript usage at request scope",
            },
            "artifacts_used": [
                self._artifact_builder(
                    context.transcript_path,
                    "read",
                    selection_reason="host_transcript_usage",
                    observed_by="claude_hook",
                    ts=ts,
                )
            ],
            "duration_ms": None,
            "tokens_input": tokens["tokens_input"],
            "tokens_output": tokens["tokens_output"],
            "tokens_cache_creation": tokens["tokens_cache_creation"],
            "tokens_cache_read": tokens["tokens_cache_read"],
            "cost_usd": cost,
            "retry_count": None,
            "token_confidence": "exact",
            "interaction_confidence": request.get("interaction_confidence"),
            "correlation_method": request.get("correlation_method"),
            "input": {
                "source": "host_transcript",
                "source_kind": "host_transcript",
                "granularity": "request",
                "legacy_granularity_alias": "turn" if context.granularity == "turn" else None,
                "request_ids": [request["request_id"]],
                "anchor_event_id": anchor_ref,
            },
            "derivation": {
                "rules_applied": ["connectors/usage-cost.md", "metrics/metrics.md"],
                "method": "request-attribution: exact tokens from transcript requestId; interaction correlation from promptId/user boundary when available",
                "attribution": "derived",
            },
            "output": {
                "model": request.get("model"),
                **tokens,
                "cost_usd": cost,
                "currency": (context.rate_card or {}).get("currency"),
                "cost_confidence": confidence,
                "token_confidence": "exact",
            },
            "model": request.get("model"),
            "tool": "scripts/metrics/attribute-usage-transcript.py",
            "parent_event_id": anchor_ref,
            "artifacts": [],
            "files_changed": [],
            "validation": {"source_record_parse": "ok", "dedup_by": "requestId"},
            "risk": None,
            "blocker": None,
            "error": None,
            "state_transition": None,
            "actions": [{"type": "attribute_usage", "status": "completed"}],
            "questions_open": [],
            "assumptions": [] if interaction_id else ["Host transcript did not expose an interaction id for this request."],
            "metric_impact": {"usage_attribution": "added"},
            "next": [],
            "metadata": {
                "connector_type": "usage-cost",
                "source_kind": "host_transcript",
                "granularity": "request",
                "cost_source_kind": "usage_rate_card" if rates else None,
                "rate_card_source": (context.rate_card or {}).get("source"),
                "rate_card_effective_from": (context.rate_card or {}).get("effective_from"),
                "rate_card_approved_by": (context.rate_card or {}).get("approved_by"),
                "rate_card_hash": (context.rate_card or {}).get("_hash"),
            },
        }, None

    def _make_interaction_events(self, request_events, state_fields):
        by_interaction = defaultdict(list)
        for event in request_events:
            interaction_id = event.get("interaction_id")
            if interaction_id:
                by_interaction[interaction_id].append(event)
        events = []
        for index, (interaction_id, group) in enumerate(sorted(by_interaction.items()), start=1):
            group.sort(key=lambda e: e.get("ts") or "")
            first = group[0]
            tokens = Counter()
            models = set()
            phases = set()
            lanes = set()
            for event in group:
                current = usage_tokens(event)
                for key in ("tokens_input", "tokens_output", "tokens_cache_creation", "tokens_cache_read", "total_tokens"):
                    tokens[key] += current[key]
                if event.get("model"):
                    models.add(event["model"])
                if event.get("phase"):
                    phases.add(event["phase"])
                if event.get("lane"):
                    lanes.add(event["lane"])
            denominator = tokens["tokens_input"] + tokens["tokens_cache_creation"] + tokens["tokens_cache_read"]
            cache_ratio = None if denominator == 0 else tokens["tokens_cache_read"] / denominator
            events.append(
                {
                    "schema_version": "alfred.observability.v1",
                    "alfred": first.get("alfred") or {"schema_version": "alfred.observability.v1"},
                    "ts": first.get("ts") or self._now(),
                    "event_id": f"interaction-completed-{interaction_id}",
                    "event_scope": "interaction",
                    "trace_id": first.get("trace_id"),
                    "session_id": first.get("session_id"),
                    "interaction_id": interaction_id,
                    "request_id": None,
                    "sequence": index,
                    "initiative_id": first.get("initiative_id"),
                    "demand_id": first.get("demand_id"),
                    "event_type": "interaction_completed",
                    "phase": first.get("phase"),
                    "lane": first.get("lane"),
                    "actor_type": "system",
                    "actor_id": "usage-cost-transcript",
                    "action": "aggregate_interaction_usage",
                    "status": "recorded",
                    "step": {"id": "usage-cost", "name": "Usage and cost attribution", "sequence": index, "goal": "Aggregate request usage by interaction"},
                    "artifacts_used": [],
                    "duration_ms": None,
                    "tokens_input": None,
                    "tokens_output": None,
                    "tokens_cache_creation": None,
                    "tokens_cache_read": None,
                    "cost_usd": None,
                    "retry_count": None,
                    "request_count": len(group),
                    "tool_call_count": None,
                    "tool_failure_count": None,
                    "usage": {
                        "tokens_input": tokens["tokens_input"],
                        "tokens_output": tokens["tokens_output"],
                        "tokens_cache_creation": tokens["tokens_cache_creation"],
                        "tokens_cache_read": tokens["tokens_cache_read"],
                        "total_tokens": tokens["total_tokens"],
                        "cache_reuse_ratio": cache_ratio,
                    },
                    "context": {
                        "unique_artifacts_read": None,
                        "framework_rules_read": None,
                        "skills_loaded": None,
                        "source_files_read": None,
                        "logs_read": None,
                        "repeated_reads": None,
                        "total_bytes_read": None,
                        "compression_used": None,
                        "rtk_used": None,
                    },
                    "outcome": None,
                    "input": {"source": "usage_attributed_events", "request_ids": [e.get("request_id") for e in group]},
                    "derivation": {"rules_applied": ["metrics/metrics.md"], "method": "sum effective request-scope usage events by interaction_id"},
                    "output": {"models": sorted(models), "phases": sorted(phases), "lanes": sorted(lanes)},
                    "model": ",".join(sorted(models)) if len(models) == 1 else None,
                    "tool": "scripts/metrics/attribute-usage-transcript.py",
                    "parent_event_id": None,
                    "artifacts": [],
                    "files_changed": [],
                    "validation": {"source_request_events": len(group)},
                    "risk": None,
                    "blocker": None,
                    "error": None,
                    "state_transition": None,
                    "actions": [{"type": "aggregate_interaction_usage", "status": "completed"}],
                    "questions_open": [],
                    "assumptions": [],
                    "metric_impact": {"interaction_usage": "aggregated"},
                    "next": [],
                    "metadata": {
                        "connector_type": "usage-cost",
                        "source_kind": "derived_observability",
                        "correlation_method": "interaction_id",
                        "framework_version": state_fields.get("framework version"),
                    },
                }
            )
        return events


def enclosing_event(request_ts, events):
    anchor = events[0] if events else None
    for event in events:
        if event["ts"] <= request_ts:
            anchor = event
        else:
            break
    return anchor
