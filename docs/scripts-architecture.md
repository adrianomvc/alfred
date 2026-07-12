# Scripts Architecture

Alfred Python helpers use a shared SOLID package under `scripts/shared/`.
Runtime folders such as `scripts/workflow/`, `scripts/metrics/`,
`scripts/validators/`, and `scripts/adapters/` are command
entrypoints or compatibility wrappers. Reusable domain, application,
infrastructure, and presentation code belongs under `scripts/shared/`.

The first implemented subdomain is observability. It stores canonical usage,
cost, tool, artifact, quality, and insight signals while host-specific logic
lives at the edges as adapters.

## Layers
- `scripts/shared/observability/domain/`: typed models and pure services
  (`Usage`, `Cost`, artifact classification, cache ratio, forecast, and
  rate-card pricing in `services/rate_card.py` — `price_usage`/`price_usage_usd`,
  the single source of the cost math).
- `scripts/shared/observability/application/`: ports and use cases.
  Business rules depend on abstractions, not Claude, Codex, Devin, filesystem,
  or subprocess.
- `scripts/shared/observability/infrastructure/`: JSONL/summary
  repositories, clocks, subprocess runner, the rate-card loader
  (`rate_cards/json_rate_card_repository.py`), and host/source adapters. The
  Claude adapters carry real parsing — `adapters/claude/transcript.py`
  (transcript requests), `adapters/claude/transcript_cursor.py` (the single
  byte-offset cursor), `adapters/claude/hook.py` (raw telemetry; artifact,
  redaction, and clock helpers are injected so shared never imports the command
  package) — and `adapters/ccusage/session.py` (session-row selection).
- `scripts/shared/observability/presentation/`: view models and
  renderers such as the toolbar presenter.
- The ingestion commands under `scripts/metrics/`
  (`attribute-usage-transcript`, `claude-code-usage-hook`, `import-ccusage`,
  `apply-usage-rate-card`) are thin drivers: argparse, I/O, and delegation into
  `shared.*`. Remaining commands (`generate-metrics-rollup`,
  `generate-metrics-insights`, `normalize-usage-cost`) stay compatible entry
  points and delegate into the layered package as they are touched.

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
