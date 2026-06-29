# Knowledge Governance

Use this guide when defining always-on policies and guardrails for Alfred.

Knowledge is not a skill. A skill is an optional capability loaded just in time. Knowledge is an always-in-force constraint that affects every decision inside its scope.

## Scopes
| Scope | Location | Purpose |
|---|---|---|
| org/framework | `knowledge/` | organization-wide floors and defaults |
| sigla/HUB | `alfred-docs-hub/knowledge/` | system-specific restrictions, contacts, naming, access, notification destinations |
| demand | `001-state.md`, `02-design/006-decisions.md`, `05-operation/007-audit.md` | temporary decisions, exceptions, and approvals |

## Precedence
1. Org/framework policy sets the floor.
2. Sigla/HUB policy may add or tighten constraints.
3. Demand decisions may choose within the allowed space.
4. A weaker demand or sigla rule requires an explicit human exception with owner, reason, expiry, and audit entry.

When policies conflict, Alfred does not guess. It records the conflict and asks the responsible human.

## Policy Shape
Use `knowledge/policy-template.md` for new framework policies and mirror the same shape in HUB knowledge files.

The example `examples/fresh-sigla-onboarding/alfred-docs-hub/knowledge/policies.md` shows a sigla policy that requires SAFE when sensitive data is identified.

Every policy should define:
- identity and scope;
- status;
- mandatory rule;
- rationale;
- enforcement behavior;
- exception path;
- audit evidence.

## Runtime Loading
On boot or phase transition, Alfred loads:
- the repo index;
- current demand state;
- knowledge links for the active scope;
- only the policy files relevant to the current action.

Policies that apply to the scope are not optional. If they cannot be loaded and the action depends on them, Alfred must pause and ask.

## Exceptions
An exception must include:
- policy id;
- exception owner;
- approval date;
- expiry or review date;
- exact allowed deviation;
- affected demand or scope;
- audit link.

Open-ended exceptions are not valid framework defaults.

## Validation
Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-knowledge.ps1
```
```bash
python scripts/python/validate-knowledge.py
```

The validator checks the framework knowledge files, the policy template, and example HUB knowledge policies.
