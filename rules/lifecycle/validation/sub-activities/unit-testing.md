---
name: sub-activity-unit-testing
description: Validate sub-activity — Unit Testing
load: sub-activity
triggers:
  phase: validation
  lane: all
  demand-type: all
  agent: all
---

# Validate sub-activity — Unit Testing

> Trigger: **logic changed**. Optional, inside Validate. The cheapest, most
> local rung — usually the first to run.

## Purpose
Prove each changed unit behaves correctly in isolation, including edge cases.

## Inputs
The changed code, `spec` + acceptance criteria, active language skill (test
conventions), the execution plan's per-step test hooks.

## Steps
1. Identify the units changed and their meaningful **edge cases**.
2. Write or update **isolated tests** per unit (no external dependencies).
3. Run them; record the **command, result, and coverage gaps**.
4. For risky logic, consider property-based tests (`property-based-testing` skill).
5. Mark units lacking tests as a **residual risk** if not covered.

## Output
Unit test results (command + pass/fail), coverage gaps, and residual risks in the
validation evidence.

## Depth by mode
FAST = key paths only · Standard = changed units + edge cases · SAFE = + negative
cases, boundaries, and explicit coverage statement.
