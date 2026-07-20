# Changelog

All notable Alfred framework changes should be recorded here.

## Unreleased

### Added
- Layered transcript usage attribution (usage-cost Layers 1-3):
  `scripts/metrics/attribute-usage-transcript.py` maps a durable host
  transcript (Claude Code) into request-scoped `usage_attributed` events and
  optional `interaction_completed` aggregates. Tokens are exact and
  de-duplicated by `requestId`; human interaction ids use host `promptId` when
  present, otherwise derived user boundaries or `interaction_confidence:
  unavailable`. The legacy `--granularity turn` flag remains an alias for
  request. Cost stays `null` unless `--rate-card-path` supplies an approved
  interaction rate card. `claude-code-usage-hook.py` plus
  `core/hooks/usage-attribution.md` run incrementally from a Claude Code Stop
  hook, can write sanitized raw JSONL via `AI_OBS_RAW_LOG`, and never block the
  host.
- `scripts/metrics/apply-usage-rate-card.py` and the
  `usage-rate-card` connector append `usage_cost_attributed` events from exact
  usage plus an approved rate card. This keeps interaction cost separate from
  `ccusage` session totals.
- `validate-observability-hygiene` validator: example event logs must use real,
  distinct ISO-8601 timestamps (no placeholders, not all-identical), guarding the
  Layer 0 hygiene contract that later attribution depends on.
- `generate-metrics-rollup.py` now separates usage tokens from cost events,
  includes cache creation/read/output and `cache_reuse_ratio`, normalizes
  legacy `artifacts_used`, and reports data-quality coverage.
- `generate-metrics-insights.py` proposes evidence-backed policy/rule/skill
  insights without changing policies automatically.
- Shared SOLID package under `scripts/shared/`, with the first implemented
  subdomain at `scripts/shared/observability/`: domain
  models, application ports/use cases, infrastructure repositories, host adapter
  registry, and toolbar presentation view models. This keeps scripts
  host-agnostic while allowing Claude Code, Codex, Devin, ccusage, and generic
  adapters to remain thin edge implementations.
- `skills/ai-stack-finder/` plus the AI Stack (`@ai-stack/cli`) entry in the
  `knowledge/external-catalogs.md` allowlist: the internal Itaú catalog of
  already-built skills, MCP servers, and toolkits, queried at the fallback step
  before building an integration from scratch.
- `assert_bash_only_installer_policy` in `validate-framework.py`: fails if
  `install/install.ps1` reappears, if `install/install.sh` loses its bash
  shebang, or if a live doc still points at the PowerShell installer. Historical
  records (`CHANGELOG.md`, `docs/plan/*`) are out of scope by design.
- Executable governance in the lifecycle CLI (Wave 10): typed acceptance
  (Reject / Request changes never close a demand), lane-scoped closing evidence
  (Standard requires PR/merge/reviewer; SAFE additionally approvals, rollback,
  and security), strict validation that also covers the App side, and an audit
  entry for every acceptance.
- `scripts/shared/risk.py` as the single risk-criteria implementation: the lane
  is now derived from the risk criteria and confirmed by a human with an audited
  justification, instead of being asked outright. Demand type, urgency, and
  owner are captured in the draft, and the sigla stays derived from the repo
  name.
- `scripts/shared/common/observability_event.py`: canonical v1 observability
  events carrying `ts`, `event_type`, `event_id`, and a monotonic sequence. The
  unspecified "v2" event shape was abandoned rather than shipped.
- `scripts/validators/validate-invariants.py`: non-blocking advisory pass over
  the framework invariants (currently the ~1-screen file rule), reported as
  warnings so it never gates a merge.
- `tests/scripts/unit/test_governance_gates.py`: 18 tests pinning the gates that
  the contracts promise — acceptance outcomes, lane evidence, phase-jump audit,
  budget modes, attachment restrictions, and telemetry sanitization — including a
  full Standard end-to-end (draft → start with a derived lane → `--complete` per
  phase through the SDD gate → close with lane evidence → rollup).
- Governance rules for the edge cases that had none: a tie between two humans
  (`core/squad.md` — one owner per axis decides; a cross-axis tie pauses the step,
  records both positions, and goes to the Sponsor; safety is never a tie), an
  emergency stabilization that fails or regresses
  (`rules/demand-types/operational.md` — raise severity, force SAFE, one
  authorized action at a time, post-mortem covers both cycles), and replan versus
  cancel (`rules/lifecycle/lifecycle.md` — `replanejada` keeps id and history and
  needs an audited `--force`; reverting shipped work is a separate `vcs`
  question).

