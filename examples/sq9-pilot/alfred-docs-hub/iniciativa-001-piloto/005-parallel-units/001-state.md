# 001-state - 005-parallel-units

## Demanda
- id: `005-parallel-units`
- titulo: Exemplo de demanda com units paralelas
- sigla: SQ9
- initiative id: `iniciativa-001-piloto`
- stream/type: Engineering / multi-repo
- lane: Standard
- framework version: 0.1.0-dev
- observability schema: alfred.observability.v1
- status: em andamento

## Progresso
- current phase: Execution
- current step: executar units independentes
- next step: serializar resultado no state e validar evidencias
- checkpoint: Tech Lead

## Active Skills
- base: `coding-standard`
- language/platform: `platform-aws-data`
- security: n/a
- loaded sections: rules, validation, review checklist

## Host Adapters
- vcs: handoff/manual
- tracker: handoff/manual
- notification: handoff/manual
- telemetry: local JSONL
- usage-cost: host export not available
- readiness: partial; no real host credentials configured

## Units
- [x] unit-001 - atualizar contrato App A
  - repo: `sq9-app-a`
  - write scope: `.alfred-docs-app/.../unit-001`
  - validation: lint textual
  - status: completed
- [x] unit-002 - atualizar contrato App B
  - repo: `sq9-app-b`
  - write scope: `.alfred-docs-app/.../unit-002`
  - validation: lint textual
  - status: completed
- [ ] unit-003 - consolidar no HUB
  - repo: HUB
  - write scope: `001-state.md`, `04-validate/013-validation-evidence.md`
  - validation: evidencias completas
  - status: pending

## Links
- problem: `01-inception/002-problem.md`
- requirements: `01-inception/003-requirements.md`
- risk: `01-inception/004-risk.md`
- tech inception: `01-inception/005-tech-inception.md`
- decisions: `02-design/006-decisions.md`
- execution plan: `03-execution/012-execution-plan.md`
- validation evidence: `04-validate/013-validation-evidence.md`
- audit: `05-operation/007-audit.md`
- metrics: `05-operation/008-metrics.md`
- observability log: `05-operation/011-observability-log.jsonl`

## Checklist
- [x] Inception
- [x] Design
- [x] Execution
- [ ] Validate
- [ ] Operation
