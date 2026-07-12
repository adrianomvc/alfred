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
2. Antes de cada merge: `validate-framework` canônico em Python com 0 erros; rodar também o wrapper PowerShell quando ele mudar ou quando o fluxo Windows/host for afetado. `validate-links` sem referência quebrada.
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
- [x] W1.9 **Otimização de contexto/tokens** ✅ (2026-07-08): pacote fechado em [`architecture-review-context-2026-07.md`](architecture-review-context-2026-07.md) e handoff em [`context-optimization-progress.md`](context-optimization-progress.md). Reduziu custo fixo planejado de sessão (~8,230 → ~3,300 tk), adicionou registries/manifests gerados, skills enxutas, shims de host por template, ordem cache-friendly e baseline em `metrics/baselines.md`.

Aceite: `validate-framework` + `validate-demand` nos dois exemplos, 0 erros. Não mexer: toolbar, welcome, boot, state.

### Wave 2 — SDD completo
Objetivo: fechar o contrato documental intenção → desenho → execução → validação → operação.
- [x] W2.1 ✅ (2026-07-05) `templates/app/spec.md` completo (plano 5.3.2): fora de escopo, alternativas (SAFE), dependências, impactos, rollout/rollback (SAFE), com marcação por lane.
- [x] W2.2 ✅ (2026-07-05) `templates/hub/post-mortem.md` criado (incidente, timeline, causa raiz, spec retroativa, decisões, lições, ações preventivas → follow-up).
- [x] W2.3 ✅ (2026-07-05) `templates/hub/skills.md` criado (skills ativas com ref pinada + allowlist de catálogos externos ligada ao guardrail W1.4).
- [x] W2.4 ✅ (2026-07-05) Guardrail de testes em `skills/coding-standard/SKILL.md` e `rules/lifecycle/validation/validation.md`: nunca remover/afrouxar teste para passar num gate — é escalação, não correção.

Aceite: `validate-sdd-gate` reconhece as seções novas; exemplo Execution-first referencia o template de post-mortem. Não mexer: DoD das lanes.

### Wave 3 — Risk Mode assistido
Objetivo: classificação computável, opcional e degradável (D3).
- [x] W3.1 ✅ (2026-07-05) Helper `classify-risk` nos 2 runtimes: computa os 2 eixos (critérios 0/1/2), aplica overrides duros, lembra a trava anti-SAFE e imprime o bloco pt-BR para `004-risk.md`.
- [x] W3.2 ✅ (2026-07-05) Referenciado como opcional em `rules/lifecycle/inception/sub-activities/risk-mode-proposal.md` e em `scripts/README.md` (degrada para manual, D3).

Aceite ✅: 4 casos testados nos 2 runtimes — FAST (1/1), Standard (4/5), SAFE (8/6) e o caso "simples e perigoso" (base FAST + dados sensíveis=2 → mínimo Standard). Overrides duros disparam (checklist 8.4). Não mexido: o checklist de `core/risk-mode.md` (fonte de verdade; o helper só o computa).

### Wave 4 — Demanda real integrada
Objetivo: primeira demanda SQ9 real ponta a ponta com validação estrita.
- [ ] W4.1 Coletar parâmetros externos via `templates/hub/environment-parameters.md` (contas, endpoints, credenciais, host).
- [ ] W4.2 Executar 1 demanda Standard ou SAFE real: 5 fases, summary, hub-sync, rollup de métricas.
- [ ] W4.3 `validate-demand -Strict` 0/0 na demanda real.

Riscos: bloqueio por credenciais → usar simuladores de `examples/connectors/` enquanto isso. Não mexer: versão do framework congelada na demanda (D15/D16).

