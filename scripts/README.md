# Scripts

Scripts are optional helpers. The framework must keep working without them.

Python is the canonical helper runtime for Alfred helpers.
- `scripts/` - canonical Python 3 helpers (D3 portability).

New helper logic starts in Python. Documentation and examples should call the
Python helpers only. Installers remain OS-native under `install/`.

## Layout
| Folder | Holds | Members |
|---|---|---|
| `shared/` | the reusable implementation (imported by the thin drivers) | `common/` (jsonl, state, markdown, text helpers) · `validation/` · `toolbar/` (service, presenter, renderers, summary, state, active_demand) · `observability/` (hexagonal: `domain/`, `application/`, `infrastructure/`, `composition/`) · `model_policy.py` · `context_manifest.py` · `sdd_gate.py` · `email_tools.py` |
| `validators/` | checks that gate or verify (exit 0/1) | `validate-*` (framework, demand, links, connectors, knowledge, model-policy, scripts-architecture, observability-hygiene, observability-intelligence, reverse-eng-staleness, sdd-gate, skills-registry, toolbar-fixtures, tool-discovery-policy, token-economy-policy, context-compression-policy, context-manifest-fixtures, email-adapter) |
| `workflow/` | thin drivers used while running a demand | `alfred-boot` · `render-toolbar` · `resolve-model-policy` · `context-manifest` · `classify-risk` · `confidence-score` · `spec-vs-impl` · `memory-query` · `migrate-state-v2` · `context-read-advisor` · `devin-context-hook` · registry/host sync helpers |
| `metrics/` | thin drivers over measurement domains | observability drivers · `session-cost` · `budget-monitor` · `evaluate-context-benchmark` |
| `adapters/` (python only) | concrete connector adapters | `mcp-email-server` |

Most real logic lives in `shared/`; `workflow/` and `metrics/` files are thin CLI
drivers that delegate to it (enforced by `validators/validate-scripts-architecture.py`).
`scripts/_common.py` is a compatibility shim re-exporting `shared.common`.

## Canonical CLI
`python scripts/alfred.py` (installed as `alfred`) provides the governed happy
path: doctor, framework status/update, workspace detection, HUB init,
draft/requirements/start, demand status/validate/close, checkpoints, usage
import, and host sync. Human output is pt-BR by default; `--json` emits
`alfred.cli.v1`. Writes apply directly, are idempotent, and support `--dry-run`.
For the installer policy, see `AGENTS.md` § Conventions.

## Allowed helpers
- validate required sections in markdown artifacts
- summarize metrics rollups
- check links between HUB state and app artifacts
- parse example observability JSONL and verify required framework paths
- render the demand toolbar from a demand `001-state.md`
- collect local observability JSONL into a telemetry-style batch
- generate a Markdown metrics rollup and human-reviewable insights from local observability JSONL
- normalize host usage/cost exports into append-only observability events
- apply an approved rate card to exact usage events and append separate interaction cost events
- validate toolbar fixtures against the renderer output
- validate registered skills and required skill sections
- validate the notification e-mail adapter dry-run, allowlist refusal, and audit JSONL
- validate a real HUB/App demand before advancing or closing it
- boot a session by detecting Framework/HUB/App and listing resumable demands
- validate reverse-engineering staleness against an app commit
- validate the SDD clarity gate before Execution
- resolve the model-policy decision (tier/model/effort) for a demand step
- validate and adopt `origin/main` at each safe boundary, with a concurrency lock and honest offline degradation
- migrate legacy usage state to the typed `alfred.usage.v2` schema with a reviewable diff
- retrieve cross-demand memory with bounded progressive disclosure
- benchmark context retrieval token reduction and answer recall
- validate Devin environment blueprints without reading or exposing secret values

## Rule
Any script output must degrade to a manual markdown checklist when the host cannot run scripts.

