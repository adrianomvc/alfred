import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.common import read_lines  # noqa: E402
from shared.toolbar.state import parse_toolbar_state  # noqa: E402
from shared.toolbar.summary import numeric_cost_text, toolbar_state_fields  # noqa: E402


class ToolbarSummaryTests(unittest.TestCase):
    def test_numeric_cost_text_extracts_decimal_cost(self):
        self.assertEqual("12.34", numeric_cost_text("USD 12,34"))
        self.assertEqual("7.5", numeric_cost_text("cost=7.5"))
        self.assertEqual("", numeric_cost_text("n/a"))

    def test_toolbar_state_fields_preserve_existing_state_and_manual_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "001-state.md"
            state.write_text(
                "\n".join([
                    "- id: demand-1",
                    "- sigla: ABC",
                    "- lane: Standard",
                    "- current phase: Design",
                    "- cost usd: 99",
                    "- usage-cost: legacy",
                ]),
                encoding="utf-8",
            )

            toolbar_state = parse_toolbar_state(read_lines(state))
            fields = toolbar_state_fields(state, toolbar_state, cost="USD 12.34", cost_usd="15")

            self.assertEqual("99", fields["cost usd"])
            self.assertEqual("legacy", fields["usage-cost"])
            self.assertEqual("manual", fields["cost source"])

    def test_toolbar_state_fields_add_manual_cost_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "001-state.md"
            state.write_text("- id: demand-1\n- sigla: ABC\n- lane: FAST\n", encoding="utf-8")

            toolbar_state = parse_toolbar_state(read_lines(state))
            fields = toolbar_state_fields(state, toolbar_state, cost="USD 12,34")

            self.assertEqual("12.34", fields["cost usd"])
            self.assertEqual("manual", fields["cost source"])
            self.assertEqual("session", fields["cost granularity"])


if __name__ == "__main__":
    unittest.main()