### Wave 5 — Skills da casa
Objetivo: exercitar extensão real do registry.
- [x] W5.1 ✅ (2026-07-09) `aws/agent-toolkit-for-aws` registrada como skill externa **available**, **pinada em `main`@`4217c65a`**, no HUB de exemplo `fresh-sigla-onboarding`: `004-skills.md` (tabelas External Skills + External Catalogs), `001-state.md` e audit `007-audit.md`. Exercita o versionamento (pin branch+commit) e os 4 gates (allowlist org já em `knowledge/external-catalogs.md` → pin → confirmação humana → conteúdo=dado). A ativação disparada por **demanda AWS real** fica para uma demanda AWS (Wave 4); aqui a skill fica `available`, não copiada.
- [ ] W5.2 Novas skills de linguagem/plataforma só quando a stack real pedir (gatilho, não antecipação).
- [x] W5.3 ✅ (2026-07-05) Disciplina "Eval before skill" documentada em `skills/skills.md`: skill nasce de lacuna observada + 2–3 casos que dobram como aceite.
- [x] W5.4 ✅ (2026-07-05, aprovado pelo dono) Frontmatter YAML `name`/`description` (padrão aberto Agent Skills) nas 7 skills + convenção no registry; skills podem apontar helpers executáveis próprios (opcional, D3).
- [x] W5.5 ✅ (2026-07-05, aprovado pelo dono) Seção "Discovery in external catalogs (on demand)" em `skills/skills.md`: busca em catálogo registrado (ex.: Context7) com os 4 gates — allowlist, pin por ref, humano confirma 1º uso, conteúdo = dado (W1.4). Sem catálogo na allowlist → perguntar, nunca buscar de fonte arbitrária. Confiabilidade analisada em [`anthropic-research-notes.md`](anthropic-research-notes.md).
  - **Context7 ativado pelo dono** (2026-07-05): allowlist org em `knowledge/external-catalogs.md` (política no formato policy-template); registro MCP por projeto no DEVIN via template `config.local.template.json` em `hosts/devin-cli/` (alfred-email + context7), criado no primeiro boot da skill `/alfred` com confirmação humana. Gates de uso permanecem.
  - **AWS ativado pelo dono** (2026-07-09): `aws/agent-toolkit-for-aws` (fonte oficial first-party) adicionado ao allowlist org em `knowledge/external-catalogs.md`, escopado a **docs + agent-skills** (a superfície de API/execução do MCP fica de fora — seria connector SAFE à parte). Regra de precedência de docs: **AWS-first para tópicos AWS, Context7 como fallback geral**. Complementa a skill built-in `platform-aws-data`.
- [x] W5.6 ✅ (2026-07-09, aprovado e executado pelo dono) Layout pasta-por-skill + skills locais no HUB + precedência HUB→framework→Context7.
  - **Layout:** migrar `skills/<nome>.md` (flat) → `skills/<nome>/SKILL.md`; a pasta da skill pode carregar arquivos de apoio (checklist, tabela de referência, template) lidos JIT após o `SKILL.md` (reforça "~1 tela por arquivo" + progressive disclosure). **Helper executável continua canônico em `scripts/`** — pasta de skill = conteúdo/dado, não código (regra de home único do `AGENTS.md` preservada).
  - **Framework e HUB carregam 1..N skills.** O HUB passa a suportar **skill local da squad** (`<hub>/skills/<nome>/SKILL.md`, escrita pela squad para seu processo) **além** do ponteiro externo já existente.
  - **Precedência HUB → framework → Context7** (a registrar também em `skills/skills.md` na seção `Precedence`): 1) segurança primeiro — mais seguro/restritivo vence entre tiers, sigla **endurece, nunca afrouxa**; 2) especificidade — para a mesma ferramenta, a skill do HUB sobrepõe a global do framework; 3) fallback — sem skill ativa cobrindo a necessidade, discovery em catálogo allowlisted (AWS-first para AWS, depois Context7); sem fonte na allowlist → perguntar ao humano.
  - **Executado (2026-07-09):** 7 skills movidas para `skills/<nome>/SKILL.md` via `git mv` (histórico preservado); `generate-registry` e `validate-skills-registry` descobrem via `glob("*/SKILL.md")`; `skills/skills.md` regenerada com a seção `Precedence` reescrita (HUB→framework→Context7) + layout de pasta em `Loading`/`External skills`; `validate-framework` (lista de arquivos), refs no repo e nota de convenção no `AGENTS.md` atualizados. Gate: `validate-framework` exit 0, `validate-links` 0 quebrados, 7 skills OK. Conteúdo das 7 skills e os 5 agentes intactos.

