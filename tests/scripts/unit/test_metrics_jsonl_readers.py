import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))


def load_script(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MetricsJsonlReaderTests(unittest.TestCase):
    def test_apply_usage_rate_card_rejects_invalid_jsonl(self):
        module = load_script("apply_usage_rate_card_cli", "scripts/metrics/apply-usage-rate-card.py")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.jsonl"
            path.write_text("{bad json\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                list(module.iter_events(path))

    def test_transcript_auxiliary_readers_skip_invalid_jsonl_lines(self):
        module = load_script("attribute_usage_transcript_cli", "scripts/metrics/attribute-usage-transcript.py")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text(
                "{bad json\n"
                '{"event_type":"usage_attributed","event_scope":"request","request_id":"req-1"}\n',
                encoding="utf-8",
            )

            self.assertEqual({"req-1"}, module.already_attributed_request_ids(path))
            self.assertEqual(1, len(module.existing_usage_events(path)))

    def test_metric_rollup_and_insights_readers_keep_source_metadata(self):
        rollup = load_script("generate_metrics_rollup_cli", "scripts/metrics/generate-metrics-rollup.py")
        insights = load_script("generate_metrics_insights_cli", "scripts/metrics/generate-metrics-insights.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "011-observability-log.jsonl"
            log.write_text(
                '{"event_id":"e1","event_type":"usage_attributed","ts":"2026-07-12T10:00:00Z","sequence":2}\n',
                encoding="utf-8",
            )

            rollup_events = rollup.read_events(root)
            insight_events = insights.read_events(root)

            self.assertEqual(str(log), rollup_events[0]["_source_file"])
            self.assertEqual(1, rollup_events[0]["_source_line"])
            self.assertEqual(str(log), insight_events[0]["_source_file"])
            self.assertEqual(1, insight_events[0]["_source_line"])

    def test_metric_readers_reject_invalid_jsonl(self):
        collect = load_script("collect_observability_cli", "scripts/metrics/collect-observability.py")
        rollup = load_script("generate_metrics_rollup_cli_invalid", "scripts/metrics/generate-metrics-rollup.py")
        insights = load_script("generate_metrics_insights_cli_invalid", "scripts/metrics/generate-metrics-insights.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "011-observability-log.jsonl"
            log.write_text("{bad json\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                collect.collect_events(root)
            with self.assertRaises(SystemExit):
                rollup.read_events(root)
            with self.assertRaises(SystemExit):
                insights.read_events(root)


if __name__ == "__main__":
    unittest.main()