### Removed
- `install/install.ps1`. The installer is bash-only (`install/install.sh`);
  the Windows path is Git Bash, which the installer already detects
  (`MINGW*|MSYS*|CYGWIN*`). The `/alfred` skill installs to `~/.agents/skills`
  on every platform.

### Fixed
- `ccusage` session totals are now state-only for toolbar/forecast display:
  `import-ccusage.py` updates `001-state.md` with `cost granularity: session`
  and no longer appends session totals to observability JSONL as
  `usage_attributed`. Interaction JSONL usage now requires an
  interaction/request-granular source such as a host transcript.
- `--allocate-cost` / `--session-cost-usd` are no longer accepted for transcript
  interaction attribution, preventing proportional allocation of session totals
  into JSONL interactions.
- Claude Code usage attribution is now wired into the runtime path:
  `render-toolbar` can register the active demand (`-RegisterActive`), the Stop
  hook falls back to `~/.alfred/runtime/active-demand.json` when no
  `ALFRED_STATE_PATH` is set, and `sync-host-shims.py -Host claude-code -Create
  -InstallHooks` installs the hook while preserving existing settings. Metrics
  rollup counts the latest event per `event_id`, so repeated session snapshots do
  not double-count tokens/cost.
- `import-ccusage.py` now resolves the `ccusage` executable via `shutil.which`
  before spawning it, so Windows npm shims (`ccusage.cmd`) are found instead of
  failing with `WinError 2`. When it is still unreachable, the helper exits with
  a clear message pointing to the `-InputPath` fallback instead of a raw
  traceback.
- Claude Code policy snapshots now emit `policy_snapshot` instead of
  `artifact_accessed`; metrics rollups ignore snapshot entries for real
  artifact reads, repeated reads, and loaded-artifact analysis.
- `validate-demand` catches two deviations that read as plausible markdown but
  break the runtime: a state with translated headings (`## Demanda` instead of
  `## Demand`), where `write_state_fields` cannot find the section and appends a
  second one when inserting a new key; and a phase name parked in `status`
  (`status: inception`), which leaves the demand reporting no lifecycle state.
  The two example states were migrated to English headings — yesterday's
  normalization reached the templates and left the examples behind, so every new
  demand and every existing example disagreed. The strict simulado stays 0/0.
- Step 6 in `core/boot.md`'s host shims tells the agent to run
  `alfred demand validate` at every phase transition and before closing. It is
  the only thing that catches a demand assembled by hand: a full set of markdown
  artifacts that never touched the CLI has no observability events at all.
- Devin token usage is attributed without any API. The plan carried Session
  Insights / the Consumption API as a blocker for W6.2, but that is only true for
  **cost**: the local session transcript already holds exact per-step
  `prompt_tokens`/`completion_tokens` with real timestamps, the model that ran,
  and human turn boundaries (`source: user`). Verified against a real session —
  the per-step values sum exactly to `final_metrics` (4,968,055 / 27,297).
  `scripts/metrics/attribute-usage-devin.py` emits one `usage_attributed` event
  per step, de-duplicated by step id and idempotent on re-runs.
  `AdapterCapabilities.request_tokens` for Devin was declaring `False` and is now
  true in both senses.
- Cost stays `null` on that path, deliberately. Devin publishes ACU only through
  the web UI, and it does not bill per token, so no coefficient could turn these
  tokens into ACU without inventing one and presenting it as measurement. USD
  still comes only from a measured ACU figure times an approved rate card. The
  framework gate now pins "never convert tokens into ACU" as the invariant.
- Alfred reads the model a DEVIN CLI session actually ran, instead of showing an
  unconfirmed policy target. Devin exposes no live model to scripts (no env var,
  hook field, or session metadata), but the CLI logs the resolved model at
  session start (`resolved_model_uid=...`) and writes `agent.model_name` into the
  session transcript. `scripts/workflow/detect-host-model.py` stamps it into the
  demand state, so the toolbar reports fact. The log is preferred: it is written
  when the session opens, while the transcript only appears when it ends. Only
  those fields are read — transcript `steps` carry session content and telemetry
  is emailed to the org destination.
