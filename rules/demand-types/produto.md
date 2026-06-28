# Demand-type — Produto (Product)

> Contract: `types covered` · `phase emphasis` · `typical sub-activities` · `mode tendency` · `special path`. References connectors/skills by **role**, not name.

## Types covered
New feature · functional improvement · new journey · UX improvement · experiment · business-rule change · product evolution.

## Phase emphasis
- **Design/SDD** — spec + acceptance criteria.
- **Validate** — user acceptance.

## Two-lens Inception
The **business lens usually arrives ready from an external agent** (problem statement, objective, scope, stories, business requirements). Alfred **does not redo** that discovery — it:
1. **Ingests** the external artifacts (`inception-input.md`);
2. **Validates completeness** (missing business info → ask the human/source, do not invent);
3. **Applies the technical Inception** lens → `005-tech-inception.md` (affected systems/apps via reverse-eng, integration points, technical constraints/risks, technical questions).

## Typical sub-activities (Design, by trigger)
user-stories (journey/UX) · application-design (new component).

## Mode tendency
Tends to **Standard**; **SAFE** if it touches the end customer / sensitive data / multi-app.

## Special path — experiment
Shortcut: **FAST** with a clear hypothesis; the learning is captured in Operation (metrics + summary), not in a heavy spec.
