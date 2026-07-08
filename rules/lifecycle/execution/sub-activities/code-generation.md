---
name: sub-activity-code-generation
description: Execution sub-activity — Code Generation
load: sub-activity
triggers:
  phase: execution
  lane: all
  demand-type: all
  agent: all
---

# Execution sub-activity — Code Generation

> Trigger: **always** (the act of building). Optional only in depth. Inherited
> from AI-DLC (Generation).

## Purpose
Produce the change aligned to the `spec`, in small steps, mirroring the active
template and coding-standard — brownfield in place.

## Inputs
`spec` + execution plan step, applicable **template** repo (load only relevant
sections, JIT), active **coding-standard / language skill** (override: most
specific wins, else `../../../../skills/coding-standard.md`).

## Steps
1. Load the template section and coding-standard for this step (JIT).
2. Implement the change **in place** — modify existing files; never create
   `arquivo_v2`.
3. Apply **SOLID** and mirror the template's structure and conventions.
4. Make the code **automation-friendly** (`data-testid`, stable selectors, clear
   seams for tests).
5. Keep each step **small and traceable**; commit per step on the demand branch.
6. Record any **deviation** from the spec/standard with its reason.

## Output
The implemented change for the step, committed on the demand branch, with
deviations recorded.

## Depth by mode
FAST = direct small change + self-review · Standard = step-by-step generation
mirroring template/standard · SAFE = + evidence and stricter standard adherence.
