import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
FIXTURE_HUB = ROOT / "examples" / "memory-fixtures" / "hub"


def load():
    path = ROOT / "scripts" / "workflow" / "generate-memory-index.py"
    spec = importlib.util.spec_from_file_location("gen_memory", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GM = load()


class GenerateMemoryIndexTests(unittest.TestCase):
    def test_index_is_deterministic_and_matches_fixture(self):
        generated = GM.render_index(FIXTURE_HUB)
        committed = (FIXTURE_HUB / "005-memory.md").read_text(encoding="utf-8")
        self.assertEqual(generated, committed)  # drift check

    def test_index_is_sorted_and_typed(self):
        generated = GM.render_index(FIXTURE_HUB)
        # sorted by filename: devin-usage-quota before parallel-run-rollback
        self.assertLess(generated.index("devin-usage-quota"),
                        generated.index("parallel-run-rollback"))
        self.assertIn("🔴 gotcha", generated)
        self.assertIn("🔵 decision", generated)

    def test_missing_required_key_fails(self):
        obs = GM.parse_frontmatter(FIXTURE_HUB / "memory" / "devin-usage-quota.md")
        for key in ("id", "type", "title", "date"):
            self.assertIn(key, obs)


if __name__ == "__main__":
    unittest.main()
