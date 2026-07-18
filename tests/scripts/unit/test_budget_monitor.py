import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))


def load():
    path = ROOT / "scripts" / "metrics" / "budget-monitor.py"
    spec = importlib.util.spec_from_file_location("budget_monitor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BM = load()


def state(limit="40", demand_acu="20", near="80"):
    tmp = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write(
        "# s\n## Budget\n"
        f"- budget limit: {limit}\n- budget near threshold: {near}\n"
        "- budget on limit: pause-and-ask\n- budget status:\n"
        "## Host Adapters\n"
        f"- demand acu: {demand_acu}\n"
        "## Checklist\n- [x] Inception\n- [x] Design\n- [ ] Execution\n- [ ] Validate\n- [ ] Operation\n"
    )
    tmp.close()
    return Path(tmp.name)


class EvaluateTests(unittest.TestCase):
    def test_within(self):
        r = BM.evaluate(state(demand_acu="20"))
        self.assertEqual(r["status"], "within")
        self.assertEqual(r["pct"], 50.0)
        self.assertEqual(r["delivered_phases"], "2/5")

    def test_near(self):
        self.assertEqual(BM.evaluate(state(demand_acu="34"))["status"], "near")

    def test_exceeded(self):
        r = BM.evaluate(state(demand_acu="42"))
        self.assertEqual(r["status"], "exceeded")
        self.assertEqual(r["remaining"], -2.0)

    def test_no_budget(self):
        self.assertEqual(BM.evaluate(state(limit=""))["status"], "no-budget")

    def test_unmeasurable_without_consumption(self):
        # demand acu absent
        tmp = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        tmp.write("# s\n## Budget\n- budget limit: 40\n## Checklist\n- [x] Inception\n")
        tmp.close()
        self.assertEqual(BM.evaluate(Path(tmp.name))["status"], "unmeasurable")


if __name__ == "__main__":
    unittest.main()
