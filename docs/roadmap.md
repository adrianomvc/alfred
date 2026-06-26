# Roadmap — Alfred para produção (pt-BR, D47)

Estado: **v0.1** — framework escrito e coerente; fluxos validados no papel (exemplos PGTO).
Falta o ciclo de validação real e as integrações de ambiente.

## 1. Validação real (sair do papel)
- [ ] Rodar 1 demanda real ponta a ponta num host (DEVIN e Claude CLI) — critério de aceite 8.3.
- [ ] Validar retomada por `state` após perda de contexto.
- [ ] Validar demanda que toca 2 apps (1 state linkando os dois).

## 2. Integrações de ambiente (connectors)
- [ ] Canal de email (D44): definir SMTP / Microsoft Graph / SES / MCP → preencher `connectors/notification-email.md`.
- [ ] Connector observability (CloudWatch) com acesso real à conta AWS (D34).
- [ ] Connector vcs (git): branch/PR; confirmar proteção de develop/main (D23).
- [ ] Connector tracker: formato real do `id-demanda` (Jira?) (D20).
- [ ] API de telemetria (futuro) → `connectors/telemetry-api.md` (D45).

## 3. Custo / observabilidade
- [ ] Captura automática de tokens/custo/modelo por etapa (depende do host) (D43/D45).
- [ ] Definir como o host expõe o modelo em uso (D46).

## 4. Customizações da empresa
- [ ] `core/model-policy.md`: preencher modelos reais por host (tabela de tiers).
- [ ] `knowledge/` (org): políticas reais (repo via ISSUE, acessos, naming...).
- [ ] `metrics/baselines.md`: calibrar com dados reais.
- [ ] `skills/lang-*`: padrões por linguagem usados pela squad.

## 5. Distribuição / governança
- [ ] Mecanismo de referência do framework (submodule / pin de versão / fetch) (D15/D26).
- [ ] Versão de skills externas: fixar commit vs. última (em aberto, 6.7).
- [ ] Política de adoção de novas versões (auto vs. pin por sigla) (D15/D16).

## 6. Decisões pequenas a confirmar
- [ ] Criação de demanda nova: como o boot obtém sigla/iniciativa (tracker? humano?).
- [ ] Estratégia exata de promoção de branch (demanda → develop → main).
