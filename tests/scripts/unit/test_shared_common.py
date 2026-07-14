import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.common import get_field, iter_jsonl, normalize_phase, phase_number, read_state_fields  # noqa: E402


class SharedCommonTests(unittest.TestCase):
    def test_markdown_field_trims_backticks(self):
        lines = ["- id: `abc-123`", "- lane: Standard"]

        self.assertEqual("abc-123", get_field(lines, "id"))
        self.assertEqual("Standard", get_field(lines, ["modo", "lane"]))

    def test_state_parser_lowercases_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "001-state.md"
            path.write_text("- Current Phase: Execution\n- Lane: SAFE\n", encoding="utf-8")

            self.assertEqual(
                {"current phase": "Execution", "lane": "SAFE"},
                read_state_fields(path),
            )

    def test_iter_jsonl_reports_invalid_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text('{"ok": true}\n\n{bad json}\n', encoding="utf-8")

            rows = list(iter_jsonl(path))

        self.assertEqual(2, len(rows))
        self.assertEqual(1, rows[0][0])
        self.assertEqual({"ok": True}, rows[0][1])
        self.assertEqual(3, rows[1][0])
        self.assertIsNone(rows[1][1])

    def test_lifecycle_phase_helpers(self):
        self.assertEqual("validate", normalize_phase("Validation"))
        self.assertEqual(4, phase_number("Validation"))
        self.assertEqual(0, phase_number("unknown"))


if __name__ == "__main__":
    unittest.main()
