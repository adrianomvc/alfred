# Toolbar

The toolbar is the top of every interaction's response, rendered by the
Orchestrator from `state`. It is never a separate source of truth.

`scripts/powershell/render-toolbar.ps1` (and the Python mirror) is an optional
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

## FAST format
One line only:

```text
ALFRED | SIGLA:SQ9 | #001-implantacao-alfred | FAST | Execution (3/5) | model: <current> | cost: <compact> | left: PR + merge
```

## Standard/SAFE — text floor (portable, always available)
ASCII block; `+-|` borders, width-1 glyphs only — never breaks:

```text
+-- ALFRED ------------------------------- SIGLA:SQ9 | #001-implantacao-alfred --+
| Lane: STANDARD        Model: <current>       Progress: 45%     |
| Cost: 312k tokens | ~US$ 4.80 | 18 interactions                |
| 1 Inception [x] -> 2 Design [>] -> 3 Execution [ ] -> 4 Validate [ ] -> 5 Operation [ ] |
| Step : generating technical spec (app: sq9-app)                |
| HITL : spec approval - Tech Lead                               |
| Next : review routing alternatives                             |
+----------------------------------------------------------------+
```

## Standard/SAFE — rich-cli (optional)
Same fields, Unicode box + the phase icon vocabulary (🔍 Inception · 📐 Design ·
🔨 Execution · ✅ Validate · 🚀 Operation) + ANSI color per mode. Rendered to
people in pt-BR:

```text
┌─ 🎩 ALFRED ───────────────────────────────────────── SIGLA:PGTO · #142 ─┐
│ Modo: STANDARD       Modelo: strong        Progresso: ▰▰▰▰▰▱▱▱ 45%        │
│ Custo: 312k tokens · ~US$ 4,80 · 18 interações                           │
│ 🔍 Inception ✓ → 📐 Design ▶ → 🔨 Execution ◻ → ✅ Validate ◻ → 🚀 Operation ◻ │
│ Etapa   : gerando a spec técnica (app: pgto-api)                         │
│ ⏸ HITL   : aprovação da spec — Tech Lead                                 │
│ → Próximo: revisar alternativas de roteamento                            │
└──────────────────────────────────────────────────────────────────────────┘
```

## Rules
- Show where the demand is, what remains, and the next human checkpoint.
- Use pt-BR when rendered to people.
- Surface a pending question/decision as a **pointer to its artifact**, not embedded
  as the source of truth (D18): e.g. `⏸ 1 decisão pendente → 003-requirements.md`.
- If the model changes, announce it and record an audit event (D46).
- If emergency Execution-first is active, mark Inception/Design as post-mortem pending.
- Optional tooling must never become the source of truth; `state` remains authoritative.
- **Alignment (so the box never breaks):** the renderer computes display width
  treating emoji as 2 columns and pads to a fixed width, so the right border always
  closes; hand-written toolbars use the `+-|` floor.
- Visual richness follows `core/presentation/README.md`: `text` is the floor;
  `rich-cli` and `web` are optional, helper-rendered profiles over the same `state`
  (token economy — the model stays on the compact source).
```
