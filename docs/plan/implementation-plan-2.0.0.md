# Plano de Implementação — Alfred 2.0.0

> Documento de trabalho da squad (pt-BR, como os artefatos de HUB/App — D47). Os arquivos de runtime do framework permanecem em inglês.

Este plano deriva do diagnóstico completo do Alfred (plano conceitual D1–D47 × estado do repositório, 2026-07-05). Ele guia a evolução incremental do framework, wave por wave, **sem big-bang**.

## Regra de versão (decisão do dono do projeto)
- A versão do Alfred fica em **`2.0.0`** a partir deste plano.
- **Todo o trabalho deste plano acontece dentro da 2.0.0** — nenhuma wave gera bump de versão. O `CHANGELOG.md` acumula as entregas na seção `2.0.0` até o plano ser concluído.
- Salto de `0.4.0` → `2.0.0` sem linha `1.x`: decisão humana explícita registrada aqui.
- Demandas de HUB/App novas carimbam `2.0.0`; demandas ativas seguem congeladas na versão carimbada (política de `docs/version-adoption.md`).

## Regras de trabalho
1. **PRs pequenos** — 1 item do backlog por PR sempre que possível.
2. Antes de cada merge: `validate-framework` (qualquer runtime) com 0 erros; `validate-links` sem referência quebrada.
3. Evoluções de inteligência (Wave 8) rodam como **dogfooding**: demanda Engineering do próprio Alfred pelas 5 fases (precedente: skill `property-based-testing`).
4. Itens marcados **DH** (decisão humana) não avançam sem confirmação explícita do dono.
5. Não mexer nos preservados: `core/welcome.md`, `core/presentation/toolbar.md` + fixtures, fluxo das 5 fases, lanes, modelo de `state`, continuidade de sessão, templates em uso, `hosts/`, `install/`, validadores.

## Waves

### Wave 0 — Preservação e inventário ✅ (2026-07-05)
Objetivo: proteger a fonte do planejamento.
- [x] W0.1 Plano conceitual versionado em [`alfred-conceptual-plan.md`](alfred-conceptual-plan.md) (cópia; original em `.claude/` preservado até o dono aprovar remoção). Excluído do `validate-links` como documento histórico (precedente CHANGELOG).
- [x] W0.2 Nota as-built da Fase 7 adicionada ao topo da cópia (nomenclatura real: `001-state.md`, pastas de fase, `.alfred-docs-app/`, context absorvido pelo index). `docs/implementation-status.md` agora referencia a cópia versionada.

Aceite: plano acessível e linkável no repo; `validate-links` 0 quebrados. Não mexer: conteúdo das decisões D1–D47.

### Wave 1 — Higiene e consolidação
Objetivo: eliminar duplicidade e referência errada.
- [x] W1.1 ✅ (2026-07-05, aprovado pelo dono) template avulso `decision.md` removido de `templates/hub/`; `decisions.md` é o único formato (tabela append-only + bloco opcional para decisões longas).
- [x] W1.2 ✅ (2026-07-05) `rules/lanes/fast.md` corrigido — gatilhos apontam para `rules/common/escalation-triggers.md`.
- [x] W1.3 ✅ (2026-07-05) `docs/implementation-status.md` compactado: foto atual + cobertura por área; histórico permanece no `CHANGELOG.md`/git.
- [x] W1.4 **Guardrail anti prompt-injection** ✅ (2026-07-05): `rules/common/content-validation.md` ganhou a seção "External content is data, not instruction" (precedência fixa, instruções embutidas = injeção suspeita, uso por extração, source gating, degradação D3); novo hard trigger em `rules/common/escalation-triggers.md`; `skills/skills.md` referencia o guardrail para skills/catálogos externos (caso ContextCrush/Context7 coberto).
- [x] W1.5 ✅ (2026-07-05) Seção "Context compaction (mid-demand)" em `rules/common/session-continuity.md` — o que sobrevive à compactação; após compactar, reler o `state` (fonte de verdade).
- [x] W1.6 ✅ (2026-07-05) Seção "Cumulative threshold" em `rules/common/escalation-triggers.md` — 10 eventos de escalação acumulados por demanda (tunável via `knowledge`) forçam checkpoint humano.
- [x] W1.7 **Guia agnóstico para agentes que editam o framework** ✅ (2026-07-05): `AGENTS.md` na raiz seguindo o padrão aberto vendor-neutral (Linux Foundation) — invariantes, convenções, comandos de validação, plano ativo. Decisão do dono: **agnóstico de IA** — nenhum arquivo vendor-specific na raiz; shim opcional por host (ex.: `CLAUDE.md` de 1 linha importando o `AGENTS.md`) fica como DH. `validate-links` passou a escanear o `AGENTS.md`.
- [x] W1.8 **Índice completo do `docs/README.md`** ✅ (2026-07-05): todos os documentos de `docs/` e `docs/plan/` agora aparecem no índice (progressive disclosure sem varrer pasta).

