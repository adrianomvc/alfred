import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.context_manifest import (  # noqa: E402
    ContextManifestError,
    build_manifest,
    normalize_phase,
    normalize_slug,
)


class ContextManifestTests(unittest.TestCase):
    def test_normalization_helpers_preserve_current_aliases(self):
        self.assertEqual("validation", normalize_phase("Validate"))
        self.assertEqual("operations", normalize_phase("Operation"))
        self.assertEqual("safe-mode", normalize_slug("SAFE_MODE"))

    def test_build_manifest_keeps_cache_friendly_prefix(self):
        manifest = build_manifest(
            ROOT,
            phase="Design",
            lane="Standard",
            demand_type="product",
            agent="spec-design",
            sub_activity="functional-design",
        )

        self.assertEqual([
            "core/principles.md",
            "rules/README.md",
            "rules/rules-index.md",
            "rules/common/overconfidence.md",
        ], manifest[:4])

    def test_build_manifest_reports_missing_root_as_domain_error(self):
        with self.assertRaises(ContextManifestError):
            build_manifest(
                ROOT / "missing-root",
                phase="Design",
                lane="Standard",
                demand_type="product",
                agent="spec-design",
            )


if __name__ == "__main__":
    unittest.main()
