---
name: sub-activity-baseline-drift-check
description: Operation sub-activity — Baseline Drift Check
load: sub-activity
triggers:
  phase: operations
  lane: all
  demand-type: all
  agent: all
---

# Operation sub-activity — Baseline Drift Check

> Trigger: **Standard/SAFE** close. Optional, inside Operation.

## Purpose
Compare this demand against baselines and flag process drift early — before it
becomes a pattern across demands.

## Inputs
The collected `metrics`, historical baselines / rollup
(`metrics/` insights), the lane that was actually used, post-mortem status.

## Steps
1. Compare against baselines: **elapsed time, cost, interactions, rework**.
2. Flag **too much SAFE** — demands escalated beyond their real risk.
3. Flag **excessive cost** or **repeated rework** on the same area.
4. Flag a **missing post-mortem** when Execution-first was used.
5. Record flags as **insight proposals** (human-reviewable), not auto-policy (D46).

## Output
A short list of drift flags / insight proposals attached to the summary; nothing
is auto-applied to policy.

## Depth by mode
FAST = skipped · Standard = the core flags above · SAFE = + trend note across
recent demands and an explicit follow-up if drift is confirmed.
