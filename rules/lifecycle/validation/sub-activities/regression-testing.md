---
name: sub-activity-regression-testing
description: Validate sub-activity — Regression Testing
load: sub-activity
triggers:
  phase: validation
  lane: all
  demand-type: all
  agent: all
---

# Validate sub-activity — Regression Testing

> Trigger: **existing behavior is touched** (brownfield change). Optional, inside
> Validate.

## Purpose
Prove the change did not break behavior that already worked in the affected area.

## Inputs
The change/diff, the existing test suite, `tech-inception` (blast radius), the
affected systems list.

## Steps
1. Scope the **affected area** from the diff and `tech-inception`.
2. Run the **existing suite** for that area; record command and result.
3. Add regression tests for any **previously untested** behavior the change risks.
4. Compare against the prior baseline; investigate every new failure.
5. Record gaps where regression coverage is missing as a **residual risk**.

## Output
Regression run result, any new regression tests, and residual risks in the
validation evidence.

## Depth by mode
FAST = run the affected-area suite · Standard = + targeted new regression tests ·
SAFE = + full suite for the blast radius and documented baseline comparison.