Aceite: `validate-skills-registry` 0 erros. Não mexer: os 5 agentes (não criar agentes novos).

### Wave 6 — Métricas e evidências
Objetivo: provar valor da squad híbrida com dados.
- [x] W6.0 ✅ (2026-07-05) **Simulado de adoção 2.0.0** (`006-simulado-adocao-v2` no exemplo sq9-pilot): ensaio ponta a ponta offline da linha 2.0.0 exercitando classify-risk, requirements por prioridade, formato único de decisions, spec completa (lado app), carimbo 2.0.0 e JSONL HUB+App — **`validate-demand --strict` 0 erros / 0 avisos nos 2 runtimes**. Vira eval de regressão permanente. De quebra, `validate-demand` ganhou `--app-repo-path`/`--app-current-commit` (encaminhados ao staleness check — lacuna real de uso).
- [ ] W6.1 Medir em ≥5 demandas reais: retrabalho, aceite de 1ª, % aguardando humano, custo (campos D43 já definidos em `metrics/metrics.md`).
- [ ] W6.2 parcial: `import-ccusage.py` ativo para Claude/Codex local CLI com logs duraveis; atualiza `001-state.md` com `cost source: ccusage` / `cost confidence: estimated` / `cost granularity: session` para toolbar, sem gravar totais de sessao no JSONL. `apply-usage-rate-card.py` calcula custo de interacao somente a partir de uso exato + rate card aprovada, em evento separado `usage_cost_attributed`. Devin Session Insights + Consumption API segue pendente de acesso/export aprovado; `normalize-usage-cost` continua para exports genericos com granularidade de interacao.
- [ ] W6.3 1 relatório de insights comparado com `metrics/baselines.md`, ratificado por humano.

Não mexer: baselines sem dados reais.

### Wave 7 — Primeiro adapter real
Objetivo: um connector sai de `contract`/`handoff` para `active`.
- [x] W7.1 ✅ (2026-07-05, decisão do dono) Primeiro adapter = **notification**, canal = **MCP em Python** (funciona em qualquer host MCP; registrado via `claude mcp add` no Claude Code). Pendente para `active`: credenciais SMTP e dono.
- [x] W7.2 ✅ parcial (2026-07-05) `mcp-email-server` (`scripts/`, stdlib puro): estados `contract → handoff → dry-run` percorridos — dry-run compõe o `.eml` no outbox (é o próprio handoff materializado); testado ponta a ponta (handshake MCP, envio dry-run, recusa fora da allowlist auditada). `active` aguarda `SMTP_*` reais.
- [x] W7.3 ✅ (2026-07-05) Seção "Response format & error guidance" em `connectors/connectors.md`; aplicada concretamente no adapter de e-mail (resposta concisa; erro diz o próximo passo e quando só um humano desbloqueia).
- [x] W7.4 ✅ (2026-07-05) Seção "Optional deterministic enforcement (hooks)" em `hosts/README.md`: validadores existentes como stop/pre-write hooks; advisório × determinístico; degrada (D3).
- [ ] W7.5 Avaliar **Codebase Memory MCP** para brownfield grande: identificar uma implementação/fonte aprovada para máquina corporativa, entender instalação offline/Artifactory, confirmar suporte no DEVIN CLI via `.devin/config.local.json`, definir contrato `connectors/codebase-memory.md` (find_symbol, references, impact, related_tests), fallback `rg`+leitura manual, e só então decidir se o installer do Alfred deve configurar esse MCP opcionalmente.

Aceite: `validate-connectors` 0 erros; 1 handoff real registrado no audit. Não mexer: regra "IA nunca mergeia branch protegida".

