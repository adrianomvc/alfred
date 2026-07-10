# Toolbar — quick reference (load this, not the full spec)

Emit the toolbar at the top of every response, from the demand `state` fields
(sigla, id, lane, phase checklist, checkpoint, current step, next step, model,
cost). Prefer the rich Unicode block, visually aligned with `welcome-screen.md`;
use the borderless text floor only when the host cannot render Unicode. Full
spec (layers, profiles, rules):
`core/presentation/toolbar.md` — load it only when a case is not covered here.

## Preferred rich block
```text
╭─ 🎩 ALFRED · TST · #toolbar-standard ──────────────────────────────────────╮
│ Modo: 🟡 STANDARD   Progresso: 40%  ▰▰▰▰▱▱▱▱▱▱   Custo: US$ 1.20           │
│ Previsão: ~US$ 3.00                                                        │
├────────────────────────────────────────────────────────────────────────────┤
│ O quê ✅ · Como ✅ · Fazer ▶ · Validar ○ · Operar ○                        │
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
Fases: O que:ok | Como:ok | Fazer:agora | Validar:pendente | Operar:pendente
HITL: Tech Lead | modelo: <current> | etapa: <current step>
Proximo: <next step from state>
```

- Progress = completed phases / 5; rich markers: `✅` done · `▶` current · `○` pending. Text fallback statuses: `ok` · `agora` · `pendente`.
- Phase aliases (pt-BR): O que · Como · Fazer · Validar · Operar.
- Execution-first (emergency): track becomes `Execution-first stabilization -> Inception posterior -> Design posterior -> Validate posterior -> Operation / post-mortem`.
- Cost is shown prominently in the top block. If no host usage source exists, write
  `custo: nao coletado` (or include the `usage-cost` state note); never hide it.
- With a numeric cost and 0<progress<100, append `| est. total: ~US$ <linear>` (estimate, never a fact).
- Helper (optional): `render-toolbar` in `scripts/python/workflow/`.
