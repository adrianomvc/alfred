# Onboarding - New Sigla

Use this checklist when adopting Alfred for a new sigla/system.

## How to onboard — confirm repo kind, then provision
On an empty or new HUB, first confirm that the current repo is the HUB when no
Alfred marker exists. A repo name like `*-hub` is a hint only, not evidence.
After HUB intent is confirmed, **act first, ask later** applies only to the
empty-HUB skeleton listed below (avoid bureaucracy):
1. **Sigla** — auto-derived from the repo name (`core/boot.md`); never asked.
2. **Create the HUB skeleton immediately** — `alfred-docs-hub/` with `001-index.md`, `002-metrics-rollup.md`, `003-insights.md` (+ `knowledge/` if sigla policies exist). Do **not** present a "how far to provision" scope menu, and do **not** interrogate for owner/apps/tracker first.
3. **Defer the rest as `pending`** in the index — owner, apps, and tracker are written as `pending` (they never block). Notification is **read** from `knowledge/notification.md` when configured, not asked. Apps and template repos resolve **per demand**, not at setup.
4. **Then offer one next step** in a single line — e.g. *"Casa pronta (sigla `sq9`; owner/apps pendentes). Quer iniciar uma demanda?"*.

This shortcut never authorizes starting a demand, cloning/fetching app code,
choosing initiative/demand identifiers, classifying a lane as accepted, or
creating demand artifacts. Those require the opening framing checkpoint in
`core/boot.md` and `docs/quickstart-real-demand.md`.

The numbered sections below describe **what** a HUB holds over time — a reference, **not a form to fill before creating the HUB**.

## 1. Scope (recorded in the index — `pending` is fine, never blocks)
- sigla: *auto-derived from the repo name (`itau-<sigla>-...`) — never asked (`core/boot.md`).*
- HUB: the current repo/directory holding `alfred-docs-hub/`.
- owner / squad: record if known, else `pending`.
- apps: resolved **per demand** (from the app repo the demand targets); `pending` until then.
- tracker: `pending`/omit — not asked.
- notification: read from `knowledge/notification.md`; not asked.
- framework version: stamped automatically at boot.

## 2. Create HUB Root
Create `alfred-docs-hub/` in the HUB repo.

Minimum files:
- `001-index.md`
- `002-metrics-rollup.md`
- `003-insights.md`
- `knowledge/` when sigla-specific policies exist

Template filenames are source names, not output names. When creating the HUB
root, write the canonical artifact names:
- `templates/hub/index.md` -> `alfred-docs-hub/001-index.md`
- `templates/hub/metrics-rollup.md` -> `alfred-docs-hub/002-metrics-rollup.md`
- `templates/hub/insights.md` -> `alfred-docs-hub/003-insights.md`
- `templates/hub/skills.md` -> `alfred-docs-hub/004-skills.md` when skills are registered

Do not create unnumbered HUB aliases such as `index.md`, `skills.md`, or
`metrics-rollup.md`.

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
