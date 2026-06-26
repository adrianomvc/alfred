# Alfred

> Framework for hybrid squads (humans + AI agents) that chooses the level of process by **risk and complexity**, not by preference.
> Built on a customized AI-DLC. Markdown-agnostic, host-portable (DEVIN / Claude CLI / GitHub Copilot).
>
> *Alfred does not choose process by preference. Alfred chooses process by risk and complexity.*

> Note: framework files are in English (D47). Interactions and generated artifacts (HUB/App) are pt-BR.

## Structure (variant C — modular)
- `core/` — kernel + entry: principles, risk-mode, boot, model-policy, architecture, glossary.
- `rules/` — the engine (customized AI-DLC): `common/`, `demand-types/`, `lanes/`, `lifecycle/`, `agents/`.
- `skills/` — pluggable capabilities (opt-in, JIT): coding-standard (SOLID), lang-*, etc.
- `connectors/` — access to external systems (observability, vcs, tracker, notification, telemetry).
- `metrics/` — metrics definition, baselines, insights.
- `templates/` — artifact templates (`hub/`, `app/`, email).
- `knowledge/` — org policies/guardrails (always-in-force).
- `scripts/` — optional automation (everything degrades to manual).
- `docs/` — human docs. `examples/` — sample sigla/iniciativa/demanda.

## Layers (D8)
`Framework` (this repo, referenced) · `HUB` (1 per sigla, source of truth) · `App` (technical, `.alfred/`).
Hierarchy: **sigla → iniciativa → demanda**. One demand → N apps of the sigla. Correlated by `id-demanda`.

## Supreme law (D41)
Never invent. On any doubt, stop and ask. Ground before asserting. Human is in control (D7).

## Status
Skeleton (stubs). Conceptual design lives in the plan file `prompt-para-claude-ticklish-lemur.md` (D1–D47 + Appendices A–F).
Fill order: see plan Phase 8.1.
