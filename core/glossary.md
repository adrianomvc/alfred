# Glossary

Terminology of the framework. Keeps the EN↔pt-BR mapping consistent across framework files (English) and generated artifacts (pt-BR).

| EN (framework) | pt-BR (artifacts/people) | Meaning |
|---|---|---|
| sigla | sigla | A systemic system identifier; has 1 HUB and N apps. |
| initiative | iniciativa | One solution; may be multi-repo. A sigla has several. Its id follows `iniciativa-<sequencia>-<iniciativa>`. |
| demand | demanda | Unit of work hanging off an initiative; holds `state` + Risk Mode. |
| unit (of work) | unit / unidade de trabalho | Checklist item inside a demand's execution plan (no own state). |
| lane | lane / modo | A Risk Mode governance mode: FAST / Standard / SAFE. |
| stream | stream | A demand family: Produto / Operacional / Engineering. |
| demand-type | tipo de demanda | Specific type within a stream (bug, refactor, migration…). |
| HUB | HUB | The sigla's repo; source of truth for `state`. |
| app | app / aplicação | An application repo of the sigla. |
| Risk Mode | Risk Mode | The governance selector (risk × complexity → lane). |
| Process Toolbar | toolbar / barra de progresso | ASCII progress header shown each interaction. |
| reverse-eng | engenharia reversa | Deep brownfield understanding before acting. |
| spec | spec | SDD artifact: problem, solution, acceptance criteria. |
| state | state | Live source of truth: phase, mode, progress, next step. |
| decisions | decisions / decisões | Why something was decided (Standard/SAFE). |
| audit | audit | Responsibility trail (all modes; lean→complete). |
| metrics | metrics / métricas | Agent and delivery measurement. |
| observability log | log de observabilidade | Append-only JSONL event log used to compute demand metrics. |
| summary | summary / resumo | Closing summarization of the demand. |
| index | index / índice | Context Index: theme → location (basis of JIT). |
| skill | skill | Pluggable capability/knowledge (opt-in, JIT). |
| connector | connector | Access to an external system (optional). |
| knowledge | knowledge / base de conhecimento | Always-in-force policies/guardrails (≠ skill). |
| HITL | HITL | Human-in-the-loop checkpoint. |
| JIT | JIT | Just-in-time context loading. |
| DoD | DoD | Definition of Done per phase × mode. |
| Execution-first | Execution-first | Emergency flow: stabilize first, record after (post-mortem). |
| host | host | The agent runtime that runs Alfred (DEVIN, Claude CLI, Copilot). |

## Streams (demand taxonomy)
- **Produto** — new feature · functional improvement · new journey · UX improvement · experiment · business-rule change · product evolution.
- **Operacional** — bug · incident · hotfix · alert · production failure · pipeline error · degradation · emergency rollback · support.
- **Engineering** — refactor · tech debt · upgrade · migration · observability · performance · security · FinOps · internal automation · architecture · provider change.

## id-demanda
Inherited from the existing tracker when available, but the Alfred artifact id does not include the sigla: `<sequencia>-<nome-demanda>` (e.g. `001-implantacao-alfred`). No tracker -> use the next sequence in the initiative. The same id correlates the HUB folder in `alfred-docs-hub` with the app folder in `.alfred-docs-app/<id-iniciativa>/<id-demanda>/`.

## id-iniciativa
Initiatives always use `iniciativa-<sequencia>-<iniciativa>` (e.g. `iniciativa-001-piloto`). The sequence is numeric; the final segment is a short lowercase slug for the solution/iniciativa.

## artifact filenames
Generated artifacts use `<sequencia>-<nomeartefato>` with the extension required by the format, for example `001-state.md`, `007-audit.md`, `009-summary.md`, and `011-observability-log.jsonl`. The sequence keeps reading order stable across hosts and plain file explorers.

## artifact phase folders
Inside each demand folder, keep the resume artifact at the root and place the remaining artifacts under the phase that owns them.

HUB demand layout:
- root: `001-state.md`
- `01-inception/`: `002-problem.md`, `003-requirements.md`, `004-risk.md`, `005-tech-inception.md`
- `02-design/`: `006-decisions.md`
- `03-execution/`: execution plans or generated work notes when needed
- `04-validate/`: validation evidence when needed
- `05-operation/`: `007-audit.md`, `008-metrics.md`, `009-summary.md`, `010-post-mortem.md`, `011-observability-log.jsonl`

App demand layout:
- root: `001-index.md`
- `01-inception/`: `002-reverse-eng.md`, `004-investigation.md` when the demand is operational
- `02-design/`: `003-spec.md`
- `03-execution/`: implementation notes when needed
- `04-validate/`: `007-evidence.md`
- `05-operation/`: `005-audit.md`, `006-metrics.md`, `008-observability-log.jsonl`, `009-hub-sync.md`

## observability log vs audit
`05-operation/007-audit.md` records responsibility and traceability. In the HUB, `05-operation/011-observability-log.jsonl` records structured events used to calculate `05-operation/008-metrics.md`. In an App-only session, `.alfred-docs-app/<id-iniciativa>/<id-demanda>/05-operation/008-observability-log.jsonl` records local events until they are synchronized into the HUB.
