import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))


def load_validator():
    script = ROOT / "scripts" / "validators" / "validate-context-manifest-fixtures.py"
    spec = importlib.util.spec_from_file_location("validate_context_manifest_fixtures", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_context_manifest_fixtures"] = module
    spec.loader.exec_module(module)
    return module


class ValidateContextManifestFixturesTests(unittest.TestCase):
    def test_validate_current_context_manifest_fixtures_passes(self):
        module = load_validator()
        report = module.validate_context_manifest_fixtures(ROOT)

        self.assertTrue(report.passed)
        self.assertIn("OK context manifest fixture standard-product-design", report.successes)
        self.assertIn("OK context manifest fixture safe-engineering-inception", report.successes)

    def test_missing_fixture_returns_structured_issue(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            report = module.validate_context_manifest_fixtures(tmp)

        self.assertFalse(report.passed)
        self.assertEqual("context_manifest_fixture.missing", report.issues[0].code)


if __name__ == "__main__":
    unittest.main()
