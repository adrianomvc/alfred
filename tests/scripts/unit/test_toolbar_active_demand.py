import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.toolbar.active_demand import active_demand_path, active_demand_payload, register_active_demand  # noqa: E402


class ToolbarActiveDemandTests(unittest.TestCase):
    def test_active_demand_path_uses_runtime_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(Path(tmp) / "active-demand.json", active_demand_path({"ALFRED_RUNTIME_DIR": tmp}))

    def test_payload_maps_state_fields_and_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "001-state.md"
            state.write_text("- id: demand-1\n- initiative id: init-1\n- sigla: ABC\n", encoding="utf-8")

            payload = active_demand_payload(state, state.read_text(encoding="utf-8").splitlines(), {"ALFRED_HOST": "host-x"})

            self.assertEqual("alfred.runtime.active-demand.v1", payload["schema_version"])
            self.assertEqual("demand-1", payload["demand_id"])
            self.assertEqual("init-1", payload["initiative_id"])
            self.assertEqual("host-x", payload["host"])
            self.assertTrue(payload["observability_log"].endswith("05-operation\\011-observability-log.jsonl") or payload["observability_log"].endswith("05-operation/011-observability-log.jsonl"))

    def test_register_active_demand_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "hub" / "001-state.md"
            state.parent.mkdir()
            state.write_text("- id: demand-1\n", encoding="utf-8")
            runtime = Path(tmp) / "runtime"

            target = register_active_demand(
                state,
                state.read_text(encoding="utf-8").splitlines(),
                {"ALFRED_RUNTIME_DIR": str(runtime)},
            )

            self.assertEqual(runtime / "active-demand.json", target)
            payload = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual("demand-1", payload["demand_id"])


if __name__ == "__main__":
    unittest.main()
