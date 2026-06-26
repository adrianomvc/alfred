# Inception técnica — PGTO-160 (D33) [Engineering: lente técnica forte]
- Sistemas/apps afetados: pgto-api (todas as camadas que usam javax).
- Reverse-eng: Java/Spring; commit a1b2c3d (D21) — confirmar atualidade.
- Restrições: migração javax -> jakarta; libs transitivas.
- Riscos técnicos: breaking changes amplos; comportamento de serialização.
- Inception curta (problema técnico claro); sem Inception de negócio.