- The tier -> model map is per host. `resolve_model_policy` already accepted a
  map but every caller got the Claude one, so a Devin session was told to target
  `claude-opus-4-8`, a model the DEVIN CLI cannot run. `core/model-policy.md`
  documented the Devin map in prose; it now exists in code.
- The rich toolbar no longer truncates HITL and Modelo into a fixed 30-character
  cut plus an unbounded model string. They share a line only when both fit whole,
  and split otherwise. This was not cosmetic: the text being cut was the model's
  own `nao confirmado` qualifier, so the truncation turned an honest hedge into
  an apparent claim that a model had run.
- The rules now name the command that creates a draft. `core/boot.md` and the
  five host shims said "write the questions in `003-requirements.md` with
  `[Resposta]:` slots" and never mentioned `alfred demand draft`, so an agent
  following them authored the file by hand — a faithful reading of the text. The
  hand-written file carries no `<!-- field: -->` markers, no `[Alternativas]`
  blocks, and none of the ten risk/complexity criteria, so it parses as zero
  fields and the lane cannot be derived. The plain-markdown fallback stays
  explicit (copy the template verbatim), so D3 is preserved.
- `demand start` refuses a requirements file where no field is recognised,
  naming the cause and the way out. It previously accepted `{}` and would build a
  demand with no ids, no risk criteria, and no lane.
