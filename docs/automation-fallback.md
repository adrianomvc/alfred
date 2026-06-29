# Automation Fallback

Alfred is markdown-first. Automation is optional.

This means every helper script must have a manual Markdown/JSONL equivalent. Scripts may speed up validation, rendering, and rollups, but they must not become the source of truth or the only way to operate Alfred.

## Source of Truth
The source of truth is always:
- HUB `001-state.md`;
- App `001-index.md`;
- phase artifacts under `01-inception/` to `05-operation/`;
- `05-operation/*audit.md`;
- `05-operation/*metrics.md`;
- append-only `observability-log.jsonl`;
- decisions and summaries.

Scripts may read or derive from those files. If a script writes an output, that output is a derived artifact and must be reproducible manually.

## Script Rule
Every script must satisfy:
- optional execution;
- no hidden state outside the repository artifacts;
- deterministic output from Markdown/JSONL inputs when possible;
- clear manual fallback;
- no required host, shell, CI, IDE, or model runtime.

PowerShell and Python helpers may coexist. They are parallel conveniences, not competing sources of truth. Each helper ships as `scripts/powershell/<name>.ps1` and `scripts/python/<name>.py` with the same flags (the Python set shares small helpers in `scripts/python/_common.py`).

## Manual Fallback Matrix
| Helper (`<name>`) | Script output | Manual Markdown/JSONL fallback |
|---|---|---|
| `alfred-boot` | terminal context summary | read HUB `001-index.md` and demand `001-state.md`; list open demands manually |
| `render-toolbar` | terminal toolbar | render the toolbar text from `001-state.md` using `core/toolbar.md` |
| `validate-framework` | terminal validation result | execute `docs/framework-validation.md` checklist manually |
| `validate-demand` | terminal validation result | review required HUB/App artifacts, links, JSONL, audit, metrics, skills, and adapters manually |
| `validate-sdd-gate` | terminal validation result | review problem, requirements, risk, decisions, spec, and execution plan manually before Execution |
| `validate-reverse-eng-staleness` | terminal freshness result | compare recorded reverse-eng commit with current app commit manually |
| `validate-toolbar-fixtures` | fixture drift result | compare `examples/toolbar-fixtures/*` with `core/toolbar.md` manually |
| `validate-skills-registry` | registry consistency result | inspect `skills/skills.md` and each linked skill for required sections |
| `validate-connectors` | connector/adapter consistency result | inspect `connectors/*.md` and adapter examples against `connectors/adapter-template.md` |
| `validate-model-policy` | model-policy consistency result | inspect `core/model-policy.md` for lane floors, tiers, overrides, and toolbar transparency |
| `validate-knowledge` | knowledge consistency result | inspect `knowledge/policy-template.md` and HUB knowledge policies using `docs/knowledge-governance.md` |
| `collect-observability` | JSONL batch | concatenate relevant `observability-log.jsonl` files preserving source path and line references |
| `generate-metrics-rollup` | Markdown rollup | summarize JSONL events manually into `metrics-rollup.md` or `05-operation/008-metrics.md` |
| `normalize-usage-cost` | normalized usage JSONL events | manually append `usage_attributed` events only from approved host export data |

## Generated Artifacts
Generated outputs should live in normal Alfred artifact locations:
- demand metrics: `05-operation/008-metrics.md`;
- demand audit: `05-operation/007-audit.md`;
- observability: `05-operation/011-observability-log.jsonl` in HUB or `05-operation/008-observability-log.jsonl` in App;
- rollups: HUB-level metrics rollup;
- handoffs: `05-operation/009-hub-sync.md` or connector handoff files.

Temporary local outputs are allowed only as scratch data. They are not the official record unless copied into the relevant Markdown/JSONL artifact.

## Acceptance
A script is acceptable when a human can perform the same governance step by reading and updating Markdown/JSONL artifacts without running the script.
