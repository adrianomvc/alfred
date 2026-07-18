import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("migrate_state_v2", ROOT / "scripts/workflow/migrate-state-v2.py")
MS = importlib.util.module_from_spec(spec); spec.loader.exec_module(MS)


class MigrateStateTests(unittest.TestCase):
    def test_migrates_and_is_idempotent(self):
        old = "# state\n## Host Adapters\n- usage acu cycle: 10/180\n- demand acu: 3\n"
        migrated, legacy, errors = MS.migrate_content(old)
        self.assertFalse(errors)
        self.assertIn("- usage schema: alfred.usage.v2", migrated)
        self.assertIn("- usage demand consumed: 3", migrated)
        again, legacy_again, errors_again = MS.migrate_content(migrated)
        self.assertEqual(migrated, again)
        self.assertFalse(legacy_again or errors_again)

    def test_ambiguous_hundred_limit_requires_unit(self):
        for limit in ("100", "100.0", "100.00"):
            old = f"# state\n- usage acu cycle: 98/{limit}\n"
            _, _, errors = MS.migrate_content(old)
            self.assertTrue(errors)
            migrated, _, errors = MS.migrate_content(old, "quota_percent")
            self.assertFalse(errors)
            self.assertIn("- usage unit: quota_percent", migrated)


if __name__ == "__main__":
    unittest.main()
