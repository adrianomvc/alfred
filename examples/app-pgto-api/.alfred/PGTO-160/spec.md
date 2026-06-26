# Spec técnica — PGTO-160 @ pgto-api (SAFE) — ARQUITETURA APROVADA (João-TechLead)
- Solução: upgrade Spring Boot 2 -> 3 (javax -> jakarta), faseado (strangler).
- Critérios de aceite: build OK; 100% regressão; sem mudança de contrato de API.
- Plano de execução (units):
  - [x] U1: deps javax -> jakarta (PR #320)
  - [x] U2: config/propriedades Boot 3 (PR #321)
  - [x] U3: testes de regressão + ajustes (PR #322)
- Rollout: por release com feature-flag de fallback — concluído sem incidentes.
- Rollback: reverter release + flag (não usado).
