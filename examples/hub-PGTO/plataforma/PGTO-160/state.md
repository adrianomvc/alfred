# PGTO-160 — upgrade Spring Boot 2 -> 3 (pgto-api)   (sigla PGTO · iniciativa plataforma)
- Alfred/framework: v0.1 · branch: alfred/PGTO-160   (D26/D23)
- Stream/Tipo: Engineering / upgrade
- Risk Mode: SAFE (override duro: breaking changes + muitos dependentes) · modelo atual: claude-opus-4-8
- Fase atual: Design
- Status: aguardando checkpoint
- Responsável humano: João-TechLead (arquitetura) · Ana-PM (custo/prazo)
- Próximo passo: aprovar arquitetura + plano de rollout/rollback
- Pendências: validar libs incompatíveis (javax->jakarta)
- Riscos ativos: breaking changes (alto); regressão ampla
- Apps tocadas: pgto-api -> ../../../app-pgto-api/.alfred/PGTO-160/
- Links HUB: tech-inception | risk | decisions | audit
- Última atividade: 2026-06-25 por agente:spec-design

## Progresso (D9)
- [x] Inception     problema técnico claro; SAFE (override breaking)
- [ ] Design        falta: aprovar arquitetura + rollout/rollback (Tech Lead)
- [ ] Execution     units: [ ] U1 deps javax->jakarta · [ ] U2 config · [ ] U3 testes regressão
- [ ] Validate
- [ ] Operation
- Etapa interna atual: Design -> alternativas + plano de rollback
- Próximo checkpoint HITL: aprovação de arquitetura (João-TechLead)
