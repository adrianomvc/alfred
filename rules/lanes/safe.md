# Lane: SAFE — operational prompt

When Risk Mode = SAFE, APPLY this. High risk/impact → strong governance (only stronger control; not a clone).

## Checkpoints (HITL by role)
A checkpoint at EVERY phase transition, with role-based approval:
- PM = scope · Tech Lead = architecture/technical risk · QA = acceptance · Sponsor/Leadership = cost/strategy.
Acceptance = human merge. Compliance is NOT an Alfred role — regulated demands only add audit/evidence.

## Per-phase behavior (full depth)
- Inception: + stakeholders, impact analysis, risk analysis; mode confirmed by role.
- Design: + alternatives, dependencies, rollout/rollback; architecture approved (Tech Lead).
- Execution: + dependency management, role approvals, evidence; phased PRs for migrations.
- Validation: full suite (integration/contract/e2e/perf/security as applicable) + formal evidence + sign-off.
- Operation: + monitoring, active rollback, post-mortem (if emergency).

## Artifacts (minimum)
All of Standard + risk analysis + rollout/rollback + approvals log + full audit.

## Model policy
SAFE floor = strong tier. Do not drop below; warn if a fixed model below floor is requested.

## Anti-degeneration
SAFE requires explicit justification in decisions; if the squad classifies >~25% as SAFE, review the criteria.