Aceite: `validate-framework` + `validate-demand` nos dois exemplos, 0 erros. Não mexer: toolbar, welcome, boot, state.

### Wave 2 — SDD completo
Objetivo: fechar o contrato documental intenção → desenho → execução → validação → operação.
- [x] W2.1 ✅ (2026-07-05) `templates/app/spec.md` completo (plano 5.3.2): fora de escopo, alternativas (SAFE), dependências, impactos, rollout/rollback (SAFE), com marcação por lane.
- [x] W2.2 ✅ (2026-07-05) `templates/hub/post-mortem.md` criado (incidente, timeline, causa raiz, spec retroativa, decisões, lições, ações preventivas → follow-up).
- [x] W2.3 ✅ (2026-07-05) `templates/hub/skills.md` criado (skills ativas com ref pinada + allowlist de catálogos externos ligada ao guardrail W1.4).
- [x] W2.4 ✅ (2026-07-05) Guardrail de testes em `skills/coding-standard.md` e `rules/lifecycle/validation/validation.md`: nunca remover/afrouxar teste para passar num gate — é escalação, não correção.

Aceite: `validate-sdd-gate` reconhece as seções novas; exemplo Execution-first referencia o template de post-mortem. Não mexer: DoD das lanes.

### Wave 3 — Risk Mode assistido
Objetivo: classificação computável, opcional e degradável (D3).
- [x] W3.1 ✅ (2026-07-05) Helper `classify-risk` nos 2 runtimes: computa os 2 eixos (critérios 0/1/2), aplica overrides duros, lembra a trava anti-SAFE e imprime o bloco pt-BR para `004-risk.md`.
- [x] W3.2 ✅ (2026-07-05) Referenciado como opcional em `rules/lifecycle/inception/sub-activities/risk-mode-proposal.md` e em `scripts/README.md` (degrada para manual, D3).

Aceite ✅: 4 casos testados nos 2 runtimes — FAST (1/1), Standard (4/5), SAFE (8/6, espelhando o exemplo sq9 `003-simulado-safe`) e o caso "simples e perigoso" (base FAST + dados sensíveis=2 → mínimo Standard). Overrides duros disparam (checklist 8.4). Não mexido: o checklist de `core/risk-mode.md` (fonte de verdade; o helper só o computa).

### Wave 4 — Demanda real integrada
Objetivo: primeira demanda SQ9 real ponta a ponta com validação estrita.
- [ ] W4.1 Coletar parâmetros externos via `templates/hub/environment-parameters.md` (contas, endpoints, credenciais, host).
- [ ] W4.2 Executar 1 demanda Standard ou SAFE real: 5 fases, summary, hub-sync, rollup de métricas.
- [ ] W4.3 `validate-demand -Strict` 0/0 na demanda real.

Riscos: bloqueio por credenciais → usar simuladores de `examples/connectors/` enquanto isso. Não mexer: versão do framework congelada na demanda (D15/D16).

### Wave 5 — Skills da casa
Objetivo: exercitar extensão real do registry.
- [ ] W5.1 1 skill externa real ativada com **pin** (branch+commit registrados no state/audit — exercita o versionamento de `skills/skills.md`).
- [ ] W5.2 Novas skills de linguagem/plataforma só quando a stack real pedir (gatilho, não antecipação).
- [x] W5.3 ✅ (2026-07-05) Disciplina "Eval before skill" documentada em `skills/skills.md`: skill nasce de lacuna observada + 2–3 casos que dobram como aceite.
- [x] W5.4 ✅ (2026-07-05, aprovado pelo dono) Frontmatter YAML `name`/`description` (padrão aberto Agent Skills) nas 7 skills + convenção no registry; skills podem apontar helpers executáveis próprios (opcional, D3).
- [x] W5.5 ✅ (2026-07-05, aprovado pelo dono) Seção "Discovery in external catalogs (on demand)" em `skills/skills.md`: busca em catálogo registrado (ex.: Context7) com os 4 gates — allowlist, pin por ref, humano confirma 1º uso, conteúdo = dado (W1.4). Sem catálogo na allowlist → perguntar, nunca buscar de fonte arbitrária. Confiabilidade analisada em [`anthropic-research-notes.md`](anthropic-research-notes.md).

