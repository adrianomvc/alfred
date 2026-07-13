import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.observability.application.use_cases.attribute_transcript_usage import (  # noqa: E402
    AttributeTranscriptUsage,
    AttributeTranscriptUsageCommand,
    TranscriptAttributionContext,
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


def request(request_id="req-1", interaction_id="prompt-1", tokens_input=1000):
    return {
        "request_id": request_id,
        "ts": datetime(2026, 7, 12, 10, 0, 1, tzinfo=timezone.utc),
        "session_id": "session-1",
        "model": "gpt-example",
        "interaction_id": interaction_id,
        "interaction_sequence": 1,
        "request_sequence": 1,
        "interaction_confidence": "exact",
        "correlation_method": "prompt_id",
        "tokens_input": tokens_input,
        "tokens_output": 100,
        "tokens_cache_creation": 50,
        "tokens_cache_read": 10,
    }


def context(**overrides):
    values = {
        "transcript_path": "transcript.jsonl",
        "state_fields": {
            "framework version": "2.0.0",
            "framework ref": "main",
            "framework commit": "abc123",
            "alfred run id": "state-run",
            "initiative id": "initiative-1",
            "id": "demand-1",
            "current phase": "validate",
            "lane": "SAFE",
        },
        "rate_card": None,
        "granularity": "request",
        "emit_interactions": False,
        "run_id": "run-1",
        "phase": "",
        "session_id": "",
    }
    values.update(overrides)
    return TranscriptAttributionContext(**values)


def rate_card():
    return {
        "_repo": FakeRateCardRepository(),
        "_hash": "abcdef123456",
        "source": "fixture",
        "currency": "USD",
        "confidence": "rated",
        "effective_from": "2026-07-12",
        "approved_by": "FinOps",
    }


class AttributeTranscriptUsageTests(unittest.TestCase):
    def test_builds_request_event_with_anchor_and_rate_card_cost(self):
        service = AttributeTranscriptUsage(artifact_builder=artifact, now=lambda: "2026-07-12T11:00:00Z")
        anchors = [{"ts": datetime(2026, 7, 12, 10, 0, tzinfo=timezone.utc), "event_id": "anchor-1", "phase": "design", "lane": "Standard"}]

        result = service.execute(
            AttributeTranscriptUsageCommand([request()], anchors, [], context(rate_card=rate_card()))
        )

        self.assertIsNone(result.missing_rate_card_model)
        event = result.events[0]
        self.assertEqual("usage_attributed", event["event_type"])
        self.assertEqual("request", event["event_scope"])
        self.assertEqual("req-1", event["request_id"])
        self.assertEqual("design", event["phase"])
        self.assertEqual("Standard", event["lane"])
        self.assertEqual("anchor-1", event["parent_event_id"])
        self.assertEqual(0.012055, event["cost_usd"])
        self.assertEqual("usage_rate_card", event["metadata"]["cost_source_kind"])

    def test_emit_interactions_aggregates_existing_and_new_requests(self):
        service = AttributeTranscriptUsage(artifact_builder=artifact, now=lambda: "2026-07-12T11:00:00Z")
        existing = {
            "event_type": "usage_attributed",
            "event_scope": "request",
            "ts": "2026-07-12T09:00:00Z",
            "request_id": "req-existing",
            "interaction_id": "prompt-1",
            "session_id": "session-1",
            "model": "gpt-example",
            "phase": "design",
            "lane": "Standard",
            "tokens_input": 10,
            "tokens_output": 1,
            "tokens_cache_creation": 0,
            "tokens_cache_read": 0,
        }

        result = service.execute(
            AttributeTranscriptUsageCommand([request(tokens_input=20)], [], [existing], context(emit_interactions=True))
        )

        interaction = [event for event in result.events if event["event_type"] == "interaction_completed"][0]
        self.assertEqual(2, interaction["request_count"])
        self.assertEqual(["req-existing", "req-1"], interaction["input"]["request_ids"])
        self.assertEqual(30, interaction["usage"]["tokens_input"])

    def test_reports_missing_rate_card_model_without_emitting_events(self):
        service = AttributeTranscriptUsage(artifact_builder=artifact, now=lambda: "2026-07-12T11:00:00Z")
        missing = dict(request())
        missing["model"] = "unknown-model"

        result = service.execute(AttributeTranscriptUsageCommand([missing], [], [], context(rate_card=rate_card())))

        self.assertEqual("unknown-model", result.missing_rate_card_model)
        self.assertEqual((), result.events)


if __name__ == "__main__":
    unittest.main()
