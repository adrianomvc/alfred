---
name: common-units
description: Common Rule - Demand Units
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common Rule - Demand Units

Demand is the governance unit. Units are execution slices inside one demand.

## When To Create Units
Create units during Design when the demand has any of these traits:
- touches multiple repos or components;
- has independent implementation slices;
- has separate risk/validation profiles;
- can be parallelized without conflicting writes;
- would make the execution plan too large if kept as one item.

Do not create a new demand only to represent a technical slice. Create a new demand only when scope, ownership, release, or acceptance is independently governable.

## Unit Format
Each unit is recorded in the demand `state` and, when needed, in `03-execution/<sequence>-execution-plan.md`.

Use this shape:

```markdown
- [ ] unit-001 - <short name>
  - repo:
  - owner agent:
  - phase:
  - risk override: none | Standard | SAFE
  - inputs:
  - outputs:
  - dependencies:
  - verification command:
  - expected signal:
  - evidence:
  - reviewer: none | explore | fresh-strong
  - worktree:
  - status:
```

## Rules
- Units share the same demand id and state.
- Units do not have their own `001-state.md`.
- Units may raise risk, never lower it below the demand lane.
- Parallel writers require disjoint write scopes and separate worktrees. Without
  isolation, parallel units are read-only research.
- Devin `explore` is read-only; `general` inherits the parent model and is not
  assumed cheaper. Record the actual profile and model.
- The Orchestrator serializes merge back into `state`.
- Every completed unit updates observability and audit.

## Completion
A unit is done when:
- its files/artifacts are created or updated;
- its local validation is recorded;
- its residual risks are listed;
- the demand `state` marks the unit complete.

