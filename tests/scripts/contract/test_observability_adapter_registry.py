import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.observability.application.ports.adapters import (  # noqa: E402
    ObservabilityAdapter,
    SessionUsageAdapter,
    TranscriptUsageAdapter,
)
from shared.observability.composition.adapter_bootstrap import (  # noqa: E402
    build_default_registry,
    build_experimental_registry,
)


PASSTHROUGH_KEYS = {
    ("codex", "hook"),
    ("codex", "otel"),
    ("devin-cli", "devin_insights"),
    ("devin-web", "devin_consumption"),
}


class ObservabilityAdapterRegistryTests(unittest.TestCase):
    def test_default_registry_excludes_passthrough_adapters(self):
        registry = build_default_registry()

        self.assertFalse(PASSTHROUGH_KEYS.intersection(registry.registered()))
        self.assertIsInstance(registry.resolve("generic", "jsonl"), ObservabilityAdapter)
        self.assertIsInstance(registry.resolve("claude-code", "host_transcript"), TranscriptUsageAdapter)
        self.assertIsInstance(registry.resolve("claude-code", "ccusage"), SessionUsageAdapter)

    def test_experimental_registry_marks_passthrough_adapters(self):
        registry = build_experimental_registry()

        registered = set(registry.registered(include_experimental=True))
        self.assertTrue(PASSTHROUGH_KEYS.issubset(registered))
        for host, source_kind in PASSTHROUGH_KEYS:
            self.assertTrue(registry.is_experimental(host, source_kind))


if __name__ == "__main__":
    unittest.main()
