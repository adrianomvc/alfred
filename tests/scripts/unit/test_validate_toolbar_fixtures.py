import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))


def load_validator():
    script = ROOT / "scripts" / "validators" / "validate-toolbar-fixtures.py"
    spec = importlib.util.spec_from_file_location("validate_toolbar_fixtures", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_toolbar_fixtures"] = module
    spec.loader.exec_module(module)
    return module


class ValidateToolbarFixturesTests(unittest.TestCase):
    def test_validate_current_toolbar_fixtures_passes(self):
        module = load_validator()
        report = module.validate_toolbar_fixtures(ROOT)

        self.assertTrue(report.passed)
        self.assertIn("OK toolbar fixture fast", report.successes)
        self.assertIn("OK toolbar fixture standard-parallel-units", report.successes)

    def test_missing_fixture_state_returns_structured_issue(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            report = module.validate_toolbar_fixtures(tmp)

        self.assertFalse(report.passed)
        self.assertEqual("toolbar_fixture.state_missing", report.issues[0].code)


if __name__ == "__main__":
    unittest.main()
