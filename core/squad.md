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
| SRE / On-call | incident authorization (Execution-first), stabilization, production rollback |
| Security | security-sensitive changes and the security sign-off in SAFE |
| FinOps | cost ceilings and cost-driven escalations when the org assigns one |

The last three act as checkpoint owners mainly in **SAFE** (or in emergencies, for SRE); when the squad does not have the role, its responsibility falls back to Tech Lead/Sponsor and that fallback is recorded in the demand `audit`.

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

