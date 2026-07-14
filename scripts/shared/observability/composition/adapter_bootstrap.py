from shared.observability.application.ports.adapters import AdapterRegistry
from shared.observability.infrastructure.adapters.ccusage.session import CcusageSessionAdapter
from shared.observability.infrastructure.adapters.claude.transcript import ClaudeTranscriptAdapter
from shared.observability.infrastructure.adapters.codex.hook import CodexHookAdapter
from shared.observability.infrastructure.adapters.codex.otel import CodexOtelAdapter
from shared.observability.infrastructure.adapters.devin.consumption import DevinConsumptionAdapter
from shared.observability.infrastructure.adapters.devin.insights import DevinInsightsAdapter
from shared.observability.infrastructure.adapters.generic.jsonl import GenericJsonlAdapter


def build_default_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register("generic", "jsonl", GenericJsonlAdapter)
    registry.register("claude-code", "host_transcript", ClaudeTranscriptAdapter)
    registry.register("claude-code", "ccusage", CcusageSessionAdapter)
    registry.register("codex", "ccusage", CcusageSessionAdapter)
    return registry


def build_experimental_registry() -> AdapterRegistry:
    registry = build_default_registry()
    registry.register("codex", "hook", CodexHookAdapter, experimental=True)
    registry.register("codex", "otel", CodexOtelAdapter, experimental=True)
    registry.register("devin-cli", "devin_insights", DevinInsightsAdapter, experimental=True)
    registry.register("devin-web", "devin_consumption", DevinConsumptionAdapter, experimental=True)
    return registry
