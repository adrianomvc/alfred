import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.common import read_state_fields, write_state_fields  # noqa: E402


def load_session_cost():
    path = ROOT / "scripts" / "metrics" / "session-cost.py"
    spec = importlib.util.spec_from_file_location("session_cost", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SC = load_session_cost()


class ParseUsageTests(unittest.TestCase):
    def test_parses_acu(self):
        self.assertEqual(SC.parse_usage("ACUs consumed: 129.42 of 180.00"),
                         ("acu", 129.42, 180.0))

    def test_parses_quota_used_colon(self):
        self.assertEqual(SC.parse_usage("Quota used: 98% (remaining: 2%)"),
                         ("quota-%", 98.0, 100.0))

    def test_parses_quota_percent_used(self):
        self.assertEqual(SC.parse_usage("98% used"), ("quota-%", 98.0, 100.0))

    def test_unparseable_returns_none(self):
        self.assertIsNone(SC.parse_usage("nothing here"))
        self.assertIsNone(SC.parse_usage(""))


class BuildResultTests(unittest.TestCase):
    def test_demand_delta_available_budget_and_usd(self):
        fields = {"usage acu demand baseline": "100.0", "budget limit": "40"}
        result = SC.build_result(fields, ("acu", 129.42, 180.0), None)
        self.assertEqual(result["demand"], 29.42)
        self.assertEqual(result["available_pct"], 28.1)
        self.assertEqual(result["budget_pct"], 73.6)
        self.assertEqual(result["confidence"], "estimated")
        self.assertNotIn("demand_usd", result)  # no rate card -> no USD

    def test_usd_only_from_rate_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = Path(tmp) / "rc.json"
            rc.write_text('{"acu": {"usd_per_acu": 2.0}}', encoding="utf-8")
            fields = {"usage acu demand baseline": "100.0"}
            result = SC.build_result(fields, ("acu", 129.42, 180.0), str(rc))
            self.assertEqual(result["demand_usd"], 58.84)

    def test_no_baseline_no_delta(self):
        result = SC.build_result({}, ("acu", 129.42, 180.0), None)
        self.assertIsNone(result["demand"])
        self.assertIsNone(result["session"])


class DisplayTextTests(unittest.TestCase):
    def test_compact_acu_line_without_usd_or_confidence(self):
        result = SC.build_result({"usage acu demand baseline": "100.0", "budget limit": "40"},
                                 ("acu", 129.42, 180.0), None)
        text = SC.display_text(result)
        self.assertIn("129.42/180.0 ACU", text)
        self.assertIn("28.1% disp", text)
        self.assertIn("demanda 29.42 (73.6% orc)", text)
        self.assertNotIn("US$", text)          # USD stays on the Custo line
        self.assertNotIn("estimated", text)


class WriteStateFieldsTests(unittest.TestCase):
    def test_updates_in_place_and_appends_to_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "001-state.md"
            state.write_text("# 001-state\n\n## Host Adapters\n- host: devin-cli\n- cost usd:\n",
                             encoding="utf-8")
            write_state_fields(state, {"cost usd": "58.84", "demand acu": "29.42"})
            fields = read_state_fields(state)
            self.assertEqual(fields["cost usd"], "58.84")   # updated in place
            self.assertEqual(fields["demand acu"], "29.42")  # appended to section


if __name__ == "__main__":
    unittest.main()
