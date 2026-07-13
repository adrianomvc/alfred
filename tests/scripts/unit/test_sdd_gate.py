import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.sdd_gate import has_useful_content, run  # noqa: E402


HUB_DEMAND = ROOT / "examples" / "sq9-pilot" / "alfred-docs-hub" / "iniciativa-001-piloto" / "006-simulado-adocao-v2"
APP_DEMAND = ROOT / "examples" / "sq9-pilot" / ".alfred-docs-app" / "iniciativa-001-piloto" / "006-simulado-adocao-v2"


class SddGateTests(unittest.TestCase):
    def test_has_useful_content_detects_current_problem_file(self):
        self.assertTrue(has_useful_content(HUB_DEMAND / "01-inception" / "002-problem.md"))

    def test_run_current_fixture_passes_non_strict(self):
        output, errors, warnings, failed = run(HUB_DEMAND, APP_DEMAND, strict=False)

        self.assertFalse(failed)
        self.assertEqual([], errors)
        self.assertIn("OK content problem", output)
        self.assertTrue(output[-1].startswith("SDD gate completed."))


if __name__ == "__main__":
    unittest.main()
