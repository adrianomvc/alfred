# Changelog

All notable Alfred framework changes should be recorded here.

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
- `scripts/validate-framework.ps1` passed on 2026-06-28 for this release preparation.
