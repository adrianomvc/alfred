# Examples Manifest

Examples are test assets, not runtime framework state. Keep only examples that
are maintained by a validator or intentionally serve a documented fixture role.

| Path | Tier | Validator |
|---|---|---|
| `sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/006-simulado-adocao-v2/` | strict demand regression | `validate-demand --strict` |
| `sq9-pilot/.alfred-docs-app/iniciativa-001-piloto/006-simulado-adocao-v2/` | strict app-side regression | `validate-demand --strict -AppDemandPath` |
| `fresh-sigla-onboarding/` | onboarding fixture | `validate-framework` JSONL/link checks |
| `observability-fixtures/` | usage/cost/cache/artifact rollup fixture | `validate-framework` JSONL + rollup checks |
| `connectors/` | connector handoff/sandbox fixture, including canonical observability decision events | `validate-connectors` + JSONL checks |
| `toolbar-states/` | renderer input fixture | `validate-toolbar-fixtures` |
| `toolbar-fixtures/` | renderer expected output fixture | `validate-toolbar-fixtures` |
| `context-manifest-fixtures/` | JIT context manifest fixture | `validate-context-manifest-fixtures` |
| `staleness-fixtures/` | reverse-eng freshness fixture | `validate-reverse-eng-staleness` |
| `generated/` | metrics helper output fixture | `validate-framework` path/link checks |

## Rule
Partial historical demand snapshots are not a tier. If a scenario is still
valuable, migrate it to a strict regression fixture or extract the narrow
behavior into a small fixture such as `toolbar-states/`.
