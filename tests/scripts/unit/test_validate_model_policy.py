import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))


def load_validator():
    script = ROOT / "scripts" / "validators" / "validate-model-policy.py"
    spec = importlib.util.spec_from_file_location("validate_model_policy", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_model_policy"] = module
    spec.loader.exec_module(module)
    return module


class ValidateModelPolicyTests(unittest.TestCase):
    def test_validate_model_policy_returns_structured_missing_file_issue(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            report = module.validate_model_policy(tmp)

        self.assertFalse(report.passed)
        self.assertEqual("model_policy.missing", report.issues[0].code)
        self.assertIn("Missing model policy", report.issues[0].message)

    def test_validate_model_policy_current_repo_passes_with_success_messages(self):
        module = load_validator()
        report = module.validate_model_policy(ROOT)

        self.assertTrue(report.passed)
        self.assertIn("OK heading Selection rule", report.successes)
        self.assertIn("OK policy toolbar declares current model", report.successes)


if __name__ == "__main__":
    unittest.main()
