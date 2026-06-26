# Roadmap — Alfred para produção (pt-BR)

Estado: **v0.1** — framework escrito e coerente; fluxos validados no papel (exemplos PGTO).
Falta o ciclo de validação real e as integrações de ambiente.

## 1. Validação real (sair do papel)
- [ ] Rodar 1 demanda real ponta a ponta num host (DEVIN e Claude CLI).
- [ ] Validar retomada por `state` após perda de contexto.
- [ ] Validar demanda que toca 2 apps (1 state linkando os dois).

## 2. Integrações de ambiente (connectors)
- [ ] Canal de email : definir SMTP / Microsoft Graph / SES / MCP → preencher `connectors/notification-email.md`.
- [ ] Connector observability (CloudWatch) com acesso real à conta AWS .
- [ ] Connector vcs (git): branch/PR; confirmar proteção de develop/main .
- [ ] Connector tracker: formato real do `id-demanda` (Jira?) .
- [ ] API de telemetria (futuro) → `connectors/telemetry-api.md` .

## 3. Custo / observabilidade
- [ ] Captura automática de tokens/custo/modelo por etapa (depende do host) .
- [ ] Definir como o host expõe o modelo em uso .

## 4. Customizações da empresa
- [ ] `core/model-policy.md`: preencher modelos reais por host (tabela de tiers).
- [ ] `knowledge/` (org): políticas reais (repo via ISSUE, acessos, naming...).
- [ ] `metrics/baselines.md`: calibrar com dados reais.
- [ ] `skills/lang-*`: padrões por linguagem usados pela squad.

## 5. Distribuição / governança
- [ ] Mecanismo de referência do framework (submodule / pin de versão / fetch) .
- [ ] Versão de skills externas: fixar commit vs. última.
- [ ] Política de adoção de novas versões (auto vs. pin por sigla) .

## 6. Decisões pequenas a confirmar
- [ ] Criação de demanda nova: como o boot obtém sigla/iniciativa (tracker? humano?).
- [ ] Estratégia exata de promoção de branch (demanda → develop → main).
