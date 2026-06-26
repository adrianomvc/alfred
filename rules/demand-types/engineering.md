# Demand-type: Engineering — operational prompt (D5/D21/D24)

Types: refactor · debito tecnico · upgrade · migracao · observabilidade · performance · FinOps · automacao interna · arquitetura · mudanca por provedor.

## Common
Short Inception (clear technical problem) + strong technical lens (`tech-inception`); reverse-eng matters (refresh if stale, D21); Design emphasis on decisions/ADR; Validation emphasis on regression; usually no business inception.

## Subtype behavior
- Refactor / tech debt: behavior preserved → acceptance = "tests pass + behavior unchanged". SOLID/template central. Standard; broad refactor rises by complexity.
- Upgrade: breaking-change risk → review changelog/compat → update → regression → rollback. SAFE if major/many dependents.
- Migration: high risk → SAFE; phased rollout (strangler/parallel-run), data care, explicit rollback; usually N units (D24); phased PRs.
- Performance: baseline before/after + perf tests; ties to cost/FinOps (D10).
- Security: security skill (D22); tends SAFE; may originate as incident (D34).
- Observability / internal automation / FinOps: usually low risk → FAST/Standard.
- Provider-driven (deprecation): external deadline; treat as upgrade/migration by size.

## Edge cases
- Reverse-eng stale vs current commit → refresh before acting (D21); only touch with certainty (S1).
- Migration touching data → never irreversible without rollback + human ok (D27).

## Output example (pt-BR)
"Upgrade major (breaking) → propondo SAFE. Plano faseado (strangler) com rollback por release; 3 units. Preciso da aprovacao de arquitetura."
