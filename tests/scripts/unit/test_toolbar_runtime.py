import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.toolbar.runtime import (  # noqa: E402
    format_framework,
    read_app_commit,
    resolve_framework_display,
    resolve_path,
    short_commit,
)


class ToolbarRuntimeTests(unittest.TestCase):
    def test_short_commit_normalizes_unknown_values(self):
        self.assertEqual("unknown", short_commit(""))
        self.assertEqual("unknown", short_commit("not-git"))
        self.assertEqual("abcdef1", short_commit("abcdef123456"))

    def test_format_framework_prefixes_version_and_shortens_commit(self):
        self.assertEqual("v2.0.0 (abcdef1)", format_framework("2.0.0", "abcdef123456"))
        self.assertEqual("v2.0.0 (unknown)", format_framework("v2.0.0", "unknown"))

    def test_resolve_framework_display_uses_local_version_when_not_stamped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "VERSION").write_text("9.9.9\n", encoding="utf-8")

            self.assertEqual("v9.9.9 (unknown)", resolve_framework_display(root))

    def test_read_app_commit_prefers_explicit_then_state_value(self):
        content = ["- app commit: 1234567890"]

        self.assertEqual("abcdef1", read_app_commit("state.md", content, explicit_app_commit="abcdef123"))
        self.assertEqual("1234567", read_app_commit("state.md", content))

    def test_read_app_commit_can_read_app_demand_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "hub" / "001-state.md"
            state.parent.mkdir()
            state.write_text("- id: demand\n", encoding="utf-8")
            app = root / "app"
            app.mkdir()
            (app / "001-index.md").write_text("- current commit: fedcba987654\n", encoding="utf-8")

            resolved = resolve_path("app", state, cwd=root)

            self.assertEqual(app.resolve(), resolved)
            self.assertEqual("fedcba9", read_app_commit(state, [], app_demand_path="app", cwd=root))


if __name__ == "__main__":
    unittest.main()
