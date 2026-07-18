import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


ADVISOR = load("context_read_advisor", "scripts/workflow/context-read-advisor.py")
BENCH = load("context_benchmark", "scripts/metrics/evaluate-context-benchmark.py")


class ContextEfficiencyTests(unittest.TestCase):
    def test_small_file_bypasses_advisor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "small.py"; path.write_text("x = 1\n", encoding="utf-8")
            self.assertIsNone(ADVISOR.advice(path))

    def test_large_file_is_advisory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large.py"; path.write_text("x" * 7000, encoding="utf-8")
            text = ADVISOR.advice(path)
            self.assertIn("advisory", text)
            self.assertIn("current source", text)

    def test_benchmark_requires_fifteen_correct_cases(self):
        records = []
        for index in range(15):
            expected = [f"symbol-{index}"]
            records.extend([
                {"provider": "baseline", "case_id": str(index), "tokens": 1000},
                {"provider": "structural", "case_id": str(index), "tokens": 500,
                 "expected_targets": expected, "found_targets": expected,
                 "correct": True, "complete": True},
            ])
        result = BENCH.evaluate(records)["structural"]
        self.assertTrue(result["eligible"])
        self.assertEqual(result["median_token_reduction_pct"], 50.0)


if __name__ == "__main__":
    unittest.main()
