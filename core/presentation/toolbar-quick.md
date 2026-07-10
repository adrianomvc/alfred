# Toolbar — quick reference (load this, not the full spec)

Emit the toolbar at the top of every response, from the demand `state` fields
(sigla, id, lane, phase checklist, checkpoint, current step, next step, model,
cost). Borderless text is the floor — nothing to misalign. Full spec (layers,
profiles, rules):
`core/presentation/toolbar.md` — load it only when a case is not covered here.

## FAST — one line
```text
ALFRED | TST | #toolbar-fast | FAST | Execution | 80% | custo: <compact> | modelo: <current> | proximo: <short>
```

## Standard/SAFE — four lines
```text
ALFRED | TST | #toolbar-standard | STANDARD | 60% | custo: <compact>
Fases: O que:ok | Como:ok | Fazer:agora | Validar:pendente | Operar:pendente
HITL: Tech Lead | modelo: <current> | etapa: <current step>
Proximo: <next step from state>
```

- Progress = completed phases / 5; phase statuses: `ok` done · `agora` current · `pendente` not done.
- Phase aliases (pt-BR): O que · Como · Fazer · Validar · Operar.
- Execution-first (emergency): track becomes `Execution-first stabilization -> Inception posterior -> Design posterior -> Validate posterior -> Operation / post-mortem`.
- Cost is shown in the first line. If no host usage source exists, write
  `custo: nao coletado` (or include the `usage-cost` state note); never hide it.
- With a numeric cost and 0<progress<100, append `| est. total: ~US$ <linear>` (estimate, never a fact).
- Helper (optional): `render-toolbar` in `scripts/python/workflow/`.
