---
name: sub-activity-technical-review
description: Execution sub-activity — Technical Review
load: sub-activity
triggers:
  phase: execution
  lane: all
  demand-type: all
  agent: all
---

# Execution sub-activity — Technical Review

> Trigger: **Standard/SAFE** (FAST self-reviews). Optional, inside Execution.
> Owner: **Reviewer** agent.

## Purpose
Catch defects and standard violations before the PR is offered for Validation —
a technical gate, distinct from spec acceptance.

## Inputs
The change/diff, `spec` + acceptance criteria, active coding-standard/language
skill, the Reviewer agent contract (`../../../agents/reviewer.md`).

## Steps
1. Review the diff against the **spec** and the **coding-standard** (SOLID).
2. Check **traceability**: every plan step maps to a requirement and is `[x]`.
3. Flag defects, smells, and missing automation seams; request fixes.
4. Confirm commits are on the **demand branch** and `state`/`audit` are current.
5. Satisfy **DoD Execution** → mark the PR ready for Validation.

## Output
Review findings, requested fixes, and a PR marked ready (or sent back) with the
result recorded in `audit`.

## Depth by mode
FAST = self-review noted in the PR · Standard = Reviewer pass + findings ·
SAFE = + dependency review and explicit sign-off before Validate.
