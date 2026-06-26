# Spec técnica — PGTO-142 @ pgto-api (Standard) — APROVADA (João-TechLead, 2026-06-25)
- Solução: novo endpoint POST /payments/{id}/split (percentual e/ou valor).
- Critérios de aceite: soma das partes = total; idempotente; arredondamento determinístico (banker's rounding); 100% regressão de pagamento OK.
- Dependências: ledger de conciliação.
- Pontos de mudança: src/payments/split/*
- Plano de teste: unit (soma/arredondamento/idempotência) + regressão.

## Plano de execução (Planning — D19/D24) — units
- [x] U1: modelo/validação do split (soma = total)
- [x] U2: endpoint POST /payments/{id}/split (idempotente)
- [x] U3: arredondamento determinístico + testes unit
- [x] U4: evento p/ ledger + teste de regressão
- PR: #318 (alfred/PGTO-142 -> develop) — revisado e MERGED por João-TechLead
