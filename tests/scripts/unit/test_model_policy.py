import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.model_policy import describe_model, model_advisory, resolve_model_policy  # noqa: E402


class ModelPolicyResolverTests(unittest.TestCase):
    def test_floor_plus_adjustment_highest_wins(self):
        self.assertEqual("medium", resolve_model_policy("Standard", "Execution").tier)
        self.assertEqual("strong", resolve_model_policy("SAFE", "Execution").tier)
        # Execution never runs on cheap, even in FAST.
        self.assertEqual("medium", resolve_model_policy("FAST", "Execution").tier)

    def test_design_pinned_strong_all_lanes(self):
        for lane in ("FAST", "Standard", "SAFE"):
            self.assertEqual("strong", resolve_model_policy(lane, "Design").tier)

    def test_inception_is_lane_specific(self):
        self.assertEqual("strong", resolve_model_policy("FAST", "Inception").tier)
        self.assertEqual("medium", resolve_model_policy("Standard", "Inception").tier)
        self.assertEqual("strong", resolve_model_policy("SAFE", "Inception").tier)

    def test_operate_floor_exception(self):
        # Operate may drop to medium even in SAFE, and cheap only in FAST.
        self.assertEqual("medium", resolve_model_policy("SAFE", "Operation").tier)
        self.assertEqual("cheap", resolve_model_policy("FAST", "Operation").tier)

    def test_concrete_model_and_effort(self):
        d = resolve_model_policy("Standard", "Design")
        self.assertEqual("claude-opus-4-8", d.model)
        self.assertEqual("xhigh", d.effort)
        self.assertIsNone(d.task_budget)
        e = resolve_model_policy("Standard", "Execution")
        self.assertEqual(20000, e.task_budget)

    def test_unknown_lane_or_phase_returns_none(self):
        self.assertIsNone(resolve_model_policy("unknown", "Design"))
        self.assertIsNone(resolve_model_policy("SAFE", "unknown"))
        self.assertIsNone(describe_model("", "unknown", "unknown"))

    def test_describe_model_shows_actual_running_model(self):
        # actual matches the policy target -> compact
        self.assertEqual(
            "claude-opus-4-8 · strong · esf xhigh",
            describe_model("claude-opus-4-8", "SAFE", "Design"),
        )

    def test_describe_model_flags_when_actual_differs_from_target(self):
        # forced but not switched: show the ACTUAL model, flag the policy target
        text = describe_model("claude-sonnet-5", "SAFE", "Design")
        self.assertIn("claude-sonnet-5", text)
        self.assertIn("política: claude-opus-4-8", text)

    def test_describe_model_marks_target_unconfirmed_when_actual_unknown(self):
        text = describe_model("default", "SAFE", "Design")
        self.assertIn("claude-opus-4-8", text)
        self.assertIn("não confirmado", text)

    def test_advisory_none_when_aligned_or_unresolvable(self):
        self.assertIsNone(model_advisory("claude-opus-4-8", "SAFE", "Design"))
        self.assertIsNone(model_advisory("anything", "unknown", "unknown"))

    def test_advisory_nudges_switch_when_diverging(self):
        msg = model_advisory("claude-sonnet-5", "SAFE", "Design")
        self.assertIn("claude-opus-4-8", msg)
        self.assertIn("claude-sonnet-5", msg)
        self.assertIn("/model", msg)

    def test_advisory_when_actual_unknown_still_invites_switch(self):
        msg = model_advisory("", "SAFE", "Design")
        self.assertIn("claude-opus-4-8", msg)
        self.assertIn("/model", msg)


if __name__ == "__main__":
    unittest.main()
