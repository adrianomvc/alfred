# Examples

Examples should stay small and illustrative. They are not part of the framework runtime.

## Planned examples
- SQ9 FAST change with lean state/audit.
- SQ9 Standard feature with spec and acceptance criteria.
- SQ9 Operational incident with Execution-first and post-mortem.
- Multi-app demand with one HUB state in `alfred-docs-hub` linking app folders in `.alfred-docs-app`.
- Fresh sigla onboarding from empty HUB/App roots.
- Parallel units inside one governed demand.

## Available examples
- `sq9-pilot/`: pilot with FAST, SAFE, Execution-first, and parallel units.
- `fresh-sigla-onboarding/`: minimal new-sigla adoption example.
- `connectors/`: handoff examples for Git/PR, notification, and telemetry.
- `toolbar-fixtures/`: rendered toolbar examples for FAST, SAFE, Execution-first, and Standard units.
- `generated-metrics-rollup.md`: example Markdown rollup generated from observability JSONL.
- `generated-insights.md`: example improvement proposals derived from the metrics rollup.

## Layout
Examples follow the same demand layout as real work:
- root: `001-state.md` or `001-index.md`
- `01-inception/`
- `02-design/`
- `03-execution/`
- `04-validate/`
- `05-operation/`
