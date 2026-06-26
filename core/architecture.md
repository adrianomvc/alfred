# Architecture — 3 layers

Foundations: **Alfred = customized AI-DLC**, engine in `rules/`, modular layout without prefix.
Tracking: `state` always · `decisions` (Std/SAFE) · `audit` (all modes); Compliance is out of scope.

## Layers
1. **Framework** (this repo) — the methodology (customized AI-DLC). **Referenced, never copied** into HUB/App.
2. **HUB** (1 per sigla) — artifacts only; **source of truth** of `state`.
3. **App** (per repo) — technical artifacts under `.alfred/`.

## Hierarchy
`sigla → iniciativa → demanda`. A demand belongs to **one** sigla; it may touch **N apps** of that sigla. **No cross-sigla demands.**

## Distribution
- **HUB:** `state`, `problem`, `inception-input`, `tech-inception`, `requirements`, `risk`, `decisions`, `audit`, `metrics`, `summary`; `index`/`skills`/`knowledge` at sigla level; `metrics-rollup`.
- **App `.alfred/`:** `reverse-eng`, `spec` (technical), `investigation`, `audit` (technical), `metrics` (technical), `index`.
- **Correlation:** shared `id-demanda`; the HUB `state` links each app's `.alfred/<id>/`.

## SOLID / contracts
Rules depend on **roles/contracts** (a lane, an observability connector, a skill), never on the concrete (FAST, CloudWatch). Swapping CloudWatch→Datadog = new connector, rules untouched. See `connectors/connectors.md`, `skills/skills.md`, `rules/lanes/`.
