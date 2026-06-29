# Design sub-activity — Application Design

> Trigger: a demand adds or changes a **component / service boundary** (new
> module, new integration, multi-app change). Optional, inside Design. Depth by mode.

## Purpose
High-level component design: **what the pieces are and how they talk** — not the
detailed business logic (that is Functional Design).

## Inputs
`requirements`, `tech-inception` (affected systems/apps), reverse-eng, any
applicable template (D35).

## Steps
1. Identify the main **components** and their single responsibility.
2. Define each component's **interface/contract** (inputs/outputs, events) — not internals.
3. Design the **service/orchestration layer** between components (who calls whom).
4. Map **dependencies and communication** (sync/async, contracts, ownership per app).
5. Record component decisions in `decisions`; feed the boundaries into Functional Design.

## Output
Component map + interfaces + dependencies in the `spec`; cross-app boundaries when
the demand touches several apps (D8). Decisions logged.

## Depth by mode
FAST = inline note if a component appears · Standard = component map + interfaces ·
SAFE = + alternatives, ownership per app, and dependency/risk analysis.
