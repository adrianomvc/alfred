# Lifecycle

Alfred uses 5 phases for every demand. Risk Mode changes depth; it does not remove phases. Emergency Operational work may run Execution-first, but the deferred phases are completed in post-mortem before closure.

## Phases
| # | Phase | Owner | Purpose | File |
|---|---|---|---|---|
| 1 | Inception | Discovery | understand what is being asked | `inception/inception.md` |
| 2 | Design | Spec/Design | define how to solve with enough clarity | `design/design.md` |
| 3 | Execution | Code + Reviewer | implement in small traceable steps | `execution/execution.md` |
| 4 | Validate | Reviewer | prove it meets spec and does not regress | `validation/validation.md` |
| 5 | Operation | Metrics | release, summarize, measure, and close | `operations/operations.md` |

## Invariants
- The active lane (`rules/lanes/*`) supplies DoD, artifacts, and checkpoints.
- The active demand type (`rules/demand-types/*`) shapes emphasis and special paths.
- The Orchestrator updates `state` and `audit` at every handoff.
- No phase advances when the supreme law is violated: if unsure, stop and ask.

## Standard handoff
Each phase ends with: current state, evidence/links, open risks, next step, checkpoint owner, and model used.

