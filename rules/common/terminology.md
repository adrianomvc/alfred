# Common rule — terminology

Use the canonical terms from `core/glossary.md` consistently. This keeps artifacts, prompts, and the index aligned across the framework (English) and generated content (pt-BR).

## Rules
- **One name per concept** — `sigla`, `initiative`, `demand`, `unit`, `lane`, `stream`, `demand-type`. Do not introduce synonyms.
- **id-iniciativa** — always `iniciativa-<sequencia>-<iniciativa>` (example: `iniciativa-001-piloto`).
- **id-demanda** — always `<sequencia>-<nome-demanda>` (example: `001-implantacao-alfred`). The same id correlates HUB artifacts in `alfred-docs-hub` with app artifacts in `.alfred-docs-app/<id-iniciativa>/<id-demanda>/`.
- **Lanes** are the three modes: FAST / Standard / SAFE — never "level," "tier" (tier is the model-policy concept), or "profile."
- **Streams** are Produto / Operacional / Engineering; **demand-types** are the specific types within a stream.
- **Artifact roots** are canonical: HUB artifacts live under `alfred-docs-hub`; app artifacts live under `.alfred-docs-app`.
- **Artifact filenames** always use `<sequencia>-<nomeartefato>` with the extension required by the format.
- **Artifact phase folders** are canonical inside each demand folder. Keep only `001-state.md` (HUB) or `001-index.md` (App) at the demand root for boot/resume. Store the other artifacts by owner phase.
- **Canonical HUB artifact paths:** root `001-state.md`; `01-inception/002-problem.md`, `01-inception/003-requirements.md`, `01-inception/004-risk.md`, `01-inception/005-tech-inception.md`; `02-design/006-decisions.md`; `05-operation/007-audit.md`, `05-operation/008-metrics.md`, `05-operation/009-summary.md`, `05-operation/010-post-mortem.md`, `05-operation/011-observability-log.jsonl` when applicable.
- **Canonical App artifact paths:** root `001-index.md`; `01-inception/002-reverse-eng.md`, `01-inception/004-investigation.md`; `02-design/003-spec.md`; `04-validate/007-evidence.md`; `05-operation/005-audit.md`, `05-operation/006-metrics.md`, `05-operation/008-observability-log.jsonl`, `05-operation/009-hub-sync.md` when applicable.
- **Observability log** is the append-only JSONL event source for metrics: phase transitions, model, cost/tokens, validation results, defects, retries, blockers, changed files/artifacts, and closeout. `audit` records responsibility; `05-operation/011-observability-log.jsonl` records HUB measurement events.
- **Observability timing:** one line per relevant interaction/step/event, appended immediately. Do not accumulate in memory and write later.
- **App-only session** records local measurement events in `.alfred-docs-app/<id-iniciativa>/<id-demanda>/05-operation/008-observability-log.jsonl`. The HUB consolidates them into `alfred-docs-hub/<id-iniciativa>/<id-demanda>/05-operation/011-observability-log.jsonl` during sync.

## Language policy (D47)
- **Interactions with people → pt-BR:** prompts, questions (`[Answer]:`), toolbar, butler voice, checkpoints.
- **Framework files → English:** `core/`, `rules/`, `skills/`, `connectors/`, `metrics/`, templates.
- **User docs + generated artifacts → pt-BR:** everything the squad reads/produces in HUB/App.
- Templates **live in English** (framework labels), but Alfred **generates the artifact content in pt-BR**. Established technical terms may stay in English.
