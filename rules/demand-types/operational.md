---
name: demand-type-operational
description: Demand-type — Operacional (Operational)
load: demand-type
triggers:
  phase: all
  lane: all
  demand-type: operational
  agent: all
---

# Demand-type — Operacional (Operational)

> Contract: `types covered` · `phase emphasis` · `typical sub-activities` · `mode tendency` · `special path`. References connectors/skills by **role**, not name.

## Types covered
Bug · incident · hotfix · alert · production failure · pipeline error · degradation · emergency rollback · support.

## Paths (compact)
The branch between the normal cycle and the emergency Execution-first (degrades to plain ASCII):

```text
  Operational demand
        │ urgent?
   no ──┴── yes (incident · hotfix · rollback · production failure)
   │                                   │
   ▼ normal (linear)                   ▼ Execution-first (stabilize first, record later)
   Inception ─► Design ─►        Declare ─► Investigate ─► Authorize (HITL min) ─► Stabilize
   Execution ─► Validate ─►        ─► Validate-stab ─► Post-mortem (Inception/Design retroactive)
   Operation                        ─► Operation     · rule: no post-mortem ─► does NOT close
```

## Normal (bug, support, alert, light degradation)
- Lean cycle, FAST/Standard: reproduce → fix → regression test → PR/merge.
- Inception/Design compressed (1 line each); Validate focuses on regression.

## Emergency (incident, hotfix, rollback, production failure) — Execution-first
High risk + very short time. The linear cycle does not serve. **Stabilize first** (minimal human authorization), then complete Inception/Design/Validate *afterward* (post-mortem). Risk Mode still measures risk; only the **time mode** is compressed.

Input: **incident number + description**. Step by step:
1. **Declare incident** — minimal `state` record: what, severity, on-call owner. (Toolbar: Execution ▶, Inception/Design `⏳ post`.)
2. **Exploratory investigation** — search observability (if AWS, **CloudWatch** via the observability connector/skill) → locate the error/stack trace → **map to affected repos** → open only the suspect code needed to act safely → produce `004-investigation.md` (probable cause). No access → the human provides logs.
   - Incident investigation is intentionally **minimal and operational** before stabilization: affected app/service, signal, probable entry point, suspect change, immediate blast radius, safest rollback/hotfix path.
   - Do **not** block a critical stabilization waiting for a complete brownfield `002-reverse-eng.md`.
   - If `002-reverse-eng.md` is missing, stale, or too shallow, record that gap and complete/update it after stabilization as part of post-incident learning.
3. **Minimal authorization** from the on-call human — HITL **compressed, not skipped**.
4. **Stabilize** — hotfix/rollback directly; `audit` records each action (nothing destructive without ok).
5. **Validate stabilization** — smoke test / monitor; confirm the bleeding stopped.
6. **Post-incident (mandatory to close):** retroactive Inception/Design = **post-mortem** — root cause (already in `investigation`), `decisions`, retroactive spec, lessons, and any needed update to `002-reverse-eng.md`.
7. **Operation** — record incident, metrics, **preventive debt/action** (becomes a new demand if needed).

Rule: **no post-mortem, the demand does not close.**

## Mode tendency
Normal → FAST/Standard. Emergency → governance by risk (often SAFE-level record), time mode compressed.

## Special path
Execution-first (above). The investigation skill (observability access) is **pluggable**, not core — without it, the human supplies logs and Alfred continues the analysis.
