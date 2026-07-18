import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


BLUEPRINT = load("devin_blueprint", "scripts/validators/validate-devin-blueprint.py")
CONTEXT_HOOK = load("devin_context_hook", "scripts/workflow/devin-context-hook.py")


class DevinHardeningTests(unittest.TestCase):
    def test_repo_command_rejected_above_repo_tier(self):
        self.assertTrue(BLUEPRINT.validate("maintenance:\n  run: npm install\n", "enterprise"))
        self.assertFalse(BLUEPRINT.validate("maintenance:\n  run: npm install\n", "repository"))

    def test_literal_secret_rejected(self):
        self.assertTrue(BLUEPRINT.validate("API_TOKEN: abc123\n", "repository"))
        self.assertFalse(BLUEPRINT.validate("API_TOKEN: ${API_TOKEN}\n", "repository"))

    def test_context_hook_reanchors_existing_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); runtime = root / "runtime"; runtime.mkdir()
            state = root / "hub/demand/001-state.md"; state.parent.mkdir(parents=True)
            state.write_text("# state\n", encoding="utf-8")
            (runtime / "active-demand.json").write_text(json.dumps({"state_path": str(state), "demand_id": "d-1"}), encoding="utf-8")
            old = os.environ.get("ALFRED_RUNTIME_DIR"); os.environ["ALFRED_RUNTIME_DIR"] = str(runtime)
            try:
                self.assertIn(str(state), CONTEXT_HOOK.context_for_active_demand())
            finally:
                if old is None: os.environ.pop("ALFRED_RUNTIME_DIR", None)
                else: os.environ["ALFRED_RUNTIME_DIR"] = old


if __name__ == "__main__":
    unittest.main()
