---
name: sub-activity-followup-conversion
description: Operation sub-activity — Follow-up Conversion
load: sub-activity
triggers:
  phase: operations
  lane: all
  demand-type: all
  agent: all
---

# Operation sub-activity — Follow-up Conversion

> Trigger: the demand leaves **open follow-ups, debts, or deferred work**.
> Optional, inside Operation.

## Purpose
Make sure nothing valuable is lost at close — every follow-up becomes a tracked
new demand instead of an orphaned note.

## Inputs
The `summary` residual risks, deferred items, recorded technical debt, the
demand-stream/type routing (`../../../demand-types/*`).

## Steps
1. Collect **open items**: residual risks, deferred scope, debts, post-mortem
   actions.
2. For each, decide **convert vs accept**: does it warrant a new demand?
3. Create a **new demand** stub (problem + stream/type) for converted items.
4. Link the new demands from the `summary`/`index` so the trail is continuous.
5. Explicitly mark accepted (not converted) items so they are a decision, not a
   gap.

## Output
New demand stubs for follow-ups, linked from the summary/index; accepted items
recorded as explicit decisions.

## Depth by mode
FAST = note follow-ups inline · Standard = convert the material ones · SAFE = +
debt register entries and explicit owner/priority.
