# Design sub-activity — Functional Design

> Trigger: the demand adds or changes **business logic** (new rules, algorithm,
> domain behavior). Optional, inside Design. Runs per unit when decomposed. Depth by mode.

## Purpose
Detailed **business logic design**, technology-agnostic — built on the component
boundaries from Application Design. This is the SDD clarity brake in practice
(D29): the logic is designed before any code.

## Inputs
`requirements`, Application Design (component structure), the unit being designed.

## Steps
1. Define the **domain model**: entities, relationships, key states.
2. Specify the **business rules**, validation, and constraints for the unit.
3. Describe the **logic/algorithm** at a level a reviewer can check against the
   acceptance criteria — no infrastructure concerns here.
4. Derive/confirm the **acceptance criteria** the logic must satisfy.
5. Keep it tech-agnostic; record open questions as `inferred / to confirm` (never invent).

## Output
Per-unit logic + domain model + rules + acceptance criteria in the `spec`.

## Depth by mode
FAST = approach in the PR description · Standard = domain model + rules + criteria ·
SAFE = + edge cases, invariants, and explicit alternatives in `decisions`.
