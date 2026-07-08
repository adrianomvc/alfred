# Knowledge

Knowledge contains always-on guardrails and defaults. It is not a skill: it is loaded according to scope.

**What lives here (owner decision):** the **company-wide rules and facts shared by every squad that uses Alfred** — this folder is the single source those squads inherit. It is not a template shipped empty: the values here (notification destinations, allowed catalogs, internal policies) are real and in force.

## Scopes
- **Org/company (this folder):** rules every squad inherits — notification/telemetry destinations, external-catalog allowlist, internal policies (naming, access, "repo via issue"...). One file per policy, following `policy-template.md`.
- **Sigla/HUB:** system-specific constraints, contacts, active skills — in each HUB's `knowledge/`.
- **Demand:** temporary decisions and overrides recorded in `state`/`decisions`.

## Rule
Company policy sets the floor. Sigla policy may be stricter, not weaker, unless a human records an explicit exception.

## Files
- `knowledge.md` — registry of policy scope and trigger; load it before selecting an org policy.
- `policy-template.md` — the mold for writing a new policy (identity → rule → enforcement → audit evidence).
- `notification.md` — company notification + telemetry destinations and triggers.
- `external-catalogs.md` — which external catalogs (e.g. Context7) Alfred may query, and the usage gates.
