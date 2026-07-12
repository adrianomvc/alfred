# Observability Architecture

Alfred observability is host-agnostic. The framework stores canonical usage,
cost, tool, artifact, quality, and insight signals; host-specific logic lives at
the edges as adapters.

## Layers
- `scripts/python/observability/domain/`: typed models and pure services
  (`Usage`, `Cost`, artifact classification, cache ratio, forecast).
- `scripts/python/observability/application/`: ports and use cases. Business
  rules depend on abstractions, not Claude, Codex, Devin, filesystem, or
  subprocess.
- `scripts/python/observability/infrastructure/`: JSONL/summary repositories,
  clocks, subprocess runner, and thin host/source adapters.
- `scripts/python/observability/presentation/`: view models and renderers such
  as the toolbar presenter.
- Legacy scripts under `scripts/python/metrics/` and `scripts/python/workflow/`
  remain compatible entry points and should delegate into the layered package
  as they are touched.

## Adapter Rule
Adding a host/source means:
1. implement a small adapter for that source;
2. declare capabilities and gaps;
3. register it in the entry-point registry;
4. add fixtures/tests.

The domain, rollup, insights, lifecycle, and toolbar must not branch on host
names. Limited adapters return `None` plus capability gaps instead of inventing
tokens, ACU, credits, or cost.

## Cost Boundary
Session totals (`ccusage`, host-native `/cost`, or session exports) are valid
for state and toolbar display with scope/source/confidence. They are not demand
cost and must not drive demand forecasts.

Demand cost comes from:
- billing/export officially attributed to the demand;
- deduplicated `usage_cost_attributed` events;
- exact granular usage priced by an approved rate card;
- approved manual demand allocation.

Unknown values stay `null`/unavailable. Observed zero is distinct from missing
data.

## Policy Snapshots
`policy_snapshot` records version/hash evidence for policies and rules in force.
It is not an `artifact_accessed` event and is excluded from artifact-read and
repeated-read metrics.
