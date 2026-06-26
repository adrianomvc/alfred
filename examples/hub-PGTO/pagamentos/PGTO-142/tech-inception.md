# Inception técnica — PGTO-142 (D33)
- Sistemas/apps afetados: pgto-api (endpoint de split); possível evento p/ pgto-worker.
- Integrações: ledger de conciliação.
- Restrições técnicas: idempotência; arredondamento determinístico.
- Riscos técnicos: divergência de centavos na conciliação.
- Perguntas técnicas: split por percentual e/ou valor fixo? -> respondido (ambos).
