# ABC Policy - Sensitive Data Requires SAFE

## identity
- policy id: ABC-POL-001
- title: Dados sensiveis exigem lane SAFE
- scope: sigla
- owner: Squad ABC
- status: active
- version: 1
- updated at: 2026-06-28

## applies to
- streams: produto, operacional, engineering
- lanes: FAST, Standard, SAFE
- repositories: todos os repos da sigla ABC
- environments: todos
- data classes: dados sensiveis, CPF, segredo, credencial
- phases: Inception, Design, Execution, Validate, Operation

## rule
Se uma demanda identificar dado sensivel, CPF, segredo ou credencial, Alfred deve propor ou elevar a lane para SAFE e registrar a justificativa em `01-inception/004-risk.md` e `02-design/006-decisions.md`.

## rationale
Dados sensiveis aumentam risco operacional, exigem rastreabilidade completa e podem precisar de controles adicionais de acesso, evidencia e rollback.

## enforcement
- block action: nao executar alteracao material enquanto a reclassificacao SAFE nao for decidida
- require human approval: sim
- require audit entry: sim
- require evidence: sim
- escalation owner: Tech Lead ABC

## exceptions
- allowed: yes
- required approver: Tech Lead ABC
- expiry required: yes
- record location: `02-design/006-decisions.md` e `05-operation/007-audit.md`

## audit evidence
| Event | Required fields | Artifact |
|---|---|---|
| policy applied | policy id, demand id, data class, lane before, lane after, owner | audit/JSONL |
| exception approved | owner, reason, expiry, exact deviation, demand id | decisions/audit |

## related artifacts
- state: `001-state.md`
- decisions: `02-design/006-decisions.md`
- audit: `05-operation/007-audit.md`
- metrics: `05-operation/008-metrics.md`
