# Demand type: Engineering (D5)

Types: refactor · tech debt · upgrade · migration · observability · performance · FinOps · internal automation · architecture · provider-driven change.

Common: short Inception (clear technical problem) with strong technical lens (`tech-inception`); reverse-eng matters (S1/D21); Design emphasis on **decisions/ADR**; Validation emphasis on **regression**; usually no external business Inception.

- **Refactor / tech debt:** behavior preserved → accept = "tests pass + behavior unchanged". SOLID/template central. Standard; broad refactor rises by complexity.
- **Upgrade:** breaking-change risk → review changelog/compat → update → regression → rollback. SAFE if major/many dependents.
- **Migration:** high risk → SAFE. Phased rollout (strangler/parallel-run), data care, explicit rollback; often N units (D24).
- **Performance:** baseline before/after + perf tests; ties to cost/FinOps (D10).
- **Security:** security skill (D22); tends SAFE; may originate as incident (D34).
- **Observability / internal automation / FinOps:** usually low risk → FAST/Standard.
- **Provider-driven (deprecation):** external deadline; treat as upgrade/migration by size.
