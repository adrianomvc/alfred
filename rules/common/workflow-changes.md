---
name: common-workflow-changes
description: Common Rule - Mid-Workflow Changes
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common Rule - Mid-Workflow Changes

The squad may change the process during a demand — add a sub-activity that was
skipped, skip a planned one, or redo the current step. Handle it safely: confirm,
warn about impact, and record. The human owns the change; Alfred never alters the
workflow silently.

## Add a skipped sub-activity/stage
1. **Confirm** what will be added and what it produces.
2. **Check prerequisites** (the ladder order — see `lifecycle/design/sub-activities/`).
3. Update the **execution plan** (`03-execution/012-execution-plan.md`) with the new step + rationale.
4. Update `001-state.md` (new checklist item) and log it in `05-operation/007-audit.md`.
5. Note that later steps or artifacts may need revision; the timeline extends.

## Skip a planned sub-activity/stage
1. **Confirm** the skip and **warn about the impact** (what will be missing).
2. Get **explicit human confirmation** of the trade-off.
3. Mark it `skipped` with the reason in the execution plan; record in `audit` (and `decisions` if it changes risk).
4. Later steps may need manual setup; the human accepts responsibility. It can be added back later.

## Redo the current step
1. Understand the concern; offer **modify existing** (faster) vs **restart clean** (more time).
2. On restart: archive the prior artifact (keep history — never overwrite blindly), reset its checklist items in the plan, mark it in progress, re-run.
3. Record the redo and its reason in `audit`.

## Guardrails
- Scope growth or a risk change is also an **escalation trigger** (see `escalation-triggers.md`) — reclassify the lane if needed.
- Every change is **confirmed + recorded**; nothing about the process changes without a human and an audit trail (D7/D41).
