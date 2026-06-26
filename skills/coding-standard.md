# Skill: coding-standard (SOLID base) — operational prompt (D36/D22)

APPLY when writing/modifying code (Execution); the Reviewer checks against it (Validation).
This is the BASE; if a `lang-<language>` skill is active and defines standards, IT WINS (more specific, D22).

## Enforce (SOLID)
- Single responsibility: one reason to change per unit/class/function.
- Open/closed: extend without modifying stable code.
- Liskov: subtypes are substitutable.
- Interface segregation: small, focused interfaces.
- Dependency inversion: depend on abstractions, not concretions.

## Good practices (always)
- Brownfield: modify in-place — NEVER create `Class_v2`, `file_new`.
- Small, traceable changes; commit per step on the demand branch.
- Automation-friendly UI (`data-testid` etc.).
- Mirror the applicable template (D35).
- Never invent API/lib/path — verify in reverse-eng/repo first (D41).

## Reviewer checklist (what to flag)
SRP violations · hidden coupling · missing tests · duplicated logic (DRY) · naming inconsistent with the template · TODO/FIXME left · broad changes beyond scope.

## If a language skill is missing
Apply this base; if language-specific decisions are needed and unclear, ASK before assuming (D41).
