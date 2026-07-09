---
name: phase-design
description: Lifecycle — Design ("How?" — strong SDD)
load: phase
triggers:
  phase: design
  lane: all
  demand-type: all
  agent: all
---

# Lifecycle — Design ("How?" — strong SDD)

Define how to solve before executing. Owner agent: **Spec/Design**. SDD is the clarity brake: **no relevant Execution starts without the Design DoD of the mode satisfied.**

## Steps
1. Load `requirements` + `tech-inception` (JIT).
2. **Solution shaping** + alternatives (SAFE) → `spec` (SDD) + acceptance criteria.
3. Sub-activities **by trigger**: application-design (new component) / units-generation (decompose) / functional-design (new logic) / NFR (perf/security/scale) / infrastructure (deploy) / user-stories (Produto). These are sub-activities **inside Design**, not new phases. Each rung has concise JIT guidance in `sub-activities/` — load only what the demand triggers.
4. **Execution plan** — impact analysis, skip/execute with justification, sequence, parallelization + test plan.
5. Confirm applicable **template** (optional — may be none) and **SOLID/language** standard to mirror in Execution. If no template was registered for the sigla, mirror the conventions from the app's reverse engineering and record that none applied.
6. Record `decisions`; **revalidate Risk Mode**; satisfy **DoD Design** → checkpoint (spec approval).

## Context compression
RAG/compressed context may help find relevant requirements, code areas, logs, and
design inputs. It must not replace a detailed `spec`, decisions, execution plan,
or original source pointers. Apply `../../common/context-compression-policy.md`
when compression is used.

## Inherited from AI-DLC
- **Conditional stages → sub-activities** (application-design, units-generation, functional-design, NFR, infrastructure) — by trigger and mode, never new phases.
- **Workflow-planning → execution plan** — impact, skip/execute justified, sequence, parallelization, risk.

## Demand × Units (decomposition)
The demand is the **governance unit** (1 `state`, 1 base Risk Mode, checkpoints, acceptance/merge). In Design it may decompose into **N units**: smaller, more isolated parts, each less complex (lower depth) and, if independent, parallelizable. **Units do not create their own state** — they are checklist items in the execution plan inside the demand `state`.

Use `../../common/units.md` for decomposition rules and `../../../templates/hub/execution-plan.md` for the execution plan shape.

## Outputs
chosen solution · spec · acceptance criteria · decisions · dependencies · execution/test plan · Risk Mode revalidation.

## Human roles
Tech Lead (architecture/decisions), PM (scope acceptance).

## Checkpoint
Spec approval (Standard/SAFE); architecture + alternatives approval (SAFE).

## Depth by mode
FAST = inline spec in the PR (no separate Design phase — folds into Execution) · Standard = spec + criteria + decisions · SAFE = + alternatives + dependencies + rollout/rollback.