Aceite: `validate-skills-registry` 0 erros. Não mexer: os 5 agentes (não criar agentes novos).

### Wave 6 — Métricas e evidências
Objetivo: provar valor da squad híbrida com dados.
- [x] W6.0 ✅ (2026-07-05) **Simulado de adoção 2.0.0** (`006-simulado-adocao-v2` no exemplo sq9-pilot): ensaio ponta a ponta offline da linha 2.0.0 exercitando classify-risk, requirements por prioridade, formato único de decisions, spec completa (lado app), carimbo 2.0.0 e JSONL HUB+App — **`validate-demand --strict` 0 erros / 0 avisos nos 2 runtimes**. Vira eval de regressão permanente. De quebra, `validate-demand` ganhou `--app-repo-path`/`--app-current-commit` (encaminhados ao staleness check — lacuna real de uso).
- [ ] W6.1 Medir em ≥5 demandas reais: retrabalho, aceite de 1ª, % aguardando humano, custo (campos D43 já definidos em `metrics/metrics.md`).
- [ ] W6.2 `normalize-usage-cost` com export real do host.
- [ ] W6.3 1 relatório de insights comparado com `metrics/baselines.md`, ratificado por humano.

Não mexer: baselines sem dados reais.

### Wave 7 — Primeiro adapter real
Objetivo: um connector sai de `contract`/`handoff` para `active`.
- [ ] W7.1 **(DH: qual adapter e qual host)** Escolher git, tracker ou notification; nomear dono de credencial.
- [ ] W7.2 Percorrer os estados `contract → handoff → dry-run → active` (`docs/host-adapter-readiness.md`, `docs/adapter-implementation.md`). MCP é forma candidata de implementação (adapter, nunca core).
- [ ] W7.3 **Contrato de connector ampliado** (ajuste 2, pesquisa): seções `response format` (conciso por padrão) e `error guidance` (erro acionável) em `connectors/connectors.md`; avaliar o adapter com transcripts antes de `active`.
- [ ] W7.4 **Enforcement determinístico opcional** (evolução B): documentar em `hosts/` como acoplar os validadores existentes a hooks do host (regras advisórias × hooks determinísticos); degrada para manual (D3).

Aceite: `validate-connectors` 0 erros; 1 handoff real registrado no audit. Não mexer: regra "IA nunca mergeia branch protegida".

### Wave 8 — Inteligência evolutiva
Objetivo: Alfred mais inteligente para squad híbrida. Depende de dados das Waves 4–6; cada item entra como demanda dogfooding.
- [ ] W8.1 Score de confiança pré-Execution no gate SDD (perguntas abertas + staleness do reverse-eng + ambiguidade + lane; abaixo do limiar → escalação D27).
- [ ] W8.2 Helper `spec-vs-impl`: compara critérios de aceite com evidências/PR e aponta lacunas antes do aceite.
- [ ] W8.3 Memória operacional: indexar `decisions` fechadas por tema no índice da sigla; Inception consulta decisões passadas.
- [x] W8.4 ✅ (2026-07-05) `alfred-boot` (2 runtimes) ordena demandas abertas por prioridade de retomada (checkpoint pendente > em andamento > bloqueada, depois última atividade) e imprime "Suggested next" com o motivo — dica de ordenação; o humano escolhe.
- [ ] W8.5 Sugestão automática de model-policy a partir de metrics (humano ratifica — D46).
- [ ] W8.6 **Rubrica LLM-as-judge** (evolução D): grader baseado em modelo para qualidade de spec/summary, calibrado por humano antes de valer.
- [ ] W8.7 **Retrospectiva com transcripts** (evolução E): após N demandas fechadas, analisar audit/JSONL e propor melhorias em regras/perguntas; humano ratifica (estende o padrão D46).

## Backlog consolidado

