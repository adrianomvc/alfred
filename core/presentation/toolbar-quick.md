# Toolbar — quick reference (load this, not the full spec)

Emit the toolbar at the top of every response, from the demand `state` fields
(sigla, id, lane, phase checklist, checkpoint, current step, next step, model,
cost). Prefer the rich Unicode block, visually aligned with `welcome-screen.md`;
use the borderless text floor only when the host cannot render Unicode. Full
spec (layers, profiles, rules):
`core/presentation/toolbar.md` — load it only when a case is not covered here.

## Rendering procedure
1. Prefer the helper: `python scripts/python/workflow/render-toolbar.py -StatePath <demand>/001-state.md -Profile rich`.
2. If the helper cannot run, use this file as the loaded source and emit the
   documented text fallback from `state`.
3. Never hand-draw the rich block from memory or paste an older toolbar shape.

## Preferred rich block
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

## Text fallback — FAST one line
```text
ALFRED | TST | #toolbar-fast | FAST | Execution | 80% | custo: <compact> | modelo: <current> | proximo: <short>
```

## Text fallback — Standard/SAFE four lines
```text
ALFRED | TST | #toolbar-standard | STANDARD | 60% | custo: <compact>
Framework: v2.0.0 (<commit>) | App: <app-commit>
Fases: 1 Inception:ok | 2 Design:ok | 3 Execution:agora | 4 Validate:pendente | 5 Operation:pendente
HITL: Tech Lead | modelo: <current> | etapa: <current step>
Proximo: <next step from state>
```

- Progress = completed phases / 5; rich markers: `✅` done · `▶` current · `○` pending. Text fallback statuses: `ok` · `agora` · `pendente`.
- Phase labels stay numbered and canonical: `1 Inception` · `2 Design` · `3 Execution` · `4 Validate` · `5 Operation`.
- Execution-first (emergency): track becomes `Execution-first stabilization -> Inception posterior -> Design posterior -> Validate posterior -> Operation / post-mortem`.
- Cost is shown prominently in the top block. If no host usage source exists, write
  `custo: nao coletado` (or include the `usage-cost` state note); never hide it.
- If `state` has `cost usd:` from an approved export, `ccusage`, or a
  host-native cost command such as Claude Code `/cost`, render that value.
- With a numeric cost and 0<progress<100, append `| est. total: ~US$ <linear>` (estimate, never a fact).
- Show traceability next to cost: `Framework: v<version> (<commit>)` and
  `App: <commit>`. Prefer stamped state fields; otherwise the helper may read
  the current framework clone and app artifacts.
- Helper (optional but preferred whenever available): `render-toolbar` in `scripts/python/workflow/`.
