---
name: lane-standard
description: Lane — Standard
load: lane
triggers:
  phase: all
  lane: standard
  demand-type: all
  agent: all
---

# Lane — Standard

Medium risk/complexity. Basic discovery, clear spec, acceptance criteria, technical review, one human checkpoint, validation before release.

> Contract: `DoD per phase` · `HITL checkpoints` · `minimal artifacts` · `tracking`. Items **accumulate**: Standard includes FAST.

## DoD per phase (+ FAST)
| Phase | Done when |
|---|---|
| Inception | requirements answered (gate); scope/out-of-scope; initial risks |
| Design | spec + acceptance criteria + decisions; execution plan; mode revalidated |
| Execution | technical review ok; units [x]; no unapproved new scope; tests during |
| Validate | acceptance criteria ✓; regression; **PR ready to merge** |
| Operation | release notes; basic metrics; `summary` + `index` |

## HITL checkpoints
- 1 checkpoint at the Design→Execution transition (approve the spec).
- 1 final acceptance in Validate. **The PR merge into develop IS the acceptance** (protected branch forces human approval).

## Minimal artifacts
`state` + `spec` (problem, solution, acceptance criteria) + `decisions` + `audit` + PR.

## Tracking
`state` + `decisions` + `audit`.

## Toolbar (full ASCII block)
Rendered by the Orchestrator at the top of each interaction (see `core/...` toolbar spec): mode, % progress, the 5-phase track, current step, checkpoint, next step, accumulated cost.

## Standardized HITL
Every relevant transition presents 2 options: **🔧 Request Changes** / **✅ Approve & Continue** — no emergent menus. Preceded by a factual summary of what was done.
