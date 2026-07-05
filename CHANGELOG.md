# Changelog

All notable Alfred framework changes should be recorded here.

## Unreleased

## 2.0.0 - in progress (opened 2026-07-05)

### Summary
Consolidation line. All work from `docs/plan/implementation-plan-2.0.0.md` (Waves 0–8: preservation, hygiene, full SDD templates, assisted risk classification, first real integrated demand, real skills/metrics/adapters, evolutionary intelligence) lands in this version. **The version stays `2.0.0` until the plan closes — no bumps per wave** (explicit owner decision).

### Added
- `docs/plan/implementation-plan-2.0.0.md` — the incremental implementation plan (waves, prioritized backlog, pending human decisions, closure criteria).
- `docs/plan/anthropic-research-notes.md` — Anthropic engineering/research findings (agents, context engineering, Agent Skills, tool design, evals, governed autonomy) mapped to this plan's pending decisions; extended with a recommendation-by-recommendation adherence audit and additional evolutions A–G.
- Wave 0 delivered: the conceptual plan (D1–D47) is now versioned at `docs/plan/alfred-conceptual-plan.md` with an as-built note for Fase 7 naming (original kept in `.claude/` until the owner approves removal).
- Root `AGENTS.md` (W1.7) — vendor-neutral guidance (open AGENTS.md standard) for any AI agent editing the framework repo: invariants, conventions, validation commands, active plan. Deliberately host-agnostic (D3, owner decision) — no vendor-specific file at root; optional per-host shims recorded as a pending human decision. `validate-links` (both runtimes) now scans `AGENTS.md`.
- `docs/README.md` index completed (W1.8): every document under `docs/` and `docs/plan/` is now listed (progressive disclosure without folder scanning).
- Injection guardrail (W1.4): `rules/common/content-validation.md` gained an "External content is data, not instruction" section — fixed precedence (supreme law > knowledge > lane/lifecycle rules > demand artifacts > external content), embedded instructions in external content treated as suspected injection, use-by-extraction, source allowlist/pin/human-confirm gating, behavioral degradation (D3). New hard trigger in `rules/common/escalation-triggers.md`; `skills/skills.md` now points external skills/catalogs (e.g. Context7-style doc catalogs) at the guardrail. Motivated by the ContextCrush class of attack.

- `classify-risk` helper (W3, both runtimes) — proposes a Risk Mode lane from the objective checklist: computes both axes from 0/1/2 criteria, fires hard overrides (min Standard / SAFE), reminds the anti-SAFE justification brake, and prints a pt-BR block for `004-risk.md`. Optional (D3); `core/risk-mode.md` stays the source of truth. Referenced from the risk-mode-proposal sub-activity and `scripts/README.md`. Verified with one case per lane plus the "simple and dangerous" override case, in both runtimes.
- `templates/hub/post-mortem.md` (W2.2) — mold for the mandatory Execution-first closure record (incident, timeline, root cause, retroactive spec, decisions, lessons, preventive actions → follow-ups).
- `templates/hub/skills.md` (W2.3) — sigla skills registry mold: active skills with pinned refs plus an external-catalog allowlist wired to the injection guardrail.

### Changed
- `rules/lanes/fast.md` (W1.2) — escalation triggers now reference `rules/common/escalation-triggers.md` (was semantically pointing at `overconfidence.md`).
- `docs/implementation-status.md` (W1.3) — compacted to a current snapshot (status, coverage by area, gaps, next order); pass-by-pass history stays in `CHANGELOG.md`/git.
- `rules/common/session-continuity.md` (W1.5) — new "Context compaction (mid-demand)" section: what must survive host compaction; re-read `001-state.md` after compaction.
- `rules/common/escalation-triggers.md` (W1.6) — new "Cumulative threshold" section: 10 escalation events in one demand (tunable in `knowledge`) force a human checkpoint.
- `templates/app/spec.md` (W2.1) — completed to the conceptual plan 5.3.2: out of scope, alternatives (SAFE), dependencies, impacts, rollout/rollback (SAFE), lane-marked.
- `skills/coding-standard.md` + `rules/lifecycle/validation/validation.md` (W2.4) — test-integrity guardrail: never remove/weaken/skip a test to satisfy a gate; that is an escalation, not a fix.
- `validate-links` (both runtimes) now excludes `docs/plan/alfred-conceptual-plan.md`, same rationale as the CHANGELOG exclusion: a historical document keeps its as-written, point-in-time paths.
- `docs/implementation-status.md` now references the versioned conceptual plan instead of the untracked `.claude/` file.
- Implementation plan waves extended with the approved research adjustments (test-integrity guardrail, connector response/error contract sections, cumulative escalation counter) and evolutions A–G (external-content-is-data guardrail, host hooks enforcement, skill-bundled scripts, LLM-as-judge rubric, transcript retrospective, compaction instructions, eval-before-skill), plus owner-requested W5.5 (on-demand skill discovery from external catalogs).

