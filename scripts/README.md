# Scripts

Scripts are optional helpers. The framework must keep working without them.

## Allowed helpers
- validate required sections in markdown artifacts
- summarize metrics rollups
- check links between HUB state and app artifacts
- parse example observability JSONL and verify required framework paths
- render an ASCII toolbar from a demand `001-state.md`
- collect local observability JSONL into a telemetry-style batch
- generate a Markdown metrics rollup from local observability JSONL
- normalize host usage/cost exports into append-only observability events
- validate toolbar fixtures against the renderer output
- validate registered skills and required skill sections
- validate a real HUB/App demand before advancing or closing it
- boot a session by detecting Framework/HUB/App and listing resumable demands
- validate reverse-engineering staleness against an app commit
- validate the SDD clarity gate before Execution

## Rule
Any script output must degrade to a manual markdown checklist when the host cannot run scripts.

## Available
- `validate-framework.ps1` - optional local validation helper matching `docs/framework-validation.md`.
- `render-toolbar.ps1` - optional toolbar renderer derived from `001-state.md`.
- `collect-observability.ps1` - optional local collector for JSONL events; it does not send data anywhere.
- `generate-metrics-rollup.ps1` - optional local Markdown rollup generator.
- `normalize-usage-cost.ps1` - optional adapter for host-exported token/cost usage records.
- `validate-toolbar-fixtures.ps1` - optional drift check for toolbar examples.
- `validate-skills-registry.ps1` - optional consistency check for `skills/skills.md`.
- `validate-demand.ps1` - optional demand-level check for HUB/App artifacts, state, JSONL, skills, and adapter readiness.
- `alfred-boot.ps1` - optional boot/resume helper for detecting context and open demands.
- `validate-reverse-eng-staleness.ps1` - optional reverse-eng freshness check by recorded app commit.
- `validate-sdd-gate.ps1` - optional SDD clarity gate before Execution.

Example:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-framework.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/render-toolbar.ps1 -StatePath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units/001-state.md -Model GPT-5 -Cost "n/a"
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/collect-observability.ps1 -Root examples
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/generate-metrics-rollup.ps1 -Root examples
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/normalize-usage-cost.ps1 -InputPath examples/connectors/usage-export.jsonl
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-toolbar-fixtures.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-skills-registry.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-demand.ps1 -HubDemandPath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/alfred-boot.ps1 -Root .
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-reverse-eng-staleness.ps1 -ReverseEngPath examples/staleness-fixtures/reverse-eng-fresh.md -CurrentCommit aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/validate-sdd-gate.ps1 -HubDemandPath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units
```
