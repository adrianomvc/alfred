# Validate sub-activity — End-to-End Testing

> Trigger: a **user-facing journey** is affected. Optional, inside Validate.
> The most expensive rung — use sparingly, on the critical path.

## Purpose
Prove the whole journey works from the user's entry point through to the outcome,
as a real user would experience it.

## Inputs
`user-stories` + acceptance criteria, the deployed/runnable build, automation
seams (`data-testid`), e2e tooling by role.

## Steps
1. Select the **critical journeys** the change affects (not every path).
2. Drive each journey end to end against a runnable build, using stable selectors.
3. Assert the **user-visible outcome** matches the acceptance criteria.
4. Record command/tool, environment, and result; capture evidence (logs/screens).
5. Flag journeys that could not be automated as a **manual check** with result.

## Output
E2E results per critical journey with evidence, and any manual-check notes in the
validation evidence.

## Depth by mode
FAST = skipped · Standard = one or two critical journeys · SAFE = full critical-
path coverage with captured evidence.
