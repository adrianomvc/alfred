# Changelog

All notable Alfred framework changes should be recorded here.

## Unreleased

### Added
- Lifecycle depth parity: the four remaining phases now materialize their sub-activities as JIT files, mirroring Design (A.2/D19). Each folder has a README with a trigger ladder plus one file per sub-activity (Trigger ▸ Purpose ▸ Inputs ▸ Steps ▸ Output ▸ Depth by mode):
  - `inception/sub-activities/`: business-inception, technical-inception, requirements-elicitation, risk-mode-proposal.
  - `execution/sub-activities/`: workflow-planning, unit-loop, code-generation, technical-review.
  - `validation/sub-activities/`: the 7 test strategies (unit, regression, integration, contract, e2e, performance, security).
  - `operations/sub-activities/`: metrics-collection, baseline-drift-check, closure-summary, hub-sync, strategic-notification, followup-conversion.
- Each phase file (`inception.md`, `execution.md`, `validation.md`, `operations.md`) now points to its `sub-activities/` ladder, with the invariant restated: sub-activities, never new phases. All 25 new files are tracked by `validate-framework` in both runtimes (PowerShell + Python).
- Markdown-SOLID directory pass (incremental, no big-bang):
  - `rules/README.md` — JIT entry index for the engine (two orthogonal axes + lifecycle + agents + common), the one top folder that had no entry point.
  - Folder entry-point convention documented in `core/architecture.md`: navigation index → `README.md` (one uniform JIT rule); contract registry → `<name>.md` (`skills.md`, `connectors.md`, `metrics.md`, `lifecycle.md`) as a deliberate, semantic exception.
  - Architecture SOLID now has an owner like code SOLID does: an **extension checklist** in `core/architecture.md`, cross-linked from `core/principles.md`, and enforced at framework-change review via `docs/framework-validation.md`.

- `validate-links` helper (both runtimes) — checks internal Markdown references (links + inline framework paths) still resolve after moves/renames; wired into `validate-framework` and documented in `docs/framework-validation.md`. Catches the kind of broken cross-reference the directory pass had to chase manually.
- Sandbox connector simulators (test doubles) so a demand can run end-to-end offline, before any real host/credential exists: `examples/connectors/tracker-sim-adapter.md` (+ `tracker-sim-demand.md` fixture) and `notification-sim-adapter.md`, joining the existing `vcs-git-dry-run-adapter.md`. All `status: dry-run`, deterministic, never mutating external state; validated by `validate-connectors` and tracked by `validate-framework`. The `examples/connectors/README.md` documents the triad as a sandbox walkthrough.