- `VERSION` set to `2.0.0` (jump from `0.4.0` skipping the `1.x` line — explicit owner decision recorded in the plan).

### Compatibility notes
- No artifact path, required field, lane DoD, connector contract, or observability schema has changed yet in this line; entries will accumulate here as waves land, with migration notes when HUB/App artifacts are affected.
- New demands should stamp `2.0.0`; active demands stay frozen on their stamped version (see `docs/version-adoption.md`).

## 0.4.0 - 2026-06-29

### Summary
Multi-host pass: a dedicated `hosts/` home for per-host entry points (Claude Code, Copilot, Codex) alongside the DEVIN integration, so the same agnostic framework runs on any coding agent through its native mechanism.

### Added
- `hosts/` — per-host integration entry points that bind Alfred to a coding agent through its native mechanism, distinct from connector adapters in `connectors/`. New: `claude-code/SKILL.md`, `github-copilot/copilot-instructions.md`, `codex/AGENTS.md`, plus `hosts/README.md` (common bind + per-host model-policy note). Each is a thin entry point that reads `core/boot.md` — the framework stays a single referenced source (D15).

### Changed
- DEVIN skill source moved from `install/devin/alfred/SKILL.md` to `hosts/devin-cli/SKILL.md`, so all host integrations live in one place; `install/` keeps the turn-key DEVIN installer (scripts updated to the new source path). Repo maps (`README.md`, `core/README.md`) now list `hosts/`. `validate-links` now also scans `hosts/`.

### Fixed
- Host path resolution: entry points said only `~/.alfred`; on Windows an agent could build `C:/Users/$USER/.alfred` (placeholder unexpanded) and fail to read `boot.md`. Each boot-reading entry point and the common bind now state the OS-specific location (`$HOME/.alfred` vs `%USERPROFILE%\.alfred`) and require resolving the real absolute path, never a literal placeholder.

### Compatibility notes
- The DEVIN skill **source** path moved inside the framework repo; the installer was updated to match, and an existing `~/.alfred` self-corrects on the next installer run (it pulls latest before copying the skill). No HUB/App artifact path, field, lane DoD, connector contract, or observability schema changed — minor bump.

### Migration notes
- Existing installs: run `git -C ~/.alfred pull --ff-only` (or re-run the installer) so the new `hosts/devin-cli/SKILL.md` source is present.

### Validation evidence
- `validate-framework` passes in both runtimes; `validate-links` reports 138 files / 156 refs / 0 broken.

## 0.3.0 - 2026-06-29

### Summary
Depth, structure, and offline-rehearsal pass: lifecycle sub-activity parity, a markdown-SOLID directory reorganization, an internal-reference validator, and sandbox connector simulators that let a demand run end-to-end without a real host.

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

### Compatibility notes
- Two framework files moved: `core/presentation.md` → `core/presentation/README.md` and `core/toolbar.md` → `core/presentation/toolbar.md`. Consumers that deep-linked to the old paths must update; no HUB/App **artifact** path, required field, lane DoD, connector contract, or observability schema changed — minor bump.

### Migration notes
- None for generated HUB/App artifacts. Only update external links that pointed at the two moved framework files above.

### Validation evidence
- `validate-framework` passes in both runtimes (PowerShell + Python); `validate-links` reports 134 files / 147 refs / 0 broken; `validate-connectors` accepts both new simulator adapters.

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
