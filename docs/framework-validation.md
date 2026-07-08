# Framework Validation

Use this checklist after changing Alfred itself.

## Static Checks
- `rg --files` lists expected framework areas.
- No generated HUB/App demand data is added under `core/`, `rules/`, `skills/`, `connectors/`, `metrics/`, or `templates/`.
- Framework files remain in English.
- Generated example artifacts may be in pt-BR.
- Templates keep framework labels in English and generated-content instruction in pt-BR.

## Required Structure
- `core/`
- `rules/common/`
- `rules/demand-types/`
- `rules/lanes/`
- `rules/lifecycle/`
- `rules/agents/`
- `skills/`
- `connectors/`
- `metrics/`
- `templates/hub/`
- `templates/app/`
- `docs/`
- `examples/`

## One-shot Validation
Run all structure, JSONL, and behavioral sub-checks at once. Use either runtime:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validators/validate-framework.ps1
```
```bash
python scripts/python/validators/validate-framework.py
```

## Example Validation Tiers
- `validate-framework` is the required framework gate. It validates examples as framework fixtures, including JSONL, links, generated outputs, the canonical demand example, and declared strict regression fixtures wired into the validator.
- `validate-demand --strict` is required only for examples explicitly declared as strict regression fixtures in `examples/README.md`.
- Historical or illustrative examples may be partial/in progress. They should pass the framework gate and remain useful as snapshots, but they are not a strict demand-closure guarantee until migrated and declared as strict regression fixtures.

## JSONL Checks
Run a JSON parse over all observability logs in examples and active pilots.

PowerShell:
```powershell
Get-ChildItem -Path examples -Recurse -Filter *observability-log.jsonl -Force |
  ForEach-Object {
    $file = $_.FullName
    Get-Content -LiteralPath $file | ForEach-Object { $_ | ConvertFrom-Json | Out-Null }
    Write-Output "OK $file"
  }
```

## Link/Path Checks
- Demand root keeps only `001-state.md` in HUB examples.
- App demand root keeps only `001-index.md` in app examples.
- HUB artifacts use phase folders:
  - `01-inception/`
  - `02-design/`
  - `03-execution/`
  - `04-validate/`
  - `05-operation/`
- App artifacts use the same phase folders.

## Behavioral Checks
- Risk Mode still has FAST, Standard, SAFE.
- Execution-first still requires post-mortem before close.
- `rules/common/overconfidence.md` still requires grounding before action.
- `rules/common/escalation-triggers.md` stops hard-trigger cases.
- `rules/common/units.md` keeps units inside one demand state.
- `rules/common/question-format.md` keeps pt-BR `[Resposta]:` with 2-5 options.
- `docs/version-adoption.md` keeps active-demand framework upgrades explicit and human-approved.
- `docs/release-governance.md` and `CHANGELOG.md` record release intent and compatibility notes.
- `docs/adapter-implementation.md` keeps concrete host adapters explicit, auditable, and degradable.
- `scripts/powershell/validators/validate-connectors.ps1` checks connector contracts and adapter-shaped examples.
- `scripts/powershell/validators/validate-model-policy.ps1` checks lane floors, tier map, adjustments, override warning, and toolbar transparency.
- `scripts/powershell/validators/validate-links.ps1` checks that internal Markdown references (links and inline framework paths) still resolve after moves/renames.
- The architecture SOLID **extension checklist** in `core/architecture.md` passes for any added/moved module, file, or artifact (one reason to change; extend by adding; substitutable via contract; loads only what it needs; depends on a role, not a concrete).

## Acceptance
A framework change is acceptable when:
- the changed rule/template has a clear owner module;
- the architecture SOLID extension checklist (`core/architecture.md`) passes for added/moved files;
- examples or docs reflect the new convention;
- JSONL examples still parse;
- connector contracts and adapter examples pass validation;
- model policy validation passes;
- no instruction conflicts with markdown-first agnostic operation;
- remaining gaps are recorded in `docs/implementation-status.md`.
- release-relevant changes are recorded in `CHANGELOG.md`.
