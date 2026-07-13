import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.observability.application.use_cases.apply_usage_rate_card import (  # noqa: E402
    ApplyUsageRateCard,
    ApplyUsageRateCardCommand,
    LoadedRateCard,
    event_tokens,
)


class FakeRateCardRepository:
    def raw_rates_for(self, model):
        if model != "gpt-example":
            return None
        return {
            "input_per_1m": 10,
            "output_per_1m": 20,
            "cache_creation_per_1m": 1,
            "cache_read_per_1m": 0.5,
        }


def artifact(path, operation, **kwargs):
    return {"path": str(path), "operation": operation, **kwargs}


def usage_event(event_id="usage-1", model="gpt-example"):
    return {
        "schema_version": "alfred.observability.v1",
        "event_id": event_id,
        "event_type": "usage_attributed",
        "event_scope": "request",
        "session_id": "session-1",
        "interaction_id": "prompt-1",
        "request_id": "request-1",
        "demand_id": "demand-1",
        "phase": "validate",
        "lane": "standard",
        "model": model,
        "output": {
            "model": model,
            "tokens_input": 1000,
            "tokens_output": 100,
            "tokens_cache_creation": 50,
            "tokens_cache_read": 10,
            "token_confidence": "exact",
        },
    }


def rate_card():
    return LoadedRateCard(
        repository=FakeRateCardRepository(),
        hash="abcdef123456",
        path="rate-card.json",
        source="fixture",
        currency="USD",
        confidence="rated",
        effective_from="2026-07-12",
        approved_by="FinOps",
    )


class ApplyUsageRateCardTests(unittest.TestCase):
    def test_generates_interaction_cost_event_from_exact_usage(self):
        service = ApplyUsageRateCard(artifact_builder=artifact, now=lambda: "2026-07-12T00:00:00Z")

        result = service.execute(ApplyUsageRateCardCommand([usage_event()], set(), rate_card()))

        self.assertEqual(1, result.generated_count)
        event = result.events[0]
        self.assertEqual("usage_cost_attributed", event["event_type"])
        self.assertEqual("usage-1", event["parent_event_id"])
        self.assertEqual("abcdef123456", event["metadata"]["rate_card_hash"])
        self.assertEqual("interaction", event["metadata"]["cost_granularity"])
        self.assertEqual(0.012055, event["cost_usd"])

    def test_skips_existing_cost_key(self):
        service = ApplyUsageRateCard(artifact_builder=artifact, now=lambda: "2026-07-12T00:00:00Z")

        result = service.execute(
            ApplyUsageRateCardCommand([usage_event()], {("usage-1", "abcdef123456")}, rate_card())
        )

        self.assertEqual(0, result.generated_count)
        self.assertEqual(1, result.skipped_existing)

    def test_reports_missing_rate_card_model(self):
        service = ApplyUsageRateCard(artifact_builder=artifact, now=lambda: "2026-07-12T00:00:00Z")

        result = service.execute(ApplyUsageRateCardCommand([usage_event(model="unknown-model")], set(), rate_card()))

        self.assertEqual(0, result.generated_count)
        self.assertEqual(("unknown-model",), result.skipped_missing_model)

    def test_event_tokens_prefers_output_payload(self):
        event = {"tokens_input": 1, "output": {"tokens_input": 2, "tokens_output": 3}}

        self.assertEqual(
            {"tokens_input": 2, "tokens_output": 3, "tokens_cache_creation": 0, "tokens_cache_read": 0},
            event_tokens(event),
        )


if __name__ == "__main__":
    unittest.main()
