# Spec técnica — PGTO-160 @ pgto-api (SAFE)
- Solução: upgrade Spring Boot 2 -> 3 (javax -> jakarta).
- Alternativas: big-bang (descartado: risco) | faseado/strangler (escolhido, D1).
- Critérios de aceite: build OK; 100% regressão; sem mudança de contrato de API.
- Dependências: libs transitivas (mapear incompatíveis).
- Plano de execução (units): U1 deps javax->jakarta · U2 config/propriedades · U3 testes de regressão.
- Rollout: por release, feature-flag de fallback.
- Rollback: reverter release + flag; sem migração de dados (reversível).
