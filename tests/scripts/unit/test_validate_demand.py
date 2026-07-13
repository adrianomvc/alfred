import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))


def load_validator():
    script = ROOT / "scripts" / "validators" / "validate-demand.py"
    spec = importlib.util.spec_from_file_location("validate_demand_script", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_demand_script"] = module
    spec.loader.exec_module(module)
    return module


def args(**overrides):
    values = {
        "hub_demand_path": str(ROOT / "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/006-simulado-adocao-v2"),
        "app_demand_path": str(ROOT / "examples/sq9-pilot/.alfred-docs-app/iniciativa-001-piloto/006-simulado-adocao-v2"),
        "app_repo_path": "",
        "app_current_commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "strict": True,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class ValidateDemandTests(unittest.TestCase):
    def test_validate_demand_returns_structured_report_for_strict_example(self):
        module = load_validator()

        result = module.validate_demand(args())

        self.assertTrue(result.report.passed)
        self.assertEqual("", result.failure_message)
        self.assertIn("OK path 001-state.md", result.report.successes)
        self.assertIn(
            "Demand validation completed. errors=0, warnings=0, strict=True",
            result.output,
        )

    def test_missing_state_returns_report_without_raising(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            result = module.validate_demand(args(hub_demand_path=tmp, app_demand_path="", strict=False))

        self.assertFalse(result.report.passed)
        self.assertEqual("Cannot validate demand without 001-state.md", result.failure_message)
        self.assertEqual("missing_path", result.report.issues[0].code)


if __name__ == "__main__":
    unittest.main()