### Wave 8 — Inteligência evolutiva
Objetivo: Alfred mais inteligente para squad híbrida. Depende de dados das Waves 4–6; cada item entra como demanda dogfooding.
- [x] W8.1 ✅ (2026-07-05) Helper `confidence-score` (2 runtimes): score 0–100 de perguntas sem resposta + lane não confirmada + decisions/plano ausentes (Std/SAFE) + reverse-eng sem commit; ≥80 segue · 50–79 revisa com humano · <50 para e escala (D27). O score informa; o humano decide.
- [x] W8.2 ✅ (2026-07-05) Helper `spec-vs-impl` (2 runtimes): compara critérios de aceite da spec com a evidência de validação (heurística de cobertura textual); aponta lacunas, nunca aprova. **No primeiro uso já achou lacuna real**: a evidência do simulado não cobria os critérios do lado app — corrigida.
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
| P2 | Allowlist AWS (agent-toolkit-for-aws) + precedência AWS-first para docs | W5.5 | ✅ concluído (2026-07-09) |
| P2 | Layout pasta-por-skill (`<nome>/SKILL.md`) + skills locais no HUB + precedência HUB→framework→Context7 | W5.6 | ✅ concluído (2026-07-09) |
| P2 | Connector: response format + error guidance | W7.3 | ✅ concluído (2026-07-05) |
| P2 | Hooks determinísticos por host (opcional) | W7.4 | ✅ concluído (2026-07-05) |
| P2 | Rubrica LLM-as-judge para artefatos | W8.6 | pendente |
| P2 | Corrigir exemplos: JSONL de observabilidade do lado App | W6 | ✅ concluído (2026-07-05): `008-observability-log.jsonl` criado nas 5 demandas de exemplo; `validate-demand` em modo app passa; exemplos históricos ficam no tier ilustrativo/non-strict até migração |
| P2 | Recomendação de próxima ação no boot | W8.4 | ✅ concluído (2026-07-05) |
| P2 | Retrospectiva com transcripts | W8.7 | pendente |
| P1 | Otimização de contexto/tokens do framework | W1.9 | ✅ concluído (2026-07-08) |
| P1 | Template hub/skills.md | W2.3 | ✅ concluído (2026-07-05) |
| P1 | Compactar implementation-status | W1.3 | ✅ concluído (2026-07-05) |
| P1 | Papéis SRE/Security/FinOps em `core/squad.md` | — | ✅ concluído (2026-07-05) |
| P2 | Pergunta explícita e opcional de repo de template no onboarding + fallback "sem template" no Design (fecha elicitação do D35) | — | ✅ concluído (2026-07-09) |
| P2 | Model-policy: Inception e Design fixos em `strong` em todas as lanes (decisão do dono) | — | ✅ concluído (2026-07-09) |
| P2 | Model-policy: Execution nunca em `cheap` (piso mínimo medium; FAST sem gate de Design) — decisão do dono | — | ✅ concluído (2026-07-09) |
| P2 | Model-policy eixo 2 (`effort` por fase×lane) + task budget na Execution + subagent barato p/ units paralelas (práticas Anthropic) | — | ✅ concluído (2026-07-09) |
| P2 | Model-policy: Inception FAST/Std → medium·high (effort compensa; SAFE segue strong) + mapa tier→modelo Claude preenchido (Haiku/Sonnet/Opus) | — | ✅ concluído (2026-07-09) |
| P2 | Model-policy refino: Inception FAST=strong (sem gate de Design), Validate nunca `cheap` (mín. medium), Operate=exceção documentada ao piso SAFE (medium) — decisão do dono | — | ✅ concluído (2026-07-09) |
| P2 | Sigla **auto-derivada** do nome do repo (`itau-<sigla>-...`), nunca perguntada — rótulo de exibição only (regra em `core/boot.md`); decisão do dono, nasceu do teste real | — | ✅ concluído (2026-07-09) |
| P2 | Onboarding "provisiona, não interroga": HUB novo → cria esqueleto direto, owner/apps/tracker=pending, sem menu de escopo (regra em `onboarding-sigla.md` + `boot.md`); nasceu do teste real | — | ✅ concluído (2026-07-09) |
| P2 | Helper classify-risk | W3 | ✅ concluído (2026-07-05) |
| P2 | Score de confiança pré-Execution | W8.1 | ✅ concluído (2026-07-05) |
| P2 | spec-vs-impl | W8.2 | ✅ concluído (2026-07-05) |
| P2 | Memória de decisões | W8.3 | pendente |
| P2 | Métricas de retrabalho/intervenção | W6 | pendente |
| P2 | Usage-cost real: desenho Devin-first + ccusage secundário | W6.2 | parcial: ccusage ativo; Devin API pendente |
| P3 | Adapter real (MCP candidato) | W7 | pendente (DH) |
| P3 | Avaliar Codebase Memory MCP para instalação corporativa + integração opcional no install do Alfred | W7.5 | pendente (DH: fonte aprovada, segurança, empacotamento, DEVIN CLI) |
| P3 | Sugestão de model-policy | W8.5 | pendente |
| P3 | Dashboard sobre JSONL | futuro | adiado |

