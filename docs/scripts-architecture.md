# Scripts Architecture

Alfred Python helpers use a shared SOLID package under `scripts/shared/`.
Runtime folders such as `scripts/python/workflow/`, `scripts/python/metrics/`,
`scripts/python/validators/`, and `scripts/python/adapters/` are command
entrypoints or compatibility wrappers. Reusable domain, application,
infrastructure, and presentation code belongs under `scripts/shared/`.

The first implemented subdomain is observability. It stores canonical usage,
cost, tool, artifact, quality, and insight signals while host-specific logic
lives at the edges as adapters.

## Layers
- `scripts/shared/observability/domain/`: typed models and pure services
  (`Usage`, `Cost`, artifact classification, cache ratio, forecast).
- `scripts/shared/observability/application/`: ports and use cases.
  Business rules depend on abstractions, not Claude, Codex, Devin, filesystem,
  or subprocess.
- `scripts/shared/observability/infrastructure/`: JSONL/summary
  repositories, clocks, subprocess runner, and thin host/source adapters.
- `scripts/shared/observability/presentation/`: view models and
  renderers such as the toolbar presenter.
- Legacy scripts under `scripts/python/metrics/` and `scripts/python/workflow/`
  remain compatible entry points and should delegate into the layered package
  as they are touched.

## Whole-Scripts Rule
New reusable logic must not be added to command scripts directly. Add it under
`scripts/shared/<subdomain>/` with the same layer boundaries:
`domain -> application ports/use cases -> infrastructure -> presentation`.

The shared package must not import `_common.py`, `workflow/`, `metrics/`,
`validators/`, or `adapters/`. Those folders may depend on `shared.*`; the
reverse dependency is forbidden.

## Adapter Rule
Adding a host/source means:
1. implement a small adapter for that source;
2. declare capabilities and gaps;
3. register it in the observability composition registry;
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
