# Reverse Engineering

> Generated content should be written in pt-BR.
> Brownfield rule: this is not a light summary. It must be detailed enough for
> a new engineer/AI agent to understand the existing app before changing it.
> If a section is not applicable, write `n/a` and explain why.

## App commit
- commit:
- branch:
- captured at:
- captured by:

## Purpose and business context
- what this app does:
- main users/consumers:
- business capabilities:

## Architecture overview
- architecture style:
- main layers/modules:
- ownership boundaries:
- diagrams/links:

## Code map
| Area/module | Path | Responsibility | Notes |
|---|---|---|---|
|  |  |  |  |

## Entry points and runtime
- application entry points:
- jobs/handlers/commands:
- configuration files:
- local run/build commands:
- deployment/runtime:

## Data model and state
- databases/storage:
- important entities/tables/files:
- migrations/schema ownership:
- stateful side effects:

## Interfaces and contracts
| Integration/API/job | Direction | Contract/schema | Auth | Failure behavior |
|---|---|---|---|---|
|  |  |  |  |  |

## Critical flows
| Flow | Trigger | Main path | Data touched | Failure/rollback notes |
|---|---|---|---|---|
|  |  |  |  |  |

## Dependencies and external systems
- internal dependencies:
- external dependencies:
- libraries/frameworks:
- version constraints:

## Tests and quality signals
- existing tests:
- how to run:
- current gaps:
- static analysis/lint:

## Operations and observability
- logs/metrics/traces:
- alerts/dashboards:
- operational runbooks:
- known incidents:

## Security and sensitive data
- auth/authz:
- secrets/config ownership:
- sensitive data:
- security constraints:

## Change impact map
- files/modules likely touched:
- downstream impact:
- rollback considerations:
- compatibility concerns:

## Known risks and unknowns
- risks:
- assumptions:
- open questions:
- human decisions needed:

## Staleness check
- current commit:
- status: fresh | stale | unknown
- action:

## Completeness check
- [ ] commit recorded
- [ ] architecture understood
- [ ] code map complete enough for the demand
- [ ] entry points/runtime understood
- [ ] data and integrations mapped
- [ ] critical flows mapped
- [ ] tests/quality signals identified
- [ ] operations/security constraints checked
- [ ] risks and unknowns recorded
