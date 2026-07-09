---
name: sub-activity-workflow-planning
description: Execution sub-activity — Workflow Planning
load: sub-activity
triggers:
  phase: execution
  lane: all
  demand-type: all
  agent: all
---

# Execution sub-activity — Workflow Planning

> Trigger: **Standard/SAFE** or any non-trivial change. Optional, inside
> Execution. Inherited from AI-DLC (Planning).

## Purpose
Turn the approved `spec` into a **numbered plan with checkboxes** that is the
single source of truth for what gets built, in what order — before any code.

## Inputs
`spec` + acceptance criteria, execution-plan template
(`../../../../templates/hub/execution-plan.md`), unit decomposition
(`../../../common/units.md`), token budget policy
(`../../../common/token-budget-policy.md`), active template/coding-standard.

## Steps
1. Break the change into **numbered steps**, each a small traceable unit of work.
2. Add a **checkbox** per step (single source of truth); mark `[x]` as done.
3. Define **sequence and parallelization**: which steps are independent.
4. Map each step to a **requirement** (requirement→code traceability).
5. Note the **test plan hook** per step (ties to Validate test strategy).
6. For large/multi-repo work, add a context budget per unit: sources to open,
   sources to search only, and sources deferred.
7. Get plan **approval** (Standard/SAFE) before generation starts.

## Output
The execution plan (numbered, checkboxed, sequenced) recorded as the demand's
single source of truth; approval recorded in `audit`.

## Depth by mode
FAST = a short inline checklist or skipped for tiny changes · Standard = full
numbered plan + approval · SAFE = + dependency ordering, rollback steps, and
evidence requirements per step.
