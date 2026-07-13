import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.validation import Severity  # noqa: E402
from shared.validation.reverse_eng_staleness import (  # noqa: E402
    get_recorded_commit,
    validate_reverse_eng_staleness,
)


class ReverseEngStalenessTests(unittest.TestCase):
    def test_get_recorded_commit_reads_app_commit_field(self):
        self.assertEqual(
            "abcdef1234567",
            get_recorded_commit(["- app commit: `abcdef1234567`"]),
        )

    def test_current_commit_prefix_match_passes(self):
        result = validate_reverse_eng_staleness(
            ROOT / "examples/staleness-fixtures/reverse-eng-fresh.md",
            current_commit="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            strict=True,
        )

        self.assertTrue(result.report.passed)
        self.assertEqual("", result.failure_message)
        self.assertIn("OK reverse-eng fresh", result.output[0])

    def test_missing_commit_is_warning_when_not_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "reverse-eng.md"
            artifact.write_text("# Reverse eng\n", encoding="utf-8")

            result = validate_reverse_eng_staleness(artifact)

        self.assertTrue(result.report.passed)
        self.assertEqual(Severity.WARNING, result.report.issues[0].severity)
        self.assertIn("WARN missing_commit", result.output[0])

    def test_git_runner_is_used_when_repo_path_is_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / ".git").mkdir()
            artifact = Path(tmp) / "reverse-eng.md"
            artifact.write_text("- commit: abcdef1\n", encoding="utf-8")
            calls = []

            def fake_git_runner(args, **kwargs):
                calls.append((args, kwargs))
                return SimpleNamespace(stdout="abcdef1234567890\n")

            result = validate_reverse_eng_staleness(
                artifact,
                app_repo_path=str(repo),
                git_runner=fake_git_runner,
            )

        self.assertTrue(result.report.passed)
        self.assertEqual(1, len(calls))
        self.assertIn("OK reverse-eng fresh", result.output[0])


if __name__ == "__main__":
    unittest.main()
