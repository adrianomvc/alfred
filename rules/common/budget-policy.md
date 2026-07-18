---
name: common-budget-policy
description: Common rule - per-demand budget monitoring and decisions
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Budget Policy

## Trigger
Load this rule when a demand has a budget set (`budget limit` in `001-state.md`)
and at every checkpoint (phase transition, unit completion). Extends
`rules/common/token-budget-policy.md`.

## Setting the budget
At the opening framing checkpoint the human may set a budget for the demand:
`budget unit` (acu default, or usd/tokens), `budget limit`, and `budget on limit`
(`pause-and-ask` default, or `warn`). On DEVIN CLI the consumption comes from the
`/usage` delta (`scripts/metrics/session-cost.py`). No budget set → this rule is
inert; work proceeds normally.

## At each checkpoint
Refresh consumption (`session-cost.py` from the pasted `/usage`), then run
`python ~/.alfred/scripts/metrics/budget-monitor.py -StatePath <hub-demand>/001-state.md`.
It cross-references two axes — **consumed (% of budget) × delivered (phases/units)**
— and returns a `status`. Also weigh the **burn-rate**: with the cost-per-phase so
far, will the budget cover what remains?

## Decision by status
- **`within` (< near threshold, default 80%):** proceed normally.
- **`near` (≥ near, < 100%), or the burn-rate projects an overrun:** **propose
  accelerating to deliver the essential within budget** — skip **optional**
  sub-activities, lean the lane (needs human approval to lower, `core/risk-mode.md`),
  defer non-critical work (`rules/common/deferred-work-policy.md`), prioritising the
  demand's **core**. Report in one line: *"consumido X% do orçamento; para caber,
  proponho acelerar pulando [opcionais]"*. The human confirms.
- **`exceeded` (≥ 100%):** **report delivered vs budgeted, then stop** — *"entregue:
  fases N/5 (core pronto); orçamento esgotado. Parar / subir o orçamento / fechar no
  mínimo entregável?"*. `budget on limit: pause-and-ask` → stop and ask before the
  next step; `warn` → warn once and continue.
- **`unmeasurable`:** do not block — ask the human to run `/usage` so consumption
  can be measured; never invent a number (D10).

## Delivery-vs-budget report
At each checkpoint and at close, state what was delivered against the budget:
`entregue: <fases/units> · consumido: <X% do orçamento>`.

## Guardrails (inviolable)
- Accelerating/degrading **never** drops acceptance criteria, constraints, rollback,
  security, or SAFE gates (`token-budget-policy.md` §Guardrails).
- **Never skip a phase** (the 5 phases are invariant) — only skip **optional**
  sub-activities or lean the lane (lowering the lane needs human approval).
- On the local DEVIN CLI the budget is **soft**: Alfred pauses itself; it cannot
  force Devin to stop. A **hard** cap exists only via `max_acu_limit` at session
  creation through the API (paid plans) — see `core/hooks/devin-hooks.md`.

## Audit
Record the budget, each status change, and any accepted acceleration/degradation
(what was skipped, human approval) in `audit`.
