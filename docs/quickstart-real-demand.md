# Quickstart - Real Demand

Use this when starting the first real demand after the SQ9 pilot.

## 1. Choose identifiers
- Sigla: `SQ9`
- Initiative id: `iniciativa-<sequencia>-<iniciativa>`
- Demand id: `<sequencia>-<nome-demanda>`

Example:
- initiative: `iniciativa-005-primeira-entrega`
- demand: `005-primeira-demanda`

## 2. Create HUB artifacts
Create:
- `alfred-docs-hub/index.md` if this is the first demand for the sigla.
- `alfred-docs-hub/<id-iniciativa>/001-initiative.md`
- `alfred-docs-hub/<id-iniciativa>/<id-demanda>/001-state.md`
- `alfred-docs-hub/<id-iniciativa>/<id-demanda>/01-inception/002-problem.md`
- `alfred-docs-hub/<id-iniciativa>/<id-demanda>/01-inception/004-risk.md`
- `alfred-docs-hub/<id-iniciativa>/<id-demanda>/05-operation/007-audit.md`
- `alfred-docs-hub/<id-iniciativa>/<id-demanda>/05-operation/008-metrics.md`
- `alfred-docs-hub/<id-iniciativa>/<id-demanda>/05-operation/011-observability-log.jsonl`

Add `01-inception/003-requirements.md`, `02-design/006-decisions.md`, `03-execution/012-execution-plan.md`, `04-validate/013-validation-evidence.md`, `05-operation/009-summary.md`, and `01-inception/005-tech-inception.md` as required by the lane.

Update `alfred-docs-hub/index.md` with the open demand row so future boot can resume from the index before reading details.

If real environment parameters are missing, create `04-validate/014-environment-parameters.md` from `templates/hub/environment-parameters.md`. Keep the demand status as `bloqueada` or `em espera` until the missing values are confirmed. Do not invent account ids, secrets, endpoints, bucket names, schemas, table volumes, schedules, alarms, or rollback parameters.

## 3. Create App artifacts
Create:
- `.alfred-docs-app/<id-iniciativa>/<id-demanda>/001-index.md`
- `.alfred-docs-app/<id-iniciativa>/<id-demanda>/01-inception/002-reverse-eng.md`
- `.alfred-docs-app/<id-iniciativa>/<id-demanda>/05-operation/005-audit.md`
- `.alfred-docs-app/<id-iniciativa>/<id-demanda>/05-operation/006-metrics.md`
- `.alfred-docs-app/<id-iniciativa>/<id-demanda>/05-operation/008-observability-log.jsonl`

Add `02-design/003-spec.md`, `01-inception/004-investigation.md`, `04-validate/007-evidence.md`, or `05-operation/009-hub-sync.md` according to the lane/type and whether the HUB is writable.

Keep `001-index.md` as the app-local context index. It should point to reverse engineering, spec, evidence, local audit/metrics, and HUB sync state.

When creating `01-inception/002-reverse-eng.md`, record the app commit used for the analysis. Before code changes, recheck staleness:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-reverse-eng-staleness.ps1 -ReverseEngPath .alfred-docs-app/<id-iniciativa>/<id-demanda>/01-inception/002-reverse-eng.md -AppRepoPath .
```

## App-only mode
If the demand starts while Alfred is running only in the app repo, create/update only `.alfred-docs-app/<id-iniciativa>/<id-demanda>/`.

In App-only mode:
- write local progress in `001-index.md`;
- write technical traceability in `05-operation/005-audit.md`;
- append local events to `05-operation/008-observability-log.jsonl`;
- write pending HUB updates in `05-operation/009-hub-sync.md`;
- do not write `alfred-docs-hub` until a HUB workspace or explicit sync path is available.

## 4. Classify Risk Mode
- FAST: low risk, reversible, small scope.
- Standard: medium risk/complexity, normal product/engineering flow.
- SAFE: high risk, hard rollback, sensitive impact, architecture/governance risk.
- Operational Execution-first: urgent incident/hotfix; stabilize first, post-mortem before close.

## 5. Declare active skills and adapters
Register active skills in `001-state.md` before Design/Execution. Examples:
- Python Glue job: `coding-standard`, `lang-python`, `platform-aws-data`.
- Oracle/S3 reconciliation SQL: `coding-standard`, `lang-sql`, `platform-aws-data`.
- Terraform AWS infrastructure: `coding-standard`, `lang-terraform`, `platform-aws-data`.
- Sensitive data or SAFE lane: add `security-review`.

If a host adapter is needed, check `docs/host-adapter-readiness.md`. If readiness is incomplete, use the connector handoff examples and record the missing input instead of pretending the adapter is active.

## 6. Run and close
During Design, create an execution plan when the demand has multiple repos, units, or validation paths. During Execution, keep unit checkboxes in the plan and mirror phase progress in `001-state.md`. During Validate, record evidence explicitly for Standard/SAFE.

Before running commands against real infrastructure or external hosts, confirm `04-validate/014-environment-parameters.md` when it exists. A command that depends on an unconfirmed account, secret, endpoint, network path, bucket, table, role, or scheduler must be blocked and recorded instead of executed with assumed values.

Before entering Execution for Standard/SAFE, run the optional SDD gate:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-sdd-gate.ps1 -HubDemandPath <alfred-docs-hub>/<id-iniciativa>/<id-demanda>
```

Keep `001-state.md` current. A demand is only closed when the checklist is complete and `05-operation/009-summary.md`/`05-operation/008-metrics.md` are updated from `05-operation/011-observability-log.jsonl`.

On closure, update:
- HUB `index.md`: move demand from open to closed and link `05-operation/009-summary.md`;
- app `001-index.md`: update evidence and HUB sync state;
- `05-operation/009-summary.md`: include the resume note and follow-ups.

Stamp the active Alfred version in `001-state.md`, `05-operation/008-metrics.md`, HUB `05-operation/007-audit.md`, and app-local `001-index.md`/`05-operation/006-metrics.md` so future analysis can segment events by framework version.

Before advancing to a major checkpoint or closing a demand, run the optional demand validator:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-demand.ps1 -HubDemandPath <alfred-docs-hub>/<id-iniciativa>/<id-demanda>
```

Use `-Strict` before closure when warnings should block the close.
