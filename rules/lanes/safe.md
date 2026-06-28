# Lane — SAFE

High risk/impact. More governance, dependency management, risk analysis, rollout/rollback, formal acceptance, traceability. **Not** a clone of any heavy methodology — just the strong-governance mode.

> Contract: `DoD per phase` · `HITL checkpoints` · `minimal artifacts` · `tracking`. Items **accumulate**: SAFE includes Standard.

## DoD per phase (+ Standard)
| Phase | Done when |
|---|---|
| Inception | stakeholders; risk analysis; mode confirmed by role |
| Design | alternatives; dependencies; rollout/rollback; architecture approved (Tech Lead) |
| Execution | dependency management; role approvals; evidence |
| Validate | full suite; formal evidence; sign-off; security |
| Operation | monitoring; active rollback plan; post-mortem (if emergency) |

## HITL checkpoints
Checkpoint at **each phase transition** + approvals by role: PM = scope, Tech Lead = architecture/technical risk, QA = acceptance, Sponsor = cost/strategy.

## Minimal artifacts
Everything in Standard + risk analysis + rollout/rollback plan + recorded approvals + **complete `audit`**.

## Tracking
`state` + `decisions` + complete `audit` (full event/evidence trail).

## Anti-SAFE brake
SAFE requires an **explicit justification** recorded in `decisions` (which override/score fired). No justification → drops to Standard. Periodic review of % SAFE per window (`../../metrics/baselines.md`).

## Model policy
SAFE floor = `strong` tier (`core/model-policy.md`); a user override below the floor is warned (trade-off) but not blocked.
