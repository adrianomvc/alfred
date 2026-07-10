# Toolbar

The toolbar is the top of every interaction's response, rendered by the
Orchestrator from `state`. It is never a separate source of truth.

**Day-to-day, load only `toolbar-quick.md`** (formats + marker rules). This file
is the full spec: layers, profiles, and rules — load it when a case is not
covered there or when changing the renderer.

`scripts/python/workflow/render-toolbar.py` is an optional
helper that renders it from a `001-state.md`. Hosts that cannot run scripts
render it manually from the same fields.

## What comes in every response (4 layers)
1. **Toolbar** — the progress header from `state` (this file): sigla, demand id,
   lane, **model**, phase track, current step, next step, next checkpoint, **cost**.
2. **Body** — the active phase's work (analysis, proposal, generated artifact, result).
3. **Human interaction, when needed** — a **pointer** to the open question/decision
   in its artifact, never embedded as the source of truth (D18): `requirements`
   for Inception clarifications, `decisions` for design choices, a checkpoint
   approval recorded in `audit`. For requirements, the person edits the artifact
   and uses chat only to say `pronto`/`terminei`.
4. **Continuity footer** — next step, next checkpoint, and "recorded in state/audit".
   Model-change (D46) and escalation (D27) notices appear only when they occur.

By mode: **FAST** = compact block (or one line in text fallback), few/no
questions; **Standard/SAFE** = the block plus a clarification set / checkpoint.

## Preferred rich block
The normal human-facing toolbar is a compact Unicode block, visually aligned
with `welcome-screen.md`:

```text
╭─ 🎩 ALFRED · TST · #toolbar-standard ──────────────────────────────────────╮
│ Modo: 🟡 STANDARD   Progresso: 40%  ▰▰▰▰▱▱▱▱▱▱   Custo: US$ 1.20           │
│ Previsão: ~US$ 3.00                                                        │
│ Framework: v2.0.0 (a289a26)        App: f9a3739                            │
├────────────────────────────────────────────────────────────────────────────┤
│ 1 Inception ✅ · 2 Design ✅ · 3 Execution ▶ · 4 Validate ○ · 5 Operation ○ │
│ HITL: Tech Lead       Modelo: claude-opus-4-8                              │
│ Próximo: finish implementation unit and update evidence                    │
╰────────────────────────────────────────────────────────────────────────────╯
```

Progress = completed phases / 5. The phase track uses numbered canonical phase
names with `✅` / `▶` / `○` statuses; Execution-first swaps the track for the
emergency sequence with posterior phases. Cost is prominent top-block
information: show the compact cost when collected, otherwise show
`custo: nao coletado` and, when available, the `usage-cost` state note. A
numeric cost (helper flag `-CostUsd`) adds `est. total: ~US$ <linear forecast>`
while 0 < progress < 100 — an estimate, labeled `~`, omitted otherwise (never
invent). Traceability appears in the same block: `Framework: v<version>
(<commit>)` and `App: <commit>`.

## Text floor (fallback)
No Unicode dependency; degrades anywhere. **FAST** is one line;
**Standard/SAFE** is four lines (see `toolbar-quick.md` for exact shapes). The
text fallback uses `ok` / `agora` / `pendente` instead of the rich markers.

## Rich renderer
Produced by the helper (`--profile rich`, default). The model should not
hand-draw the block when the helper is available; it should render from `state`.
If the host cannot render Unicode boxes or icons, fall back to `--profile text`.

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
- Visual richness follows `core/presentation/README.md`: `rich` is preferred;
  `text` and `web` are alternate helper-rendered profiles over the same `state`
  (token economy — the model stays on the compact source).
