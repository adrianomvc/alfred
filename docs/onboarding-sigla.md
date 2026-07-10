# Onboarding - New Sigla

Use this checklist when adopting Alfred for a new sigla/system.

## 1. Identify Scope
- sigla: *auto-derived from the repo name (`itau-<sigla>-...`) — never asked; a display label only (rule in `core/boot.md`).*
- HUB repo:
- app repos:
- squad owners:
- tracker source:
- notification policy:
- framework version:

## 2. Create HUB Root
Create `alfred-docs-hub/` in the HUB repo.

Minimum files:
- `001-index.md`
- `002-metrics-rollup.md`
- `003-insights.md`
- `knowledge/` when sigla-specific policies exist

The HUB must reference this framework repo/version. Do not copy framework files into the HUB.
Choose the reference mode using `docs/version-adoption.md` and record the selected version/ref/commit in the HUB index before the first demand.

## 3. Register Apps
For each app repo, create `.alfred-docs-app/`.

Minimum files:
- `001-index.md`

For brownfield apps, create or refresh reverse engineering before the first material change.

## 4. Configure Knowledge
Record mandatory policies that Alfred must always respect:
- repo creation rules;
- branch and PR rules;
- access rules;
- naming conventions;
- notification destinations;
- environment constraints;
- sensitive data rules.

Knowledge is a guardrail, not an optional skill.

## 5. Reference / Template Repos (optional)
Ask explicitly — but never block: **"Are there template/reference repos that show how this squad/stack builds (structure, conventions, scaffolding)?"**
- Record each as a **pointer** (repo URL/path + what it exemplifies: API, front, lib, IaC) in the HUB `001-index.md` — a pointer, not a copy (D3), resolved JIT (D35).
- **None is a valid answer.** Record "no template" so Design/Execution knowingly fall back to the conventions inferred from the app's reverse engineering.
- A template is **code to mirror**, not a skill — that is why it lives here, not under Configure Skills.

## 6. Configure Skills
Record active optional skills for the sigla:
- language-specific coding standards;
- security review;
- observability/log investigation;
- cloud/provider-specific practices.

Skills are opt-in and loaded JIT.

## 7. Run First Demand
Use `docs/quickstart-real-demand.md`.

The first demand should prove:
- boot/resume from `001-state.md`;
- HUB/App correlation by `id-demanda`;
- Risk Mode classification;
- requirements question flow;
- Design before Execution when Standard/SAFE;
- JSONL observability append discipline;
- metrics/audit update.

## 8. Acceptance
Onboarding is accepted when:
- one demand runs through all five phases or reaches a documented blocker;
- HUB and app artifacts are committed;
- observability JSONL parses;
- `001-state.md` is enough to resume;
- the adopted framework version/ref/commit is recorded;
- pending policies/skills are listed explicitly.
