import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_alfred_boot():
    script = ROOT / "scripts" / "workflow" / "alfred-boot.py"
    spec = importlib.util.spec_from_file_location("alfred_boot", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["alfred_boot"] = module
    spec.loader.exec_module(module)
    return module


class AlfredBootTests(unittest.TestCase):
    def test_render_resume_preview_delegates_to_shared_toolbar_service(self):
        module = load_alfred_boot()
        calls = []

        def fake_render_toolbar(state_path, *, framework_root, model, cost):
            calls.append((state_path, framework_root, model, cost))
            return ["preview"]

        original = module.render_toolbar
        try:
            module.render_toolbar = fake_render_toolbar
            lines = module.render_resume_preview({"Path": "state.md"}, "GPT-5", "n/a")
        finally:
            module.render_toolbar = original

        self.assertEqual(["preview"], lines)
        self.assertEqual(("state.md", module.FRAMEWORK_ROOT, "GPT-5", "n/a"), calls[0])


if __name__ == "__main__":
    unittest.main()
