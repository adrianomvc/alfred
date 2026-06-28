# Architecture — 3 layers / 3 repos

Alfred operates across three distinct repositories. **Compliance is not part of Alfred** — the `audit` exists for technical/operational traceability, not regulatory approval.

## The three layers
1. **Framework repo** — Alfred itself (principles, risk-mode, lifecycle, agents, skills, templates). **Single source, referenced by users (not copied into HUB/app).** Holds no initiative data.
2. **HUB repo (1 per sigla)** — each systemic *sigla* has its own HUB. Alfred artifacts live under `alfred-docs-hub`. Holds the *what/why*, decisions, and the `state`. **Source of truth for `state`.**
3. **Application repo** — app code + **technical artifacts for that repo** under `.alfred-docs-app` (reverse-engineering, technical spec, technical audit, repo metrics). A sigla may have **N apps**.

## Hierarchy (all within 1 sigla — no cross-sigla)
`Sigla (HUB) → Initiative → Demand`
- **Sigla** = a system; has 1 HUB and N apps.
- **Initiative** = one solution; **may be multi-repo** (span several apps of the sigla). A sigla has several initiatives. Its id follows `iniciativa-<sequencia>-<iniciativa>` (example: `iniciativa-001-piloto`).
- **Demand** = unit of work hanging off an initiative; may touch 1+ apps. It is where `state` and the Risk Mode classification live.

## Responsibility split (HUB + App)
- **HUB (of the sigla):** sigla + apps context under `alfred-docs-hub`; per initiative `001-initiative.md` (objective + repos involved); per demand root `001-state.md` (source of truth) plus phase folders for problem/scope, `risk`, `decisions`, `audit`, `metrics`, `summary`, and observability. At sigla level: `index`, active `skills`, `knowledge`, `metrics-rollup`.
- **App (per repo):** `.alfred-docs-app/<id-iniciativa>/<id-demanda>/` contains root `001-index.md` plus phase folders for `reverse-eng`, technical `spec`, technical `audit`, technical `metrics`, local observability events, evidence, PR link, and the HUB sync handoff when the HUB is not writable.
- **Correlation:** the `id-demanda` is shared between HUB and apps; the `state` links the technical artifacts in each app the demand touches.

## Write scope and HUB sync
- **HUB session:** if the current writable workspace is the HUB repo, Alfred writes HUB artifacts directly under `alfred-docs-hub/<id-iniciativa>/<id-demanda>/`.
- **App session with HUB available:** if the current workspace includes both app and HUB paths, Alfred writes app-local artifacts under `.alfred-docs-app/<id-iniciativa>/<id-demanda>/` and updates the HUB `state`/`audit`/`metrics` directly.
- **App-only session:** if only the app repo is writable, Alfred does not attempt to write the HUB. It writes only under `.alfred-docs-app/<id-iniciativa>/<id-demanda>/`, including `05-operation/008-observability-log.jsonl` and `05-operation/009-hub-sync.md`. The HUB remains the source of truth, but it is marked **pending sync** until a HUB session imports the app handoff.
- **No hidden cross-repo writes:** writing outside the detected repo requires an explicit mounted path, connector, or human-approved sync step.

## Demand artifact layout
Artifacts are grouped by lifecycle phase inside each demand folder. Keep only the boot/resume file at the demand root.

HUB:
- root: `001-state.md`
- `01-inception/`: problem, requirements, risk, technical inception
- `02-design/`: decisions
- `03-execution/`: execution notes when needed
- `04-validate/`: validation evidence when needed
- `05-operation/`: audit, metrics, summary, post-mortem, observability log

App:
- root: `001-index.md`
- `01-inception/`: reverse engineering and operational investigation
- `02-design/`: technical spec
- `03-execution/`: implementation notes when needed
- `04-validate/`: evidence
- `05-operation/`: technical audit, metrics, local observability log, HUB sync handoff

## Distribution & evolution (hard separation)
- The HUB holds **only artifacts**. **Nothing from the framework** is copied into HUB or app repos.
- The framework lives in **its own repo** (single source). HUB and app **consume/reference** it.
- Evolution/customization is **central and adopted by users**: when the framework evolves, users adopt that version — no divergent copies scattered across HUBs.
- Artifacts may record which framework version they were produced against (traceability); the active reference is always the framework repo. The *how to reference* mechanism (submodule, version pin, fetch) is an implementation detail, respecting the agnostic principle.

Version adoption is governed by `docs/version-adoption.md`: active demands freeze the stamped framework version unless a human explicitly approves an in-flight upgrade.

## SOLID applied to Alfred itself
- **S** — one reason to change per module (`core`/`rules`/`skills`/`connectors`/`metrics`) and per artifact; each agent owns 1 phase.
- **O** — extend by **adding** (skill, connector, demand-type, lane) without touching the core.
- **L** — family members are substitutable: lanes, connectors (cloudwatch↔datadog), hosts (DEVIN↔Claude↔Copilot). Consumers depend on the **role**, not the concrete.
- **I** — each consumer loads **only what it needs** = JIT / cascading index.
- **D** — high level depends on **abstraction**: `lifecycle` asks for "a lane"/"an observability connector," not a concrete; agents communicate through the `state` bus, not with each other.

Each pluggable family declares a **contract** in its registry (`connectors/connectors.md`, `skills/skills.md`, `rules/lanes/*`, `rules/agents/*`, `rules/demand-types/*`). Rules reference the contract/role, never the concrete — swapping CloudWatch for Datadog is swapping the connector, with no rule change.

## Layout
See the directory layout in the repo root and `core/README.md`. Two explicit axes: `demand-types` (path, per stream) × `lanes` (governance, per mode) — orthogonal; a demand combines one of each.
