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
    registry.register("codex", "hook", CodexHookAdapter)
    registry.register("codex", "otel", CodexOtelAdapter)
    registry.register("devin-cli", "devin_insights", DevinInsightsAdapter)
    registry.register("devin-web", "devin_consumption", DevinConsumptionAdapter)
    registry.register("claude-code", "ccusage", CcusageSessionAdapter)
    registry.register("codex", "ccusage", CcusageSessionAdapter)
    return registry

