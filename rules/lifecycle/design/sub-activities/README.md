# Design sub-activities

Optional steps **inside Design** (never new phases). They run **by trigger** and
their depth scales with the Risk Mode. Loaded just in time — only the ones the
demand needs. Distilled from AI-DLC, kept stack-agnostic (no AWS); reference
connectors/skills by role.

## The ladder (run only the rungs the demand triggers)
| Sub-activity | Trigger | Gives |
|---|---|---|
| `user-stories` | Produto: new feature/journey/UX | user-centered stories + acceptance criteria + personas |
| `application-design` | new/changed component or service boundary | components, interfaces, service layer, dependencies |
| `functional-design` | new/changed business logic | per-unit logic, domain model, rules, validation (tech-agnostic) |
| `nfr-design` | perf / scale / availability / security matters | NFR woven into the design via patterns/components |
| `infrastructure-design` | needs deploy / infra change | logical components mapped to infrastructure choices |

## Order (when several fire)
`user-stories` → `application-design` → `functional-design` → `nfr-design` → `infrastructure-design`.
Each is optional; skip with justification in the execution plan (workflow-planning).

## Where the output lands
Into the demand `spec` (and `decisions`), per unit when decomposed (D24). No
separate per-unit folders — units are checklist items in the execution plan.

## Depth by mode
FAST usually skips these (inline spec). Standard runs the rungs the demand
triggers, briefly. SAFE runs them with alternatives, dependencies, and evidence.
