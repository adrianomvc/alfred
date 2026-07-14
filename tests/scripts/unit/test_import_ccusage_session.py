import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.observability.application.use_cases.import_ccusage_session import (  # noqa: E402
    ImportCcusageSession,
    ImportCcusageSessionCommand,
)
from shared.observability.infrastructure.adapters.ccusage.session import (  # noqa: E402
    CcusageSessionAdapter,
    NoSessionMatch,
)


def artifact(path, operation, **kwargs):
    return {"path": str(path), "operation": operation, **kwargs}


def command(**overrides):
    values = {
        "row": {
            "period": "session-1",
            "agent": "claude",
            "totalCost": 1.25,
            "inputTokens": 1000,
            "outputTokens": 250,
            "cacheCreationTokens": 50,
            "cacheReadTokens": 25,
            "totalTokens": 1325,
            "metadata": {"lastActivity": "2026-07-12T10:00:00Z"},
        },
        "state_fields": {
            "framework version": "2.0.0",
            "framework ref": "main",
            "framework commit": "abc123",
            "alfred run id": "state-run",
            "initiative id": "initiative-1",
            "id": "demand-1",
            "current phase": "execute",
            "lane": "SAFE",
        },
        "selection_method": "latest_agent_session",
        "source_path": "ccusage session --json",
        "run_id": "run-1",
        "phase": "",
        "host": "claude-code",
        "model": "claude-sonnet",
        "last_activity": "2026-07-12T10:00:00Z",
    }
    values.update(overrides)
    return ImportCcusageSessionCommand(**values)


class ImportCcusageSessionTests(unittest.TestCase):
    def test_builds_session_snapshot_without_allocating_interaction_cost(self):
        service = ImportCcusageSession(artifact_builder=artifact, now=lambda: "2026-07-12T11:00:00Z")

        result = service.execute(command())
        snapshot = result.snapshot

        self.assertEqual("alfred.usage-session.v1", snapshot["schema_version"])
        self.assertEqual("session_usage_snapshot", snapshot["record_type"])
        self.assertEqual("session-1", snapshot["session_id"])
        self.assertEqual("demand-1", snapshot["demand_id"])
        self.assertEqual("execute", snapshot["phase"])
        self.assertEqual("SAFE", snapshot["lane"])
        self.assertEqual(1.25, snapshot["cost_usd"])
        self.assertEqual("claude-sonnet", snapshot["model"])
        self.assertEqual("latest_agent_session", snapshot["input"]["selection_method"])
        self.assertEqual("session", snapshot["metadata"]["granularity"])
        self.assertIn("session total only", snapshot["derivation"]["method"])

    def test_builds_state_updates_as_session_cost_fields(self):
        service = ImportCcusageSession(artifact_builder=artifact, now=lambda: "2026-07-12T11:00:00Z")

        updates = service.execute(command()).state_updates

        self.assertEqual("ccusage automatic", updates["usage-cost"])
        self.assertEqual("ccusage", updates["cost source"])
        self.assertEqual("1.25", updates["cost usd"])
        self.assertEqual("session", updates["cost granularity"])
        self.assertEqual("session-1", updates["usage session id"])
        self.assertEqual("2026-07-12T11:00:00Z", updates["usage imported at"])
        self.assertEqual("run-1", updates["alfred run id"])

    def test_uses_clock_when_last_activity_is_unavailable(self):
        service = ImportCcusageSession(artifact_builder=artifact, now=lambda: "2026-07-12T11:00:00Z")

        snapshot = service.execute(command(last_activity="")).snapshot

        self.assertEqual("2026-07-12T11:00:00Z", snapshot["ts"])


class CcusageSelectSessionTests(unittest.TestCase):
    def _payload(self):
        return {"session": [
            {"agent": "claude", "period": "aaaa-1111-2222-3333-444455556666",
             "metadata": {"lastActivity": "2026-07-12T09:00:00Z"}},
            {"agent": "claude", "period": "bbbb-7777-8888-9999-000011112222",
             "metadata": {"lastActivity": "2026-07-12T12:00:00Z"}},
            {"agent": "codex", "period": "cccc", "metadata": {"lastActivity": "2026-07-12T13:00:00Z"}},
        ]}

    def test_exact_period_match(self):
        row, method = CcusageSessionAdapter().select_session(self._payload(), "claude", "aaaa-1111-2222-3333-444455556666")
        self.assertEqual("session_id", method)
        self.assertEqual("aaaa-1111-2222-3333-444455556666", row["period"])

    def test_truncated_id_resolves_via_prefix(self):
        # a stored id truncated at demand creation still finds its full session
        row, method = CcusageSessionAdapter().select_session(self._payload(), "claude", "aaaa-1111-2222-3333-4444")
        self.assertEqual("fallback_prefix", method)
        self.assertEqual("aaaa-1111-2222-3333-444455556666", row["period"])

    def test_unknown_id_with_multiple_sessions_refuses_to_guess(self):
        # Several agent sessions and no exact/prefix match -> refuse (safe), so the
        # caller keeps the prior cost as stale instead of attributing an unrelated one.
        with self.assertRaises(NoSessionMatch):
            CcusageSessionAdapter().select_session(self._payload(), "claude", "zzzz-does-not-exist")

    def test_unknown_id_with_single_session_auto_heals(self):
        payload = {"session": [
            {"agent": "claude", "period": "only-session-uuid",
             "metadata": {"lastActivity": "2026-07-12T12:00:00Z"}},
        ]}
        row, method = CcusageSessionAdapter().select_session(payload, "claude", "totally-different-id")
        self.assertEqual("fallback_latest", method)
        self.assertEqual("only-session-uuid", row["period"])

    def test_no_agent_sessions_raises(self):
        with self.assertRaises(NoSessionMatch):
            CcusageSessionAdapter().select_session(self._payload(), "devin", "whatever")


if __name__ == "__main__":
    unittest.main()
