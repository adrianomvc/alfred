import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.observability.domain.services.interaction_context import (  # noqa: E402
    interaction_context,
    tool_counters,
)


def tool(name, is_error=False, **inp):
    return {"tool_name": name, "is_error": is_error, "input": inp}


class InteractionContextTests(unittest.TestCase):
    def test_counts_calls_and_failures(self):
        obs = [tool("Read", file_path="a.py"), tool("Bash", command="ls", is_error=True), tool("Grep", pattern="x", path="b.md")]
        calls, failures = tool_counters(obs)
        self.assertEqual(3, calls)
        self.assertEqual(1, failures)

    def test_classifies_reads_and_counts_repeats(self):
        obs = [
            tool("Read", file_path="rules/common/foo.md"),
            tool("Read", file_path="src/app.py"),
            tool("Read", file_path="src/app.py"),      # repeat
            tool("Read", file_path="skills/dataviz/SKILL.md"),
            tool("Grep", pattern="x", path="run.log"),
            tool("Bash", command="echo hi"),            # not a read
        ]
        ctx = interaction_context(obs)
        self.assertEqual(4, ctx["unique_artifacts_read"])
        self.assertEqual(1, ctx["framework_rules_read"])
        self.assertEqual(1, ctx["skills_loaded"])
        self.assertEqual(1, ctx["source_files_read"])
        self.assertEqual(1, ctx["logs_read"])
        self.assertEqual(1, ctx["repeated_reads"])

    def test_rtk_detected_and_unexposed_fields_stay_none(self):
        ctx = interaction_context([tool("Bash", command="rtk git status")])
        self.assertTrue(ctx["rtk_used"])
        self.assertIsNone(ctx["total_bytes_read"])
        self.assertIsNone(ctx["compression_used"])

    def test_empty_is_all_zero_not_none(self):
        ctx = interaction_context([])
        self.assertEqual(0, ctx["unique_artifacts_read"])
        self.assertFalse(ctx["rtk_used"])
        self.assertEqual((0, 0), tool_counters([]))


if __name__ == "__main__":
    unittest.main()
