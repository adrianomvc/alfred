# Examples

Examples should stay small and illustrative. They are not part of the framework runtime — but they double as the **regression suite**: validators run against them, so a passing example is proof the framework still behaves.

## Validation tiers
- **Framework gate:** `validate-framework` must pass. It validates structure, JSONL, links, generated registries/shims/fixtures, connector contracts, model policy, and declared strict regression fixtures.
- **Strict regression examples:** examples explicitly called out as strict regression fixtures must pass `validate-demand --strict` with 0 errors / 0 warnings. Today this is `sq9-pilot/.../006-simulado-adocao-v2`.
- **Toolbar fixtures:** lane-rendering states live under `toolbar-states/`; they are not demands and must stay small.
- **Historical/illustrative examples:** do not keep stale demand snapshots in-tree. Migrate them to a strict fixture or remove them.

## Available examples
- `examples.md`: manifest of maintained examples and validation tier.
- `sq9-pilot/`: one maintained end-to-end strict regression demand — `006-simulado-adocao-v2` (passes `validate-demand --strict` 0/0).
- `fresh-sigla-onboarding/`: minimal new-sigla adoption from empty HUB/App roots.
- `connectors/`: handoff examples (Git/PR, notification, telemetry) + sandbox simulator adapters for offline rehearsal.
- `toolbar-states/` + `toolbar-fixtures/`: rendered toolbar outputs for FAST, SAFE, Execution-first, and Standard states (drift-checked against the renderer).
- `staleness-fixtures/`: reverse-engineering freshness fixture for the staleness validator.
- `generated/`: outputs the metrics helpers produce — `metrics-rollup.md` (from observability JSONL) and `insights.md` (human-reviewable proposals).

## Layout
Examples follow the same demand layout as real work:
- root: `001-state.md` or `001-index.md`
- `01-inception/`
- `02-design/`
- `03-execution/`
- `04-validate/`
- `05-operation/`
