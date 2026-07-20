---
name: lifecycle
description: Lifecycle
load: lifecycle
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Lifecycle

Alfred uses 5 phases for every demand. Risk Mode changes depth; it does not remove phases. Emergency Operational work may run Execution-first, but the deferred phases are completed in post-mortem before closure.

## Phases
| # | Phase | Owner | Purpose | File |
|---|---|---|---|---|
| 1 | Inception | Discovery | understand what is being asked | `inception/inception.md` |
| 2 | Design | Spec/Design | define how to solve with enough clarity | `design/design.md` |
| 3 | Execution | Reviewer | implement in small traceable steps (code-generation sub-activity) | `execution/execution.md` |
| 4 | Validate | Reviewer | prove it meets spec and does not regress | `validation/validation.md` |
| 5 | Operation | Metrics | release, summarize, measure, and close | `operations/operations.md` |

## Invariants
- The active lane (`rules/lanes/*`) supplies DoD, artifacts, and checkpoints.
- The active demand type (`rules/demand-types/*`) shapes emphasis and special paths.
- The Orchestrator updates `state` and `audit` at every handoff.
- No phase advances when the supreme law is violated: if unsure, stop and ask.

## Going backwards: replan or cancel
- **Replan (`replanejada`)** — a premise fell; the work still matters, the framing does not. With human approval the demand returns to Design/Inception keeping `id` and history, completed phases re-open in the Checklist, and `decisions` records the fallen premise and who approved. Never automatic: a non-sequential jump needing `--force` with audited justification.
- **Cancel (`cancelada`)** — should not be done at all; leaves the active set with a mini-summary (`../common/session-continuity.md`). Human decision only.
- **Reverting shipped work is neither** — via the `vcs` contract on the demand branch, never by editing history.

## Standard handoff
Each phase ends with: current state, evidence/links, open risks, next step, checkpoint owner, and model used.

