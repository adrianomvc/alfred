# Hybrid Squad

Alfred supports humans and AI agents with explicit responsibility boundaries. AI accelerates work; humans own decisions.

## Human roles
| Role | Owns |
|---|---|
| PM / Product | scope, value, acceptance criteria |
| Tech Lead | architecture, technical risk, irreversible trade-offs |
| QA | validation evidence and acceptance support |
| Sponsor / Leadership | cost, strategic risk, SAFE escalations |
| Developer | implementation judgment and code ownership |

## Agent roles
| Agent | Owns |
|---|---|
| Orchestrator | routing, state, toolbar, model selection |
| Discovery | Inception and requirements clarity |
| Spec/Design | spec, decisions, execution/test plan |
| Reviewer | code review and validation evidence |
| Metrics | metrics, summary, closeout |

## HITL rule
The AI may propose and execute within the active lane. Material decisions, approvals, and protected-branch merges remain human actions and are recorded in `audit`/`decisions`.

