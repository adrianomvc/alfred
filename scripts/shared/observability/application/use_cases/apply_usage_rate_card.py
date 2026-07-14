from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from shared.observability.domain.services.rate_card import ModelRate, price_usage_usd


ArtifactBuilder = Callable[..., dict[str, object]]
Clock = Callable[[], str]


@dataclass(frozen=True)
class LoadedRateCard:
    repository: object
    hash: str
    path: str
    source: object
    currency: object
    confidence: object
    effective_from: object
    approved_by: object


@dataclass(frozen=True)
class ApplyUsageRateCardCommand:
    usage_events: Sequence[Mapping[str, object]]
    existing_cost_keys: set[tuple[object, object]]
    rate_card: LoadedRateCard


@dataclass(frozen=True)
class ApplyUsageRateCardResult:
    events: tuple[dict[str, object], ...]
    skipped_missing_model: tuple[str, ...]
    skipped_existing: int

    @property
    def generated_count(self) -> int:
        return len(self.events)

    def empty_detail(self) -> str:
        detail = ""
        if self.skipped_missing_model:
            detail = f" Missing rate card models: {', '.join(sorted(set(self.skipped_missing_model)))}."
        if self.skipped_existing:
            detail += f" Existing cost events skipped: {self.skipped_existing}."
        return detail


class ApplyUsageRateCard:
    def __init__(self, *, artifact_builder: ArtifactBuilder, now: Clock) -> None:
        self._artifact_builder = artifact_builder
        self._now = now

    def execute(self, command: ApplyUsageRateCardCommand) -> ApplyUsageRateCardResult:
        events = []
        skipped_missing_model = []
        skipped_existing = 0
        for event in command.usage_events:
            if event.get("event_type") != "usage_attributed":
                continue
            model, rates = rate_for(event, command.rate_card)
            if not rates:
                skipped_missing_model.append(model or "unknown")
                continue
            key = (event.get("event_id"), command.rate_card.hash)
            if key in command.existing_cost_keys:
                skipped_existing += 1
                continue
            tokens = event_tokens(event)
            cost = calculate_cost(tokens, rates)
            cost_event = self.make_cost_event(event, tokens, cost, model, rates, command.rate_card, len(events) + 1)
            events.append(cost_event)
        return ApplyUsageRateCardResult(tuple(events), tuple(skipped_missing_model), skipped_existing)

    def make_cost_event(self, usage_event, tokens, cost, model, rates, rate_card, sequence):
        parent = usage_event.get("event_id")
        short_hash = rate_card.hash[:8]
        ts = self._now()
        return {
            "schema_version": "alfred.observability.v1",
            "alfred": usage_event.get("alfred") or {"schema_version": "alfred.observability.v1"},
            "ts": ts,
            "event_id": f"usage-cost-{parent}-{short_hash}",
            "trace_id": usage_event.get("trace_id"),
            "session_id": usage_event.get("session_id"),
            "interaction_id": usage_event.get("interaction_id"),
            "sequence": sequence,
            "initiative_id": usage_event.get("initiative_id"),
            "demand_id": usage_event.get("demand_id"),
            "event_type": "usage_cost_attributed",
            "phase": usage_event.get("phase"),
            "lane": usage_event.get("lane"),
            "actor_type": "system",
            "actor_id": "usage-rate-card",
            "action": "attribute_interaction_cost",
            "status": "recorded",
            "step": {
                "id": "usage-cost",
                "name": "Usage and cost attribution",
                "sequence": sequence,
                "goal": "Compute interaction cost from exact usage and an approved rate card",
            },
            "artifacts_used": [
                self._artifact_builder(rate_card.path, "read", selection_reason="approved_rate_card", observed_by="usage-rate-card", ts=ts),
                self._artifact_builder(parent, "reference", selection_reason="parent_usage_event", observed_by="usage-rate-card", ts=ts),
            ],
            "duration_ms": None,
            "tokens_input": tokens["tokens_input"],
            "tokens_output": tokens["tokens_output"],
            "cost_usd": cost,
            "retry_count": None,
            "input": {
                "source": "usage_attributed_event",
                "source_kind": "usage_rate_card",
                "parent_event_id": parent,
                "rate_card_source": rate_card.source,
            },
            "derivation": {
                "rules_applied": [
                    "connectors/usage-cost.md",
                    "connectors/usage-rate-card.md",
                    "metrics/metrics.md",
                ],
                "method": "interaction cost = exact usage units multiplied by approved per-model rate card; no session-total allocation",
                "attribution": "derived",
            },
            "output": {
                "model": model,
                "tokens_input": tokens["tokens_input"],
                "tokens_output": tokens["tokens_output"],
                "tokens_cache_creation": tokens["tokens_cache_creation"],
                "tokens_cache_read": tokens["tokens_cache_read"],
                "cost_usd": cost,
                "currency": rate_card.currency or "USD",
                "cost_confidence": rate_card.confidence or "rated",
                "token_confidence": (usage_event.get("output") or {}).get("token_confidence", "exact"),
                "rates_per_1m": rates,
            },
            "model": model,
            "tool": "scripts/metrics/apply-usage-rate-card.py",
            "parent_event_id": parent,
            "artifacts": [],
            "files_changed": [],
            "validation": {"rate_card_parse": "ok", "source_usage_event": "ok"},
            "risk": None,
            "blocker": None,
            "error": None,
            "state_transition": None,
            "actions": [{"type": "attribute_interaction_cost", "status": "completed"}],
            "questions_open": [],
            "assumptions": [],
            "metric_impact": {"interaction_cost_attribution": "added"},
            "next": [],
            "metadata": {
                "connector_type": "usage-rate-card",
                "source_kind": "usage_rate_card",
                "rate_card_source": rate_card.source,
                "rate_card_effective_from": rate_card.effective_from,
                "rate_card_approved_by": rate_card.approved_by,
                "rate_card_currency": rate_card.currency or "USD",
                "rate_card_hash": rate_card.hash,
                "cost_granularity": "interaction",
            },
        }


def event_tokens(event):
    output = event.get("output") or {}
    return {
        "tokens_input": int(output.get("tokens_input") or event.get("tokens_input") or 0),
        "tokens_output": int(output.get("tokens_output") or event.get("tokens_output") or 0),
        "tokens_cache_creation": int(output.get("tokens_cache_creation") or event.get("tokens_cache_creation") or 0),
        "tokens_cache_read": int(output.get("tokens_cache_read") or event.get("tokens_cache_read") or 0),
    }


def rate_for(event, rate_card):
    model = event.get("model") or (event.get("output") or {}).get("model")
    rates = rate_card.repository.raw_rates_for(model)
    return model, rates


def calculate_cost(tokens, rates):
    return price_usage_usd(tokens, ModelRate.from_mapping(rates))
