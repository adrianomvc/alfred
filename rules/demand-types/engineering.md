---
name: demand-type-engineering
description: Demand-type — Engineering
load: demand-type
triggers:
  phase: all
  lane: all
  demand-type: engineering
  agent: all
---

# Demand-type — Engineering

> Contract: `types covered` · `phase emphasis` · `typical sub-activities` · `mode tendency` · `special path`. References connectors/skills by **role**, not name.

## Types covered
Refactor · tech debt · upgrade · migration · performance · security · FinOps · internal automation · architecture · provider change.

## Common traits
Short Inception (clear technical problem) with a **strong technical lens** (`tech-inception`); **reverse-eng matters** (staleness-checked); Design emphasizes **decisions/ADR**; Validate emphasizes **regression**; usually no external business Inception.

## Sub-flows by type
- **Refactor / tech debt** — behavior **preserved**. Acceptance = "tests pass + behavior unchanged." SOLID/template at the center. Standard; broad refactor (many components) rises by complexity.
- **Upgrade (dependency/framework)** — risk comes from **breaking changes**. Steps: review changelog/compat → update → **regression** → rollback plan. **SAFE** override if major/breaking or many dependents.
- **Migration (tech/platform/provider)** — **high risk → SAFE**. Irreversibility + multi-component. Needs **phased rollout** (strangler/parallel-run), care with **data migration**, explicit **rollback**. Reverse-eng essential; often splits into several **units**.
- **Performance** — requires **baseline before/after** (metrics) and **performance tests** in Validate. Risk if it touches a hot path. Ties to cost/FinOps.
- **Security** — uses the **security skill** (precedence: most restrictive wins); tends SAFE; if a production vuln, may be born as an **incident** (Operacional).
- **Observability / internal automation / FinOps** — usually low risk/internal → FAST/Standard.
- **Provider change (deprecation)** — has an **external deadline**; risk by blast radius; treat as upgrade/migration by size.

## Mode tendency
Tends to **Standard**; **migration / architecture / security / breaking-upgrade → SAFE** (hard overrides).

## Sub-activities (Design, by trigger)
application-design · unit decomposition (`rules/common/units.md`) · NFR · infrastructure-design.

## Playbooks
Operational step-by-step roteiros for a type, loaded JIT when it applies (see `rules/demand-types/playbooks/`):
- Migration → `rules/demand-types/playbooks/migration.md`.
