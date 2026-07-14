import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))


def load_validator():
    script = ROOT / "scripts" / "validators" / "validate-observability-hygiene.py"
    spec = importlib.util.spec_from_file_location("validate_observability_hygiene", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_observability_hygiene"] = module
    spec.loader.exec_module(module)
    return module


class ValidateObservabilityHygieneTests(unittest.TestCase):
    def test_check_log_returns_structured_issues(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "events.jsonl"
            log.write_text(
                json.dumps({
                    "ts": "<placeholder>",
                    "event_type": "usage_attributed",
                    "event_scope": "request",
                    "cost_usd": 1,
                    "artifacts_used": "bad",
                    "duration_ms": 0,
                }) + "\n",
                encoding="utf-8",
            )

            report_issues = module.check_log(log)

        codes = {item.code for item in report_issues}
        self.assertIn("observability_hygiene.invalid_ts", codes)
        self.assertIn("observability_hygiene.artifacts_used_not_list", codes)
        self.assertIn("observability_hygiene.request_id_missing", codes)
        self.assertIn("observability_hygiene.request_cost_inline", codes)
        self.assertIn("observability_hygiene.duration_zero", codes)

    def test_exact_duplicate_event_is_flagged_but_updated_reemit_is_not(self):
        module = load_validator()
        base = {
            "ts": "2026-07-12T10:00:00Z",
            "event_id": "interaction-completed-p1",
            "event_type": "interaction_completed",
            "usage": {"total_tokens": 100},
            "request_count": 1,
        }
        grown = dict(base, usage={"total_tokens": 300}, request_count=2)
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "events.jsonl"
            log.write_text(
                json.dumps(base) + "\n"
                + json.dumps(base) + "\n"      # exact repeat -> flagged
                + json.dumps(grown) + "\n",     # legitimate grown re-emit -> allowed
                encoding="utf-8",
            )
            issues = module.check_log(log)

        dup = [i for i in issues if i.code == "observability_hygiene.duplicate_event"]
        self.assertEqual(len(dup), 1)
        self.assertIn(":2", dup[0].message)

    def test_validate_current_repo_passes_and_reports_log_count(self):
        module = load_validator()
        report, log_count = module.validate_observability_hygiene(ROOT)

        self.assertTrue(report.passed)
        self.assertGreaterEqual(log_count, 1)


if __name__ == "__main__":
    unittest.main()
