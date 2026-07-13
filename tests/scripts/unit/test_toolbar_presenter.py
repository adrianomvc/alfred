import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.observability.presentation.toolbar_presenter import ToolbarViewModelBuilder as LegacyBuilder  # noqa: E402
from shared.toolbar.presenter import ToolbarViewModelBuilder  # noqa: E402
from shared.toolbar.renderers import render_text, render_web  # noqa: E402


class ToolbarPresenterTests(unittest.TestCase):
    def test_legacy_observability_import_reexports_toolbar_builder(self):
        self.assertIs(ToolbarViewModelBuilder, LegacyBuilder)

    def test_builder_without_summary_keeps_current_fallback_text(self):
        view_model = ToolbarViewModelBuilder().build(
            demand_id="001",
            sigla="ABC",
            lane="Standard",
            progress=0,
            framework="v2.0.0 (unknown)",
            app_commit="unknown",
            summary=None,
        )

        self.assertEqual("não coletado · adapter de uso não configurado", view_model.primary_usage_text)
        self.assertEqual("fonte de custo não configurada", view_model.cost_gap_text)
        self.assertIsNone(view_model.forecast_text)

    def test_text_renderer_keeps_ascii_fallback_shape(self):
        view_model = ToolbarViewModelBuilder().build(
            demand_id="001",
            sigla="ABC",
            lane="Fast",
            progress=20,
            framework="v2.0.0 (unknown)",
            app_commit="unknown",
            summary=None,
        )

        lines = render_text(
            "ABC", "001", "Fast", "Execution", "ship it", "step", "n/a",
            "GPT-5", 20, [("Execution", ">")], "v2.0.0 (unknown)", "unknown",
            view_model,
        )

        self.assertTrue(lines[0].startswith("ALFRED | ABC | #001 | FAST | Execution | 20%"))
        self.assertIn("Custo USD: indisponível", lines[0])

    def test_web_renderer_escapes_title_values(self):
        lines = render_web("A&B", "001<bad>", "Safe", "next", "step", 0, [])

        self.assertIn("A&amp;B", lines[0])
        self.assertIn("001&lt;bad&gt;", lines[0])


if __name__ == "__main__":
    unittest.main()
