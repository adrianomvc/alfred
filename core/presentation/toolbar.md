# Toolbar

The toolbar is the top of every interaction's response, rendered by the
Orchestrator from `state`. It is never a separate source of truth.

**Day-to-day, load only `toolbar-quick.md`** (formats + marker rules). This file
is the full spec: layers, profiles, and rules — load it when a case is not
covered there or when changing the renderer.

`scripts/powershell/workflow/render-toolbar.ps1` (and the Python mirror) is an optional
helper that renders it from a `001-state.md`. Hosts that cannot run scripts
render it manually from the same fields.

## What comes in every response (4 layers)
1. **Toolbar** — the progress header from `state` (this file): sigla, demand id,
   lane, **model**, phase track, current step, next step, next checkpoint, **cost**.
2. **Body** — the active phase's work (analysis, proposal, generated artifact, result).
3. **Human interaction, when needed** — a **pointer** to the open question/decision
   in its artifact, never embedded as the source of truth (D18): `requirements`
   for Inception clarifications, `decisions` for design choices, a checkpoint
   approval recorded in `audit`. The person may answer in chat; Alfred then
   persists the answer into the artifact.
4. **Continuity footer** — next step, next checkpoint, and "recorded in state/audit".
   Model-change (D46) and escalation (D27) notices appear only when they occur.

By mode: **FAST** = one line, few/no questions; **Standard/SAFE** = the block plus
a clarification set / checkpoint.

## Text floor (borderless — owner-approved 2026-07-07)
No box: nothing to misalign, degrades anywhere. **FAST** is one line;
**Standard/SAFE** is four lines (see `toolbar-quick.md` for the exact shapes):

```text
ALFRED | SQ9 | #005-parallel-units | STANDARD
[############........] 60% | O que[x] -> Como[x] -> Fazer[>] -> Validar[ ] -> Operar[ ]
HITL: Tech Lead | model: GPT-5 | cost: n/a
Next: serializar resultado no state e validar evidencias
```

Progress bar = 20 chars of `#`/`.`; phase track uses the pt-BR aliases with
`[x]`/`[>]`/`[ ]` markers; Execution-first swaps the track for the emergency
sequence with posterior phases. A numeric cost (helper flag `-CostUsd`) adds
`est. total: ~US$ <linear forecast>` while 0 < progress < 100 — an estimate,
labeled `~`, omitted otherwise (never invent).

## Rich-cli (optional)
Same fields and line count, rendered with the fixed icon vocabulary
(🎩 header · 🔍 📐 🔨 ✅ 🚀 phases · 🟢🟡🔴 lane) + ANSI color per lane +
`▰▱` progress bar, in pt-BR (`Modo`, `⏸ HITL`, `→ Próximo`, `previsão total`).
FAST stays one line. Produced only by the helper (`--profile rich`) — the model
never hand-draws it.

## Web (optional)
Self-contained SVG card of the same `state` (helper `--profile web`), rendered
out-of-band by graphical hosts.

## Rules
- Show where the demand is, what remains, and the next human checkpoint.
- Use pt-BR when rendered to people.
- Surface a pending question/decision as a **pointer to its artifact**, not embedded
  as the source of truth (D18): e.g. `⏸ 1 decisão pendente → 003-requirements.md`.
- If the model changes, announce it and record an audit event (D46).
- If emergency Execution-first is active, mark Inception/Design as post-mortem pending.
- Optional tooling must never become the source of truth; `state` remains authoritative.
- Fixtures under `examples/toolbar-fixtures/` are the executable contract:
  `validate-toolbar-fixtures` fails on drift between the two runtimes and the fixtures.
- Visual richness follows `core/presentation/README.md`: `text` is the floor;
  `rich-cli` and `web` are optional, helper-rendered profiles over the same `state`
  (token economy — the model stays on the compact source).
