# Scripts

Scripts are optional helpers. The framework must keep working without them.

They ship in two equivalent runtimes so the framework can be checked on any
machine:
- `scripts/powershell/*.ps1` - PowerShell helpers (Windows-first).
- `scripts/python/*.py` - Python 3 helpers for machines without PowerShell (D3 portability).

Both sets accept the same flags (`-Root`, `-StatePath`, `-HubDemandPath`, ...)
and produce equivalent output. Pick whichever runtime the host has.

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
Each helper exists as both `scripts/powershell/<name>.ps1` and `scripts/python/<name>.py`.
- `validate-framework` - optional local validation helper matching `docs/framework-validation.md`.
- `render-toolbar` - optional toolbar renderer derived from `001-state.md`; `-Profile text` (default, ASCII) · `rich` (ANSI color/icons) · `web` (self-contained SVG). See `core/presentation/README.md`.
- `collect-observability` - optional local collector for JSONL events; it does not send data anywhere.
- `generate-metrics-rollup` - optional local Markdown rollup generator.
- `normalize-usage-cost` - optional adapter for host-exported token/cost usage records.
- `validate-toolbar-fixtures` - optional drift check for toolbar examples.
- `validate-skills-registry` - optional consistency check for `skills/skills.md`.
- `validate-demand` - optional demand-level check for HUB/App artifacts, state, JSONL, skills, and adapter readiness.
- `alfred-boot` - optional boot/resume helper for detecting context and open demands.
- `validate-reverse-eng-staleness` - optional reverse-eng freshness check by recorded app commit.
- `validate-sdd-gate` - optional SDD clarity gate before Execution.
- `validate-links` - optional internal-reference check (Markdown links + inline framework paths) to catch broken cross-references after moves/renames.
- `classify-risk` - optional Risk Mode proposal from the objective checklist (`core/risk-mode.md`): computes both axes (0/1/2 criteria), fires hard overrides, applies the anti-SAFE brake reminder, and prints a pt-BR block for `004-risk.md`. The checklist stays the source of truth; the AI proposes and the human confirms.

## PowerShell

Example:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-framework.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/render-toolbar.ps1 -StatePath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units/001-state.md -Model GPT-5 -Cost "n/a"
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/collect-observability.ps1 -Root examples
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/generate-metrics-rollup.ps1 -Root examples
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/normalize-usage-cost.ps1 -InputPath examples/connectors/usage-export.jsonl
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-toolbar-fixtures.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-skills-registry.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-demand.ps1 -HubDemandPath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/alfred-boot.ps1 -Root .
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-reverse-eng-staleness.ps1 -ReverseEngPath examples/staleness-fixtures/reverse-eng-fresh.md -CurrentCommit aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-sdd-gate.ps1 -HubDemandPath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/classify-risk.ps1 -Reversibility 1 -BlastRadius 1 -SensitiveData 0 -CustomerImpact 1 -Cost 1 -Components 1 -Novelty 1 -Ambiguity 1 -Integrations 1 -Effort 1
```

## Python (no PowerShell)

Same helpers, same flags, for machines without PowerShell. Requires Python 3.

```bash
python scripts/python/validate-framework.py
```

```bash
python scripts/python/render-toolbar.py -StatePath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units/001-state.md -Model GPT-5 -Cost "n/a"
```

```bash
python scripts/python/validate-demand.py -HubDemandPath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units
```

```bash
python scripts/python/alfred-boot.py -Root .
```

Every other helper follows the same pattern: `python scripts/python/<name>.py`
with the same flags shown in the PowerShell examples above (flags also accept
the `--kebab-case` form, e.g. `--state-path`).