## Organização de `scripts/` (pedido do dono, 2026-07-05)
- [x] ✅ Diretório reorganizado por responsabilidade nos 2 runtimes: `validators/` · `workflow/` · `metrics/` · `adapters/` (python-only). Referências atualizadas em todo o repo (CHANGELOG e plano conceitual preservados como históricos); smoke tests e validação estrita 0/0 pós-mudança. Nota de compatibilidade no CHANGELOG (paths de chamada mudaram; flags idênticos).
- [x] ✅ Política simplificada de runtime (pedido do dono, 2026-07-09): Python passa a ser o runtime canônico para lógica de helpers e para exemplos de uso. `install.ps1` e `install.sh` continuam nativos por sistema operacional.
- [ ] Remover gradualmente helpers de runtime não canônico quando forem tocados, sem big-bang e sem quebrar instalações existentes.

### Migração SOLID dos scripts (observabilidade)
Objetivo: lógica reutilizável mora em `scripts/shared/observability/` (SOLID); comandos em `scripts/metrics/` são drivers finos. Boundary e regras em [`scripts-architecture.md`](../scripts-architecture.md), travadas por `validate-scripts-architecture.py`.
- [x] W-SOLID.1 ✅ (2026-07-12) **Núcleo de ingestão migrado.** Custo unificado em domínio (`domain/services/rate_card.py` `price_usage`, substituindo os dois `calculate_cost` duplicados) + carga de rate card em infra (`infrastructure/rate_cards/`). Parsing host-específico saiu dos comandos para adapters reais: `adapters/claude/transcript.py` (parse de transcript + `load_requests`), `adapters/claude/transcript_cursor.py` (cursor único, antes duplicado em 2 comandos), `adapters/claude/hook.py` (raw telemetry, helpers de artefato/redação/clock injetados) e `adapters/ccusage/session.py` (seleção de sessão). Os 4 comandos (`attribute-usage-transcript`, `claude-code-usage-hook`, `import-ccusage`, `apply-usage-rate-card`) viraram drivers finos via `shared.*` — contrato de CLI inalterado, saída byte-idêntica (fixtures ts-normalizadas) e `validate-observability-intelligence` verde. Enforcement endurecido: anti-stub, sem-parsing/pricing-inline no comando, comando-delega. Gate `validate-framework` 0 erros.
- [x] W-SOLID.2 ✅ (2026-07-12) **Classificador de artefato desduplicado.** As duas cópias divergentes de `classify_artifact` (domínio × `scripts/metrics/observability.py`) viraram uma só em `domain/services/artifact_classifier.py`, com a lista completa de tipos (prefixos de framework + nomes de demanda + extensões) e a melhoria de classificar teste antes de `source_code`. Equivalência provada contra a versão emitida (idêntica para todo caso não-teste). `scripts/metrics/observability.py` passou a reexportar do shared. Gate `validate-framework` 0 erros.
- [ ] W-SOLID.3 (opcional, quando tocados) Consolidar os demais helpers de `scripts/metrics/observability.py` (`canonical_artifact`/`safe_path`/`effective_events`/`usage_tokens`) em `shared` via shim de reexport, e adelgaçar `generate-metrics-rollup.py`/`generate-metrics-insights.py`/`normalize-usage-cost.py`. Baixo ganho arquitetural (código único, não duplicado) × risco de regressão de saída — fazer sob demanda. Preencher os adapters ainda stub (`codex/*`, `devin/*`) com parsing real quando houver fonte/fixture.

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

