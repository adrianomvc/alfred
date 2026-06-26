# Demand-type: Operacional — operational prompt

Types: bug · incidente · hotfix · alerta · falha em produção · erro de pipeline · degradação · rollback emergencial · suporte.

## Normal (bug, support, light alert)
Lean cycle (FAST/Standard): reproduce → fix → regression test → PR/merge. Inception/Design compressed to one line each.

## Emergency (incident, hotfix, rollback, prod failure) — Execution-first
Input: incident number + description. Run this runbook:
1. Declare — minimal `state`: what · severity · on-call owner. Toolbar: Execution running, Inception/Design pending (post).
2. Exploratory investigation — query observability via the connector (e.g., CloudWatch); locate error/stack; map to repos; open suspect code; write `investigation.md` (probable cause). NO connector/access → ASK the human for logs; do not guess.
3. Minimal authorization — get on-call ok (HITL compressed, not skipped). Nothing destructive (reprocess, prod rollback) without explicit ok.
4. Stabilize — apply hotfix/rollback; `audit` every action.
5. Validate stabilization — smoke/monitor; confirm the bleeding stopped.
6. Post-mortem (MANDATORY to close) — retroactive Inception/Design: root cause, retro spec, lessons.
7. Operation — record incident, MTTR, preventive debt (spawn new demands); email (incident point).

## Hard rule
No post-mortem → the demand does NOT close. Mode is usually SAFE (production risk) → strong model.

## Output example (pt-BR)
"Incidente INC-9921 declarado. Investigando via CloudWatch... erro de idempotencia no publish (SplitEventPublisher). Posso aplicar o hotfix? (preciso do seu ok)"
