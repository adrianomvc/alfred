import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.email_tools import TOOLS  # noqa: E402


class EmailToolsTests(unittest.TestCase):
    def test_email_tool_catalog_keeps_expected_tools(self):
        names = {tool["name"] for tool in TOOLS}

        self.assertEqual({
            "send_email",
            "send_demand_report",
            "send_telemetry",
            "email_status",
        }, names)


if __name__ == "__main__":
    unittest.main()
