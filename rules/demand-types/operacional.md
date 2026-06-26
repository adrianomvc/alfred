# Demand type: Operacional (D5/D6/D34)

Types: bug · incident · hotfix · alert · prod failure · pipeline error · degradation · emergency rollback · support.

## Normal (bug, support, light alert)
Lean cycle (FAST/Standard): reproduce → fix → regression test → PR/merge. Inception/Design compressed.

## Emergency (incident, hotfix, rollback, prod failure) — Execution-first (D6)
Input: **incident number + description**. Steps:
1. **Declare incident** — minimal `state`: what, severity, on-call owner. (Toolbar: Execution ▶, Inception/Design ⏳ post.)
2. **Exploratory investigation (D34)** — observability (if AWS, **CloudWatch via connector**) → locate error/stack → **map to repos** → open code → `investigation.md` (probable cause). No connector → human provides logs.
3. **Minimal authorization** by on-call — HITL compressed, not skipped (D7).
4. **Stabilize** — hotfix/rollback; `audit` records each action (D27: nothing destructive without ok).
5. **Validate stabilization** — smoke/monitor.
6. **Post-mortem (mandatory to close)** — retroactive Inception/Design: root cause, `decisions`, retro spec, lessons.
7. **Operation** — record incident, metrics, preventive debt (may spawn new demands).
Rule: no post-mortem → demand does not close (D6).
