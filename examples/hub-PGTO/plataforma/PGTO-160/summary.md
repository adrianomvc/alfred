# Summary — PGTO-160 (fechamento, D11)
- Feito: upgrade Spring Boot 2 -> 3 (javax->jakarta) no pgto-api, faseado.
- Decisões-chave: D1 (migração faseada/strangler + rollback por release).
- Skills usadas: coding-standard, lang-java.
- Resultado: 100% regressão; sem mudança de contrato; rollout sem incidentes.
- Débitos/próximas melhorias: revisar libs depreciadas remanescentes.
- Post-mortem: n/a.
