---
name: sub-activity-unit-loop
description: Execution sub-activity — Unit Loop
load: sub-activity
triggers:
  phase: execution
  lane: all
  demand-type: all
  agent: all
---

# Execution sub-activity — Unit Loop

> Trigger: the demand was **decomposed into more than one unit** in Design (D24).
> Optional, inside Execution.

## Purpose
Execute each unit in an isolated, repeatable loop so progress is traceable and a
failing unit never blocks an independent one.

## Inputs
The execution plan units (`workflow-planning`), `state` two-level checkbox, the
escalation triggers (`../../../common/escalation-triggers.md`).

## Steps
1. Pick the next unit from the plan (respect sequence; parallel only if independent).
2. **Generate and verify** using the guided-then-strict attempts in
   `../../../common/verification-loop.md`. Do not silently repeat the same mode.
3. If an attempt fails, record its mode, failed signal, evidence, feedback, and
   scope delta. After the strict-minimal attempt fails, stop the unit and replan.
4. **Commit** on the demand branch; mark the plan checkbox `[x]` and update the
   phase checkbox in `state` (two-level → toolbar).
5. **Review** the unit (hand to `technical-review` for Standard/SAFE).
6. Watch the **escalation triggers**; on a hard trigger, stop the unit, persist
   state/audit/observability, and ask the responsible human.
7. Repeat until all units are done; units never create their own `state`.

## Output
Per-unit commits with updated two-level checkboxes, attempt evidence, recorded
deviations, and a clean hand-off to Validate.

## Depth by mode
FAST = usually a single unit, no loop · Standard = loop with per-unit commit +
review · SAFE = + per-unit evidence and dependency approvals.
