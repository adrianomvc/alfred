import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))


def load_validator():
    script = ROOT / "scripts" / "validators" / "validate-tool-discovery-policy.py"
    spec = importlib.util.spec_from_file_location("validate_tool_discovery_policy", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_tool_discovery_policy"] = module
    spec.loader.exec_module(module)
    return module


class ValidateToolDiscoveryPolicyTests(unittest.TestCase):
    def test_validate_current_policy_passes(self):
        module = load_validator()
        report = module.validate_tool_discovery_policy(ROOT)

        self.assertTrue(report.passed)
        self.assertIn("OK MCP tool descriptions 4 tools", report.successes)

    def test_tool_description_limit_returns_structured_issue(self):
        module = load_validator()
        issues = []
        successes = []

        module.validate_tool_descriptions([
            {
                "name": "long_tool",
                "description": "word " * (module.MAX_TOOL_DESCRIPTION_WORDS + 1),
                "inputSchema": {"properties": {}},
            }
        ], issues, successes)

        self.assertEqual("tool_discovery.tool_description_too_long", issues[0].code)


if __name__ == "__main__":
    unittest.main()
