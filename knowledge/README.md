# Knowledge

Knowledge contains always-on guardrails and defaults. It is not a skill: it is loaded according to scope.

**What lives here (owner decision):** the **company-wide rules and facts shared by every squad that uses Alfred** — this folder is the single source those squads inherit. It is not a template shipped empty: the values here (notification destinations, allowed catalogs, internal policies) are real and in force.

**Corporate instance note:** this repository is a corporate instance of Alfred. The framework core (`core/`, `rules/`, `skills/` contracts) stays organization-agnostic; the org-specific values — the AI-Stack catalog, the telemetry destination in `notification.md`, internal URLs — are adoption configuration recorded here on purpose. Another organization adopting Alfred replaces the contents of `knowledge/` (and the org-specific skill entries), not the core.

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
- `external-catalogs.md` — **which external catalogs Alfred may query, in which order, and the usage gates.**
