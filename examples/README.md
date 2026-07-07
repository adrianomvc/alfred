# Examples

Examples should stay small and illustrative. They are not part of the framework runtime — but they double as the **regression suite**: validators run against them, so a passing example is proof the framework still behaves.

## Available examples
- `sq9-pilot/`: six end-to-end demands — implantation (Standard), FAST, SAFE, Operational Execution-first with post-mortem, parallel units, and the 2.0.0 adoption rehearsal (`006-simulado-adocao-v2`, passes `validate-demand --strict` 0/0).
- `fresh-sigla-onboarding/`: minimal new-sigla adoption from empty HUB/App roots.
- `connectors/`: handoff examples (Git/PR, notification, telemetry) + sandbox simulator adapters for offline rehearsal.
- `toolbar-fixtures/`: rendered toolbar outputs for FAST, SAFE, Execution-first, and Standard units (drift-checked against the renderer).
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
