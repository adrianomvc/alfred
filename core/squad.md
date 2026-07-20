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

## When two humans disagree
Each row names **one owner per axis**, who decides within it even against someone more senior. It is only a tie when it crosses axes (PM wants scope the Tech Lead calls unsafe). Alfred never picks a side nor averages both into a compromise nobody approved: **pause** the disputed step, record **both** positions in `02-design/006-decisions.md` (owner + rationale, neither marked chosen), escalate to the **Sponsor** to decide or delegate, and log it in `05-operation/007-audit.md`. Safety is not a tie — the more restrictive position on risk, security, or data exposure holds until the Sponsor rules otherwise (`rules/common/escalation-triggers.md`).

## HITL rule
The AI may propose and execute within the active lane. Material decisions, approvals, and protected-branch merges remain human actions and are recorded in `audit`/`decisions`.

