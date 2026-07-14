import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.observability.application.use_cases.process_claude_hook import (  # noqa: E402
    ClaudeHookContext,
    EngineRunResult,
    ProcessClaudeHook,
    ProcessClaudeHookCommand,
)


class FakeRawAdapter:
    def __init__(self, *, fail=False):
        self.fail = fail

    def read_slice(self, transcript_path, cursor_path):
        if self.fail:
            raise RuntimeError("raw failed")
        return ["{}"], 0, 42

    def normalize_records(self, lines, provider):
        return ([{"provider": provider, "raw_event_type": "model_request"}], "request-1")


def context(**overrides):
    values = {
        "transcript_path": "transcript.jsonl",
        "mode": "both",
        "raw_log": "raw.jsonl",
        "raw_cursor_path": "raw-cursor.json",
        "alfred_cursor_path": "alfred-cursor.json",
        "state_path": "001-state.md",
        "obs_log": "011-observability-log.jsonl",
        "run_id": "run-1",
        "provider": "claude-code",
        "project": "alfred",
        "team": "platform",
        "environment": "test",
    }
    values.update(overrides)
    return ClaudeHookContext(**values)


class ProcessClaudeHookTests(unittest.TestCase):
    def test_raw_mode_appends_enriched_events_and_writes_cursor(self):
        appended = []
        cursors = []

        service = ProcessClaudeHook(
            raw_adapter=FakeRawAdapter(),
            append_events=lambda path, events: appended.append((path, list(events))),
            write_cursor=lambda path, transcript, offset, request: cursors.append((path, transcript, offset, request)),
            write_policy_snapshot=lambda payload, active: None,
            run_engine=lambda invocation: EngineRunResult(0),
        )

        result = service.execute(ProcessClaudeHookCommand({}, {}, context(mode="raw")))

        self.assertEqual((), result.messages)
        self.assertEqual("raw.jsonl", appended[0][0])
        event = appended[0][1][0]
        self.assertEqual("alfred", event["project"])
        self.assertEqual("platform", event["team"])
        self.assertEqual("test", event["environment"])
        self.assertEqual(("raw-cursor.json", "transcript.jsonl", 42, "request-1"), cursors[0])

    def test_alfred_mode_invokes_engine_with_expected_flags(self):
        invocations = []
        snapshots = []

        service = ProcessClaudeHook(
            raw_adapter=FakeRawAdapter(),
            append_events=lambda path, events: None,
            write_cursor=lambda path, transcript, offset, request: None,
            write_policy_snapshot=lambda payload, active: snapshots.append((payload, active)),
            run_engine=lambda invocation: invocations.append(invocation) or EngineRunResult(0),
        )

        result = service.execute(
            ProcessClaudeHookCommand({"session_id": "session-1"}, {"state_path": "unused"}, context(mode="alfred"))
        )

        self.assertEqual((), result.messages)
        self.assertEqual(1, len(snapshots))
        args = invocations[0].args
        self.assertIn("--transcript-path", args)
        self.assertIn("transcript.jsonl", args)
        self.assertIn("--cursor-path", args)
        self.assertIn("alfred-cursor.json", args)
        self.assertIn("--session-id", args)
        self.assertIn("session-1", args)
        self.assertIn("--run-id", args)
        self.assertIn("run-1", args)

    def test_alfred_mode_reports_warning_when_no_target_is_configured(self):
        service = ProcessClaudeHook(
            raw_adapter=FakeRawAdapter(),
            append_events=lambda path, events: None,
            write_cursor=lambda path, transcript, offset, request: None,
            write_policy_snapshot=lambda payload, active: None,
            run_engine=lambda invocation: EngineRunResult(0),
        )

        result = service.execute(
            ProcessClaudeHookCommand({}, {}, context(mode="alfred", state_path="", obs_log=""))
        )

        self.assertEqual(1, len(result.messages))
        self.assertIn("skipping Alfred log", result.messages[0])

    def test_failures_are_reported_as_messages_instead_of_raising(self):
        service = ProcessClaudeHook(
            raw_adapter=FakeRawAdapter(fail=True),
            append_events=lambda path, events: None,
            write_cursor=lambda path, transcript, offset, request: None,
            write_policy_snapshot=lambda payload, active: None,
            run_engine=lambda invocation: EngineRunResult(1, stdout="", stderr="engine failed"),
        )

        result = service.execute(ProcessClaudeHookCommand({}, {}, context()))

        self.assertEqual(2, len(result.messages))
        self.assertIn("alfred-usage-hook raw: raw failed", result.messages)
        self.assertIn("alfred-usage-hook: engine failed", result.messages)


if __name__ == "__main__":
    unittest.main()
