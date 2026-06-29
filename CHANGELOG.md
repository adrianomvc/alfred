# Changelog

All notable Alfred framework changes should be recorded here.

## Unreleased

### Added
- Installer auto-updates `~/.alfred` to the latest version on each `/alfred` boot (with the active-demand freeze safeguard), plus `-List`/`list` and one-step `-Rollback`/`rollback` to a previous release tag in both runtimes.

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
