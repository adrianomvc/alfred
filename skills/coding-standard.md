# Skill: coding-standard (SOLID base, D36)

Applied in Execution; checked by Reviewer in Validation. Overridden by an active `lang-*` skill (D22).

## SOLID
- **S**ingle responsibility · **O**pen/closed · **L**iskov substitution · **I**nterface segregation · **D**ependency inversion.

## Good practices
- Brownfield in-place (never `file_v2`); small, traceable changes.
- Automation-friendly (`data-testid` etc.).
- Mirror the applicable template (D35).
- Never invent API/lib/path — verify in reverse-eng/repo first (D41).