- `.github/workflows/validate.yml` is no longer a required path. It is GitHub
  Actions plumbing that runs neither at install nor at runtime, so requiring it
  made the framework unvalidatable wherever CI does not exist — a mirror that
  does not copy `.github/`, a corporate GitHub that blocks workflows, an offline
  copy, a zip export. That crosses the D3 line ("no feature may require a
  specific model, API, CI, or UI") and blocked a real corporate install, where
  the person had reasonably skipped `.github/` as repo metadata.
  `validate-invariants.py` now reports its absence as a non-blocking hint, and a
  test asserts no `.github/` path is ever required again.
- The installer no longer hides why `rtk init -g` failed, and no longer implies
  it is pending work on a Devin machine. `rtk init -g` configures Claude Code
  (plus `--opencode`/`--gemini`), and `rtk hook` has no Devin target at all, so
  on a Devin-only machine it has nothing to configure and fails as expected —
  Devin is covered by Alfred's own PreToolUse bridge installed right after. The
  output was swallowed by `>/dev/null 2>&1` and the message said "Run it manually
  when ready", sending people to re-run a command that fails again.
- Telemetry path sanitization no longer depends on the host OS. It used
  `os.path.isabs()`, which answers only for the running platform, so a Windows
  path processed on Linux (`C:/abs/path/001-state.md`) was shipped whole instead
  of being reduced to its filename. Absolute paths are now matched explicitly for
  POSIX roots, drive letters, and UNC shares; relative artifact paths still
  survive intact. Caught by the CI Ubuntu leg, which the Windows leg could not see.
- The SDD gate on entry to Execution crashed with a `TypeError` instead of
  blocking: `_transition_gate` joined `run_sdd_gate`'s
  `(severity, code, message)` triples as if they were strings, so the
  Standard/SAFE gate had never actually fired. Found by the new Standard E2E.
- `validate-context-budget.py` reported `OK budget 8453 <= 8400 tk` for scenarios
  that busted their cap: the `else` was bound to the growth-cap check alone. A
  scenario is now only OK when it is under both caps, and the line names both.
- `state` is once again a single source of truth: `write_state_fields` replaces
  the last occurrence of a key and drops the duplicates instead of appending,
  `migrate-state-v2` de-duplicates on migration, and `validate-demand` now fails
  on a duplicated key rather than silently reading one of them.
- `demand start` is atomic: it stages the demand folder and commits it with
  `os.replace`, refuses to overwrite an existing App demand, keeps the draft
  until the very end, and rolls back on partial failure.
- Checkpoints no longer auto-update. A stale cache produces a warning; adoption
  happens only at boot or through an explicit command. Phase transitions are
  sequential (`--complete` per phase), the SDD gate runs on entry to Execution
  for Standard/SAFE, and `--force` is audited.
- Email adapter hardening: attachments are restricted by root, extension, and
  size; an active send aborts when its audit entry cannot be persisted; and
  telemetry is sanitized through a field allowlist (no `user@hostname`, no
  absolute paths, no unparsed lines). The org destination is unchanged, by owner
  decision.
- Installer: `mode: dry-run` replaces the `auto` value the adapter never
  supported, a blocked update no longer aborts the reinstall, `--quiet` is gated,
  and resolved npm versions are logged.
- Windows robustness: UTF-8 subprocesses across the CLI, a toolbar that degrades
  to ASCII on non-UTF-8 consoles, and CLI errors without raw tracebacks.
- Documentation consistency: removed the phantom "Code Generator" agent and the
  phantom `units-generation` sub-activity, fixed the `scripts/*/workflow/` glob,
  reconciled "FAST has no Design", unified the attempt ceiling in the
  verification loop, completed the commons list in `rules/README.md`, made refs
  root-relative, added the artifact→template map, and switched template headings
  to English (content stays pt-BR, D47).

### Changed
- External catalog fallback is now a **total order** (AI Stack → AWS → Context7)
  for any topic, stopping at the first catalog that answers, and it runs only at
  the fallback step — not as a per-turn preamble. Supersedes the previous
  topic-routed rule (AWS-first for AWS topics, Context7 as the general
  fallback), which left overlaps undefined: Athena/Hive is simultaneously an AWS
  topic and an internal Itaú platform. The order is declared once in
  `knowledge/external-catalogs.md`; `skills/skills.md`, `docs/skills-activation.md`,
  `templates/hub/skills.md`, and `install.sh` now point at it instead of
  transcribing it.
- `knowledge/external-catalogs.md` § enforcement now defines **pin granularity**
  (the pinned ref is the content — the resolved `<name>@<version>`, library id, or
  commit — never the catalog client, which is transport) and **discovery ≠
  adoption** (querying a catalog is fetching data; installing a skill/MCP is an
  adoption event requiring human confirmation for both `install -s` and
  `mcp install`).
- Observability event hygiene is now an explicit contract (Layer 0): events must
  carry a real ISO-8601 `ts` from the system clock (never a placeholder), a real
  host `session_id`, stable `trace_id`/`ALFRED_RUN_ID`, and the Execution commit,
  so later usage attribution has precise window boundaries. `metrics/metrics.md`
  documents why per-event tokens/cost stay `null` on hosts without per-interaction
  usage (session totals arrive in state for toolbar display; interaction tokens
  can arrive as `usage_attributed`) and directs running the `usage-cost` import
  at each checkpoint, not only at close.
- Toolbar forecast display now explains why the total estimate is unavailable
  when cost exists but progress is still 0% or already 100%, instead of hiding
  the forecast line.
- Alfred's butler persona now uses gender-neutral address for people: rendered
  welcome/UI text avoids `senhor`, `senhora`, and `senhor(a)`, and validation
  guards the neutral-address rule.
- Host entry updates now include `sync-host-shims.py`, so pulling `~/.alfred`
  can refresh copied Claude Code/DEVIN/Codex entry files instead of leaving
  stale host instructions active.
- `ccusage` session import is now an active automatic usage-cost path for local
  CLI hosts: `scripts/metrics/import-ccusage.py` maps `ccusage session
  --json` into `001-state.md` session cost fields with estimated confidence and
  auditable session-selection metadata.
- Requirements questions are file-only: `003-requirements.md` is the single answer channel, chat/UI may only point to it, host-native question popups are forbidden for requirements, and FAST material questions still go to the artifact. The framework validator now guards this rule.
- Toolbar rendering is now explicitly grounded: boot/orchestrator prefer `render-toolbar`; if the helper is unavailable, agents must load `toolbar-quick.md` and use only the documented text fallback instead of hand-drawing rich blocks.
- Claude Code cost capture is now an explicit manual usage-cost path: humans can run `/cost`, record `cost usd`/source/confidence in `001-state.md`, and the toolbar renderer reads that state value for display and forecast.
- Toolbar CLI now guards against accidental ASCII fallback: `--profile text` requires `--allow-text-fallback`; capable hosts should omit `--profile` or use `--profile rich`.
- Installers can now best-effort install optional npm tools from a corporate registry / Artifactory: `ccusage` and `codebase-memory`, with package-name overrides and skip flags.
- Toolbar rendering now consumes a usage summary view model and separates
  session cost from demand cost. Session totals can be displayed with scope and
  confidence, but demand forecasts require demand-scoped cost with sufficient
  coverage.

## 2.0.0 - in progress (opened 2026-07-05)

### Summary
Consolidation line. All work from `docs/plan/implementation-plan-2.0.0.md` (Waves 0–9: preservation, hygiene, full SDD templates, assisted risk classification, first real integrated demand, real skills/metrics/adapters, evolutionary intelligence, and Devin/context hardening) lands in this version. **The version stays `2.0.0` until the plan closes — no bumps per wave** (explicit owner decision).

### Added
- Wave 9 hardening: typed `alfred.usage.v2` state and migration, strict Devin
  `/usage` parsing with reset-safe deltas, same-unit budget monitoring, shared
  approved ACU rate validation, and toolbar derivation without invented USD.
- Progressive-disclosure memory (`startup/search/timeline/get`), structural
  context retrieval policy, non-blocking read advisor, and a 15-case benchmark
  gate requiring token reduction without sacrificing recall.
- Devin execution hardening: least-privilege config templates, environment-tier
  blueprint validation, secrets outside YAML/argv, SessionStart/PostCompaction
  state reinjection, capability probes, rollout/build-health/pinning policy, and
  an explicit five-pilot release evidence matrix.
- Executable verification-loop fields, fresh-review guidance, separate
  worktrees for parallel writers, cross-platform GitHub Actions validation, and
  mandatory SHA-256 verification for downloaded RTK packages.
- ManagerWorker-aligned execution refinement: guided autonomy on the first
  attempt, corrective feedback on the second, strict-minimal scope on the third,
  compact evidence-bearing exploration reports, conditional delegation, and an
  A/B routing eval that measures total usage rather than strong tokens alone.
- Usage-cost adoption design: `docs/usage-cost-adoption.md` defines the next measurement path with Devin Session Insights + Consumption API as the primary ACU source, `ccusage` as a secondary local-CLI source, `ALFRED_RUN_ID`/`devin-...` correlation, confidence labels, and a pilot checklist before automatic model-policy suggestions.
- Token economy policies: `rules/common/token-budget-policy.md` adds context-budget preflight before large loads/token-heavy work, and `rules/common/deferred-work-policy.md` allows batch/flex/background execution only for non-critical-path drafts such as rollups, read-only scans, stale reverse-eng refreshes, summaries, and notifications. `validate-token-economy-policy` keeps the wiring intact.
- Context compression policy: `rules/common/context-compression-policy.md` allows RAG/compressed summaries for safe context selection while requiring original sources for code edits, Design decisions, SAFE/incident judgment, and validation evidence. Design, Execution, Code Generation, Validate, boot, and `validate-context-compression-policy` now enforce that boundary.
- Tool discovery / JIT tools policy: `rules/common/tool-discovery-policy.md` defines progressive tool, skill, connector, MCP, and external-catalog loading. Host shims and connector guidance now tell agents to select the capability before loading/calling full schemas, and `validate-tool-discovery-policy` guards MCP tool description size.
- Prompt caching policy: `rules/common/prompt-caching-policy.md` makes stable-prefix loading explicit for hosts with prompt caching/persistent context, and context-manifest validation now guards the cache-friendly prefix.
- RTK terminal-token policy and DEVIN CLI hook docs: `rules/common/terminal-token-policy.md` defines bounded terminal-output behavior, `core/hooks/rtk.md` documents optional RTK setup, and the DEVIN installer can run `rtk init -g` or download RTK when `-RtkUrl` / `ALFRED_RTK_URL` is provided. No URL means no download; Alfred degrades to bounded native commands.
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
- Helper runtime policy simplified: Python is now the canonical runtime for helper logic and documented helper commands. `install.ps1` and `install.sh` stay OS-native bootstraps. Existing non-canonical helper entry points are no longer advertised in active docs and can be removed gradually when touched.
- E-mail adapter audit hardening: refused allowlist attempts now record the normalized `[Alfred-Framework]` subject in audit JSONL, matching the notification connector contract. New `validate-email-adapter` behavior check covers dry-run report generation, allowlist refusal, `.eml` outbox creation, and audit subject prefix.
- Examples cleanup: stale SQ9 historical demand snapshots were removed from the maintained example suite. `006-simulado-adocao-v2` is now the SQ9 strict regression demand; lane toolbar coverage moved to small `examples/toolbar-states/` fixtures with `examples/examples.md` declaring tiers.
- Context7 activated as an allowlisted external catalog (owner decision): org policy `knowledge/external-catalogs.md` (policy-template format) records the allowlist and the four usage gates; DEVIN per-project MCP registration via `hosts/devin-cli/config.local.template.json` (alfred-email + context7 stdio servers) — the `/alfred` skill offers to create `.devin/config.local.json` from it on first boot (human confirms; context7 block removable). Installers point DEVIN users at the template.
- Telemetry by e-mail (owner decision — provisional transport until the telemetry API exists, D45): new `send_telemetry` MCP tool batches every local observability JSONL (each line = `{sender, collected_at, source, event}`, sender = user@host) and mails it to the org `telemetry_to` destination registered in `knowledge/notification.md`; installers copy that destination into each runner's `~/.alfred-email.json`; the strategic-notification sub-activity fires it automatically at every generation that appends events (closure, hub-sync, rollup), audited, no per-send prompt (durable authorization). Swapping to the real API later changes only the transport, not the rules.
- Installers (`install/`, both runtimes) now set up the notification adapter (owner decision): prompt for the destination e-mail (`-Email` / `ALFRED_EMAIL`; interactive prompt otherwise; `-SkipEmail` / `ALFRED_SKIP_EMAIL=1` to skip), write `~/.alfred-email.json` in dry-run mode (never overwriting an existing config), and register the `alfred-email` MCP server in Claude Code (user scope) when the CLI and Python are available. Best-effort: no failure breaks the install; everything degrades to the manual handoff (D3).
- Phase names: EN stays canonical everywhere (folders, rules, validators); pt-BR aliases **"O quê · Como · Fazer · Validar · Operar"** registered in `core/glossary.md` and shown in the welcome phase table (owner decision — presentation layer only, D47).
- `scripts/` reorganized by responsibility, mirrored in both runtimes: `validators/` (all `validate-*`), `workflow/` (alfred-boot, render-toolbar, classify-risk, confidence-score, spec-vs-impl), `metrics/` (collect-observability, generate-metrics-rollup, normalize-usage-cost), and python-only `adapters/` (mcp-email-server). `_common.py` stays at the runtime root. All internal imports/spawns and every repo reference updated; verified by `validate-framework`, `validate-links`, boot, strict demand validation, and classify-risk smoke tests in both runtimes.
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

- Owner approvals batch (2026-07-05, "aprovo 1–7"):
  - `templates/hub/decision.md` removed (W1.1) — `decisions.md` is the single decision format (append-only table + optional long-form block).
  - Agent Skills open-standard frontmatter (`name`/`description`) added to all 7 skills; registry documents the convention, skill-bundled helpers, and the "eval before skill" discipline (W5.3/W5.4).
  - On-demand skill/doc discovery in **allowlisted external catalogs** (e.g. Context7) documented in `skills/skills.md` with 4 mandatory gates (W5.5).
  - Root `CLAUDE.md` one-line shim importing `AGENTS.md` (content stays vendor-neutral; the shim is a host binding, D3).
  - `rules/demand-types/produto.md` → `product.md`, `operacional.md` → `operational.md` (D47 language consistency); all references updated.
  - `core/squad.md` gains SRE/On-call, Security, and FinOps as checkpoint owners (SAFE/emergency) with recorded fallback.
  - Original untracked conceptual plan removed from `.claude/` after byte-level verification against the committed copy.
- Examples fixed: app-side `05-operation/008-observability-log.jsonl` added to the 5 example app demands — `validate-demand --app-demand-path` now passes (pre-existing gap).
- `mcp-email-server` (`scripts/`, **Python-only by owner decision**) — the first concrete connector adapter: an MCP stdio server (stdlib only, no dependencies) implementing the `notification` contract. Tools `send_email` (allowlist gating with human-only unblock, `[Alfred-Framework]` subject prefix, per-attempt audit JSONL, dry-run outbox by default, SMTP/STARTTLS in active mode) and `email_status`. Tested end-to-end: MCP handshake, dry-run compose, allowlist refusal audited. Registered per host via MCP (e.g. `claude mcp add alfred-email -- python .../mcp-email-server.py`). Resolves the D44 channel decision (MCP + Python); `active` state awaits real SMTP credentials.
- `mcp-email-server` gains a **registered destination** (JSON config at `~/.alfred-email.json` or `ALFRED_EMAIL_CONFIG`; env vars override) and a `send_demand_report` tool that reads `001-state.md` and auto-attaches the demand's metrics, audit, summary, and observability JSONL (short body + attachments, per the D44 e-mail pattern). `knowledge/notification.md` documents the registration precedence (HUB knowledge → config file → env).
- `spec-vs-impl` helper (W8.2, both runtimes) — heuristic coverage check of spec acceptance criteria against `013-validation-evidence.md`; flags gaps, never approves. Its first run caught a real gap in the 2.0.0 rehearsal demand (app-side criteria missing from the HUB evidence), now fixed.
- `confidence-score` helper (W8.1, both runtimes) — pre-Execution clarity score from recorded signals (unanswered questions, unconfirmed lane, missing decisions/plan for Standard/SAFE, reverse-eng without commit); below the floor the verdict is the escalation rule. The score informs; the human decides.
- `connectors/connectors.md` — "Response format & error guidance" adapter-design section (concise replies, actionable errors, transcript evaluation before `active`), applied concretely in the e-mail adapter (W7.3).
- `hosts/README.md` — "Optional deterministic enforcement (hooks)" section: wiring existing validators to host hook points (advisory rules vs deterministic hooks, D3-degradable) (W7.4).
- Example demand `006-simulado-adocao-v2` (sq9-pilot) — offline end-to-end rehearsal of the 2.0.0 line: classify-risk proposal recorded in `004-risk.md`, priority-grouped requirements answered in-file, single decisions format, full app spec (new template sections), 2.0.0 stamps, HUB+App JSONL. Passes `validate-demand --strict` with 0 errors / 0 warnings in both runtimes; serves as a permanent regression eval.
- `validate-demand` (both runtimes) — optional `-AppRepoPath` / `-AppCurrentCommit` forwarded to the reverse-eng staleness check, so app-side strict validation can resolve the current commit (previously always warned `current_commit_unknown`).
- `validate-framework` (both runtimes) now runs the declared strict regression fixture (`006-simulado-adocao-v2`); `examples/README.md` and `docs/framework-validation.md` document maintained example tiers.
- `alfred-boot` (both runtimes, W8.4): open demands are ordered by resume priority (pending human checkpoint > in progress > blocked, then last activity) and a "Suggested next" hint with the reason is printed; the human still chooses.

### Compatibility notes
- Usage state has a new `alfred.usage.v2` schema. Existing state remains readable
  through compatibility fallbacks, but should be migrated with
  `migrate-state-v2.py --check` and a reviewed `--write`; a legacy limit of 100
  requires explicit `--unit acu|quota_percent`.
- Two framework rule files were renamed (`rules/demand-types/product.md`, `rules/demand-types/operational.md`) and one template was removed (`templates/hub/decision.md` — use `decisions.md`); consumers that deep-linked those paths must update.
- **All helper script paths moved** into category subfolders (`scripts/<runtime>/{validators,workflow,metrics,adapters}/<name>`). Callers/CI that invoked flat paths (e.g. `scripts/validate-framework.py`) must add the category segment (e.g. `scripts/validators/validate-framework.py`). Flags and behavior are unchanged.
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
- Python 3 helper set under `scripts/` mirroring every PowerShell helper, so the framework can be validated on machines without PowerShell (D3 portability).
- DEVIN CLI installer (`install/`) that clones the framework into `~/.alfred` and installs the `/alfred` skill; supports pinned versions via `-Version`/`ALFRED_VERSION` (D14/D15/D26).
- Per-type playbook convention (`rules/demand-types/playbooks/`) with a Migration playbook distilled from the real SQ9 migration (D5/3.6).
- Knowledge subsystem: richer policy template, `docs/knowledge-governance.md`, `docs/automation-fallback.md`, and a `validate-knowledge` helper (both runtimes) wired into framework validation (D42/D3).
- Branch promotion model and HUB vs App protection defined in `connectors/git.md` (D23, plan open item closed).
- External skill versioning policy (pinned default, opt-in track-latest) in `skills/skills.md` (plan 6.8 closed).

### Changed
- Helper scripts are now organized by runtime: `scripts/powershell/*.ps1` and `scripts/*.py`. Both runtimes accept the same flags and produce equivalent output.
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