- [x] Canal do connector de notificação (D44): **MCP em Python** — decidido pelo dono em 2026-07-05; adapter em dry-run.
- [x] Primeiro adapter real (W7.1): **notification** via MCP.
- [x] E-mail em `knowledge/notification.md`: já não há endereço hardcoded no framework (o arquivo delega à sigla/HUB); destino vem de configuração (`ALFRED_EMAIL_DEFAULT_TO`/knowledge da adoção) — resolvido de fato.

- [x] Estrutura de `hosts/` ✅ (2026-07-07, decisão do dono): permanece `hosts/<nome-do-produto>/` (claude-code, devin-cli, github-copilot, codex) — **fonte versionada e visível**; a instalação materializa nos locais nativos de cada IA (`~/.claude/skills/`, `%APPDATA%\devin\skills\`, `.devin/` por projeto, `.github/`). Dot-names foram descartados: pastas ocultas em Unix, nomes nativos inconsistentes entre IAs (`.github` ≠ Copilot obviamente), e dotfolder na raiz ativaria "modo Alfred" ao editar o próprio framework. Distinção documentada em `hosts/README.md`.
- [x] Nomes de fase ✅ (2026-07-05, decisão do dono): EN permanece canônico (pastas, regras, validadores); apelidos pt-BR **"O quê · Como · Fazer · Validar · Operar"** registrados no `core/glossary.md` e exibidos no welcome (`core/welcome.md`). Camada de apresentação apenas (D47).

- [x] Telemetria por e-mail ✅ (2026-07-05, decisão do dono): os logs de observabilidade de **cada pessoa rodando o Alfred** são enviados automaticamente ao destino org (`telemetry_to` em `knowledge/notification.md`, copiado pelo installer para o config de cada máquina) — tool `send_telemetry` no MCP (lote = `{sender, collected_at, source, event}`), disparo na strategic-notification a cada geração de eventos. **Transporte provisório até a API de telemetria existir (D45)** — trocar o transporte não toca as regras. Endereço confirmado pelo dono: `adriano.vilela-costa@itau-unibanco.com.br`.
- [x] Cadastro do e-mail ✅ (2026-07-05, decisão do dono): acontece **no processo de install** — os instaladores (`install/`, 2 runtimes) perguntam o e-mail (ou `-Email`/`ALFRED_EMAIL`), gravam `~/.alfred-email.json` em dry-run sem sobrescrever config existente, e registram o MCP `alfred-email` no Claude Code quando CLI+Python existem (best-effort; degrada, D3).

- [x] Otimização de contexto/tokens ✅ (2026-07-08, decisões do dono): aprovados e executados os 6 DHs do pacote — split do welcome, Risk Mode JIT na Inception, model-policy JIT na seleção de modelo, toolbar quick, contrato enxuto de skills com frontmatter, e shims de host gerados de template. Relatório final: [`architecture-review-context-2026-07.md`](architecture-review-context-2026-07.md).

Ainda pendentes:
- [ ] Credenciais SMTP + dono para promover o adapter de e-mail de `dry-run` a `active` (preencher `smtp{}` no `~/.alfred-email.json`).

## Encerramento do plano
O plano é considerado concluído quando: Waves 0–4 fechadas, `validate-framework` e `validate-links` limpos, 1 demanda real estrita 0/0, e a seção `2.0.0` do `CHANGELOG.md` consolidada com notas de compatibilidade e migração. Só então uma nova versão pode ser discutida (decisão humana).
