import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.validation import Severity, ValidationIssue, ValidationReport  # noqa: E402


class ValidationModelsTests(unittest.TestCase):
    def test_report_passed_depends_on_error_issues(self):
        self.assertTrue(ValidationReport(()).passed)
        self.assertTrue(ValidationReport((
            ValidationIssue("warning", Severity.WARNING, "warning"),
        )).passed)
        self.assertFalse(ValidationReport((
            ValidationIssue("error", Severity.ERROR, "error"),
        )).passed)


if __name__ == "__main__":
    unittest.main()