## Available
Canonical helpers live at `scripts/<category>/<name>.py`. The `adapters/` folder contains concrete local adapters.
- `validate-framework` - optional local validation helper matching `docs/framework-validation.md`.
- `render-toolbar` - optional but preferred toolbar renderer derived from `001-state.md`; use it whenever available instead of hand-drawing. Profiles: `-Profile rich` (default, Unicode block) · `text` (ASCII fallback, CLI requires `-AllowTextFallback`) · `web` (self-contained SVG). On Claude Code, pass `-RegisterActive` so the Stop hook can target the active demand log. See `core/presentation/README.md`.
- `collect-observability` - optional local collector for JSONL events; it does not send data anywhere.
- `generate-metrics-rollup` - optional local Markdown rollup generator; separates usage tokens from cost events, includes cache reuse, artifact lineage, and data-quality coverage.
- `generate-metrics-insights` - optional proposal generator; emits human-reviewable insight blocks and never changes policies/rules automatically.
- `normalize-usage-cost` - optional adapter for host-exported token/cost usage records.
- `import-ccusage` - optional automatic importer for `ccusage session --json`; updates demand cost state for toolbar display. It does not append session totals to observability JSONL.
- `attribute-usage-transcript` - optional finer attribution from a host transcript (Claude Code); emits request-scoped `usage_attributed` events (legacy `-Granularity turn` remains an alias), de-duplicated by `requestId`, correlated to `promptId` when the host exposes it. `-EmitInteractions` adds derived `interaction_completed` aggregates. Cost stays `null` unless `-RateCardPath` supplies an approved interaction rate card.
- `apply-usage-rate-card` - optional cost attribution helper; reads token-exact `usage_attributed` events plus an approved `usage-rate-card` fixture and appends separate `usage_cost_attributed` events. It never allocates `ccusage` session totals.
- `validate-toolbar-fixtures` - optional drift check for toolbar examples.
- `validate-skills-registry` - optional consistency check for `skills/skills.md`.
- `validate-email-adapter` - optional behavior check for the Python-only notification adapter: dry-run report generation, allowlist refusal, and audit subject prefix.
- `validate-demand` - optional demand-level check for HUB/App artifacts, state, JSONL, skills, and adapter readiness.
- `alfred-boot` - optional boot/resume helper for detecting context and open demands.
- `validate-reverse-eng-staleness` - optional reverse-eng freshness check by recorded app commit.
- `validate-sdd-gate` - optional SDD clarity gate before Execution.
- `validate-links` - optional internal-reference check (Markdown links + inline framework paths) to catch broken cross-references after moves/renames.
- `classify-risk` - optional Risk Mode proposal from the objective checklist (`core/risk-mode.md`): computes both axes (0/1/2 criteria), fires hard overrides, applies the anti-SAFE brake reminder, and prints a pt-BR block for `004-risk.md`. The checklist stays the source of truth; the AI proposes and the human confirms.
- `mcp-email-server` - Python MCP stdio server implementing the `notification` connector: `send_email` (allowlist, `[Alfred-Framework]` prefix, audit JSONL, dry-run outbox by default, SMTP in active mode), `send_demand_report` (auto-attaches the demand's metrics/audit/summary/observability JSONL from `001-state.md` context), `send_telemetry` (batches every local observability JSONL to the org `telemetry_to` — provisional transport until the telemetry API, D45), and `email_status`. Destinations are **registered** in `~/.alfred-email.json` (or `ALFRED_EMAIL_CONFIG`), overridable by env vars. See `connectors/notification-email.md`.
- `spec-vs-impl` - optional heuristic comparison of spec acceptance criteria vs validation evidence: flags criteria with no textual echo in `013-validation-evidence.md` so the Reviewer/human looks at them. Informative by default; `-Strict` fails on gaps. It never approves.
- `confidence-score` - optional pre-Execution clarity score (0-100) composed from signals Alfred already records: unanswered `[Resposta]:` questions, unconfirmed lane, missing decisions/plan for Standard/SAFE, reverse-eng without commit. >=80 proceed · 50-79 review with human · <50 stop and escalate. The score informs; the human decides.
- `sync-host-shims` - refreshes copied native host entry files after `~/.alfred` updates, so Claude Code/DEVIN/Codex do not keep running stale host instructions. Use `-InstallHooks` with `-Host claude-code` to install the usage attribution Stop hook.
- `memory-query` - bounded startup/search/timeline/get access to HUB decision/gotcha memory; detail remains JIT.
- `migrate-state-v2` - idempotent legacy usage-state migration with `--check`, diff, ambiguity refusal, and explicit `--write`.
- `context-read-advisor` - advisory cost warning for large reads; it never denies access to authoritative source files.
- `evaluate-context-benchmark` - gates a 15+ case retrieval fixture at >=30% median token reduction and >=95% recall.
- `validate-devin-blueprint` - checks environment-tier placement and rejects secret literals in Devin blueprints.

## Python

Requires Python 3.

```bash
python scripts/validators/validate-framework.py
```

```bash
python scripts/workflow/render-toolbar.py -StatePath examples/toolbar-states/standard.md -Model GPT-5 -Cost "n/a"
```

```bash
python scripts/validators/validate-demand.py -HubDemandPath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/006-simulado-adocao-v2 --strict
```

```bash
python scripts/workflow/alfred-boot.py -Root .
```

```bash
python scripts/metrics/collect-observability.py -Root examples
```

```bash
python scripts/metrics/generate-metrics-rollup.py -Root examples
```

```bash
python scripts/metrics/generate-metrics-insights.py -Root examples
```

```bash
python scripts/metrics/normalize-usage-cost.py -InputPath examples/connectors/usage-export.jsonl
```

```bash
python scripts/metrics/import-ccusage.py -StatePath <hub-demand>/001-state.md -Host claude-code
```

```bash
python scripts/metrics/apply-usage-rate-card.py -InputPath <hub-demand>/05-operation/011-observability-log.jsonl -RateCardPath <approved-rate-card.json>
```

```bash
python scripts/workflow/sync-host-shims.py -Host claude-code
```

```bash
python scripts/validators/validate-toolbar-fixtures.py
```

```bash
python scripts/validators/validate-skills-registry.py
```

```bash
python scripts/validators/validate-reverse-eng-staleness.py -ReverseEngPath examples/staleness-fixtures/reverse-eng-fresh.md -CurrentCommit aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

```bash
python scripts/validators/validate-sdd-gate.py -HubDemandPath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/006-simulado-adocao-v2
```

```bash
python scripts/workflow/classify-risk.py -Reversibility 1 -BlastRadius 1 -SensitiveData 0 -CustomerImpact 1 -Cost 1 -Components 1 -Novelty 1 -Ambiguity 1 -Integrations 1 -Effort 1
```

Every other helper follows the same pattern:
`python scripts/<category>/<name>.py`. Flags also accept the
`--kebab-case` form, e.g. `--state-path`.
