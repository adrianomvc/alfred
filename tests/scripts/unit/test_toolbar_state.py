import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.common import read_lines  # noqa: E402
from shared.toolbar.state import EXECUTION_FIRST_PHASES, parse_toolbar_state  # noqa: E402


class ToolbarStateTests(unittest.TestCase):
    def test_standard_state_parses_fields_markers_and_progress(self):
        state = parse_toolbar_state(read_lines(ROOT / "examples/toolbar-states/standard.md"))

        self.assertEqual("toolbar-standard", state.demand_id)
        self.assertEqual("TST", state.sigla)
        self.assertEqual("Standard", state.lane)
        self.assertEqual("Execution", state.phase)
        self.assertEqual("unit loop", state.step)
        self.assertEqual("Tech Lead", state.checkpoint)
        self.assertEqual(40, state.progress)
        self.assertEqual(
            (
                ("Inception", "x"),
                ("Design", "x"),
                ("Execution", ">"),
                ("Validate", " "),
                ("Operation", " "),
            ),
            state.markers,
        )

    def test_execution_first_state_uses_special_phase_track(self):
        state = parse_toolbar_state(read_lines(ROOT / "examples/toolbar-states/execution-first.md"))

        self.assertEqual(EXECUTION_FIRST_PHASES, state.phases)
        self.assertEqual(60, state.progress)
        self.assertEqual(("Validate posterior", ">"), state.markers[3])


if __name__ == "__main__":
    unittest.main()
