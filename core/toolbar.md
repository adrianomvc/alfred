# Process Toolbar (D9/D10/D46) — single source of truth

Rendered by the Orchestrator at the START of every interaction, from the `state`.
Interactions are pt-BR (D47). ASCII is the official form (D3); rich UI is optional.

## Required fields (always present)
- Identity: `SIGLA · <id-demanda> · "<title>"`
- **Mode** (lane) + **current model** (D46)
- Phase X/5 + **5-phase track**: ✓ done · ▶ current · ◻ pending · ⏸ waiting human · ⚠ risk
- Progress bar / %
- Units checklist (if decomposed — D24)
- **Cost line (ALWAYS — D10): `Custo: <tokens> · ~US$ <valor> · <interações>`**
- "Falta na fase" (DoD gap — D25)
- Next HITL checkpoint
- Next step

## Standard/SAFE example
```
ALFRED · SIGLA:PGTO · PGTO-142 "novo split de pagamento" · Standard · modelo: claude-opus-4-8
[✓ Inception] [✓ Design] [▶ Execution] [◻ Validate] [◻ Operation]   ██████░░░░ ~50%
Units: [◻ U1] [◻ U2] [◻ U3] [◻ U4]
Custo: 312k tokens · ~US$ 4,80 · 18 interações
Falta na fase: U1..U4 + PR  ·  Próximo checkpoint: revisão+merge (Tech Lead)
→ Próximo passo: iniciar U1
```

## FAST one-line (compact, still shows cost)
```
ALFRED · PGTO-143 · FAST · Execution (3/5) · falta: PR+merge · modelo: haiku · ~US$ 0,40
```

## Rules
- Cost and model are NEVER omitted (D10/D46). FAST uses the compact line.
- Model change between stages is announced here + audit event (D45).
- Emergency: track shows Execution ▶ with Inception/Design ⏳ post (D6).