### Changed
- Presentation moved out of the kernel into `core/presentation/` (optional rendering layer, D3/OCP): `presentation.md` → `core/presentation/README.md` (the layer's navigation index) and `toolbar.md` → `core/presentation/toolbar.md`. All live references updated (`core/README.md`, root `README.md`, `scripts/README.md`, `docs/automation-fallback.md`, `docs/implementation-status.md`, both `validate-framework` scripts); validation passes 0/0.

## 0.2.2 - 2026-06-28

### Summary
Presentation, persona, and AI-DLC depth pass, kept within the v0.2 line.

### Added
- Personalized butler welcome (`core/welcome.md`) stating the 5 phases, the FAST/Standard/SAFE risk modes, and the interaction style, plus an ASCII flow of phases and risk lanes.
- Presentation profiles (`core/presentation.md`): one `state`, many renderers (`text` / `rich-cli` / `web`); the model stays on the compact source while helpers render (token economy). `render-toolbar` gains `-Profile rich` (ANSI color/bar/icons) and `-Profile web` (self-contained SVG). README embeds a self-contained flow SVG (`docs/assets/alfred-fluxo.svg`).
- Design sub-activities materialized as JIT files (`rules/lifecycle/design/sub-activities/`): user-stories, application-design, functional-design, nfr-design, infrastructure-design, with a trigger ladder — closing the AI-DLC depth gap (A.2/D19).
- Mid-workflow changes rule (`rules/common/workflow-changes.md`): safely add/skip/redo a sub-activity with confirm + impact warning + audit trail.

### Changed
- `escalation-triggers` now includes an error-handling recovery procedure with severity levels (critical/high/medium/low).

## 0.2.1 - 2026-06-28

### Added
- Installer auto-updates `~/.alfred` to the latest version on each `/alfred` boot (with the active-demand freeze safeguard), plus `-List`/`list` and one-step `-Rollback`/`rollback` to a previous release tag in both runtimes.

### Fixed
- Version-aware boot update: the welcome only fast-forwards when on the default branch; a pin/rollback (detached HEAD) is respected and survives boots instead of erroring. Re-running the installer recovers the latest from a pinned state and refreshes a stale `origin/HEAD`.

## 0.2.0 - 2026-06-28

### Summary
Portability, distribution, and governance pass over the 0.1.0 framework: a Python helper set, a DEVIN CLI installer with version pinning, per-type playbooks, a richer knowledge subsystem, and closure of the plan's open items.

### Added
- Python 3 helper set under `scripts/python/` mirroring every PowerShell helper, so the framework can be validated on machines without PowerShell (D3 portability).
- DEVIN CLI installer (`install/`) that clones the framework into `~/.alfred` and installs the `/alfred` skill; supports pinned versions via `-Version`/`ALFRED_VERSION` (D14/D15/D26).
- Per-type playbook convention (`rules/demand-types/playbooks/`) with a Migration playbook distilled from the real SQ9 migration (D5/3.6).
- Knowledge subsystem: richer policy template, `docs/knowledge-governance.md`, `docs/automation-fallback.md`, and a `validate-knowledge` helper (both runtimes) wired into framework validation (D42/D3).
- Branch promotion model and HUB vs App protection defined in `connectors/git.md` (D23, plan open item closed).
- External skill versioning policy (pinned default, opt-in track-latest) in `skills/skills.md` (plan 6.8 closed).

### Changed
- Helper scripts are now organized by runtime: `scripts/powershell/*.ps1` and `scripts/python/*.py`. Both runtimes accept the same flags and produce equivalent output.
- Docs and examples now reference the runtime-scoped script paths.

### Compatibility Notes
- Backward compatible with 0.1.0 artifacts. Demands stamped `0.1.0`/`0.1.0-dev` stay valid; new demands should stamp `0.2.0`.
- Releases are git tags `vMAJOR.MINOR.PATCH`; the installer's default tracks the `main` branch, `-Version vX.Y.Z` pins a release.

## 0.1.0 - 2026-06-28

### Summary
First operational Alfred framework release for markdown-first AI-DLC adoption across Framework/HUB/App layers.

### Added
- Markdown-first Framework/HUB/App structure.
- AI-DLC lifecycle adapted to Inception, Design, Execution, Validate, and Operation.
- Risk Mode lanes: FAST, Standard, SAFE, plus Operational Execution-first.
- HUB/App templates with phase folders.
- JSONL observability templates and metrics rollup helpers.
- Optional validation, boot, toolbar, staleness, SDD gate, and usage-cost scripts.
- Skill registry with base, language, and AWS data-platform skills.
- Version adoption policy for freezing and upgrading Alfred per demand.
- Environment-parameters template for external blockers.
- Host adapter states, implementation guide, and adapter template.
- Connector/adapters validation script and VCS dry-run adapter example.
- Model-policy validation script for lane floors, tier map, adjustments, override warning, and toolbar transparency.

### Compatibility Notes
- Framework files stay in English.
- Generated HUB/App artifacts are intended to be written in pt-BR.
- Active demands should keep their stamped framework version frozen unless a human approves an in-flight upgrade.
- Existing pilot artifacts stamped as `0.1.0-dev` remain valid historical records and should not be rewritten only to change the version.

### Migration Notes
- New demands should stamp `0.1.0` in `001-state.md`, metrics, audit, app index, and JSONL events.
- Active demands already running on `0.1.0-dev` should either stay frozen until close or record a human-approved in-flight upgrade.

### Validation
- `scripts/powershell/validate-framework.ps1` passed on 2026-06-28 for this release preparation.