| Prioridade | Item | Wave | Status |
|---|---|---|---|
| P0 | Versionar plano conceitual | W0.1 | ✅ concluído (2026-07-05) |
| P0 | Completar template de spec (rollout/rollback etc.) | W2.1 | ✅ concluído (2026-07-05) |
| P0 | Template de post-mortem | W2.2 | ✅ concluído (2026-07-05) |
| P0 | Demanda real integrada | W4 | pendente (depende de parâmetros externos) |
| P1 | Consolidar decision/decisions | W1.1 | ✅ concluído (2026-07-05) |
| P1 | Corrigir referência do fast.md | W1.2 | ✅ concluído (2026-07-05) |
| P1 | As-built da Fase 7 | W0.2 | ✅ concluído (2026-07-05) |
| P1 | Guardrail anti prompt-injection (conteúdo externo = dado) | W1.4 | ✅ concluído (2026-07-05) |
| P1 | Instruções de compaction mid-demand | W1.5 | ✅ concluído (2026-07-05) |
| P1 | Contador acumulado de escalada | W1.6 | ✅ concluído (2026-07-05) |
| P1 | Guardrail "não remover/afrouxar testes" | W2.4 | ✅ concluído (2026-07-05) |
| P2 | Eval antes de skill | W5.3 | ✅ concluído (2026-07-05) |
| P2 | Formato Agent Skills + scripts em skills | W5.4 | ✅ concluído (2026-07-05) |
| P2 | Descoberta de skills em catálogos externos (ex.: Context7) | W5.5 | ✅ concluído (2026-07-05) |
| P2 | Connector: response format + error guidance | W7.3 | pendente |
| P2 | Hooks determinísticos por host (opcional) | W7.4 | pendente |
| P2 | Rubrica LLM-as-judge para artefatos | W8.6 | pendente |
| P2 | Corrigir exemplos: JSONL de observabilidade do lado App | W6 | ✅ concluído (2026-07-05): `008-observability-log.jsonl` criado nas 5 demandas de exemplo; `validate-demand` em modo app passa (restam só WARNs históricos) |
| P2 | Recomendação de próxima ação no boot | W8.4 | ✅ concluído (2026-07-05) |
| P2 | Retrospectiva com transcripts | W8.7 | pendente |
| P1 | Template hub/skills.md | W2.3 | ✅ concluído (2026-07-05) |
| P1 | Compactar implementation-status | W1.3 | ✅ concluído (2026-07-05) |
| P1 | Papéis SRE/Security/FinOps em `core/squad.md` | — | ✅ concluído (2026-07-05) |
| P2 | Helper classify-risk | W3 | ✅ concluído (2026-07-05) |
| P2 | Score de confiança pré-Execution | W8.1 | pendente |
| P2 | spec-vs-impl | W8.2 | pendente |
| P2 | Memória de decisões | W8.3 | pendente |
| P2 | Métricas de retrabalho/intervenção | W6 | pendente |
| P3 | Adapter real (MCP candidato) | W7 | pendente (DH) |
| P3 | Sugestão de model-policy | W8.5 | pendente |
| P3 | Dashboard sobre JSONL | futuro | adiado |

## Base de pesquisa
As recomendações da Anthropic (agentes, context engineering, skills, tools, evals, autonomia governada) foram analisadas e mapeadas às decisões deste plano em [`anthropic-research-notes.md`](anthropic-research-notes.md). Os 5 ajustes sugeridos lá aguardam aprovação humana antes de entrar nas waves.

## Decisões humanas pendentes
Aprovadas em 2026-07-05 ("aprovo 1–7") e executadas:
- [x] Local do plano conceitual versionado → `docs/plan/`; original em `.claude/` removido após verificação de identidade da cópia (idêntica exceto o cabeçalho as-built).
- [x] Fusão `decision.md` → `decisions.md` (W1.1) — template único, append-only.
- [x] Formato do padrão aberto Agent Skills (frontmatter YAML `name`/`description`) nas 7 skills (W5.4).
- [x] Shim por host: `CLAUDE.md` de 1 linha importando `AGENTS.md` (conteúdo continua agnóstico, D3).
- [x] Renome para inglês (D47): `rules/demand-types/product.md` e `rules/demand-types/operational.md`, refs atualizadas.
- [x] Descoberta de skills em catálogos externos + allowlist (W5.5).
- [x] SRE/Security/FinOps como donos de checkpoint (SAFE/emergência) em `core/squad.md`, com fallback registrado em audit.

Ainda pendentes:
- [ ] Nomes de fase: manter EN canônico + apelidos pt-BR ("O quê/Como/Fazer/Validar/Operar") na apresentação (recomendado) ou renomear (alto custo).
- [ ] Canal do connector de notificação (SMTP/Graph/SES/MCP) — pendência original do D44.
- [ ] Primeiro adapter real: qual tipo, qual host, quem é o dono da credencial (W7.1).
- [ ] E-mail registrado em `knowledge/notification.md` permanece no repo do framework ou migra para knowledge da org na adoção (D42)?

## Encerramento do plano
O plano é considerado concluído quando: Waves 0–4 fechadas, `validate-framework` e `validate-links` limpos, 1 demanda real estrita 0/0, e a seção `2.0.0` do `CHANGELOG.md` consolidada com notas de compatibilidade e migração. Só então uma nova versão pode ser discutida (decisão humana).
