# Plano de Implementação — Alfred 2.0.0

> Documento de trabalho da squad (pt-BR, como os artefatos de HUB/App — D47). Os arquivos de runtime do framework permanecem em inglês.

Este plano deriva do diagnóstico completo do Alfred (plano conceitual D1–D47 × estado do repositório, 2026-07-05). Ele guia a evolução incremental do framework, wave por wave, **sem big-bang**.

## Regra de versão (decisão do dono do projeto)
- A versão do Alfred fica em **`2.0.0`** a partir deste plano.
- **Todo o trabalho deste plano acontece dentro da 2.0.0** — nenhuma wave gera bump de versão. O `CHANGELOG.md` acumula as entregas na seção `## Unreleased` até a tag estável 2.0.0 ser criada (W9.7).
- Salto de `0.4.0` → `2.0.0` sem linha `1.x`: decisão humana explícita registrada aqui.
- Demandas de HUB/App novas carimbam `2.0.0`; demandas ativas seguem congeladas na versão carimbada (política de `docs/version-adoption.md`).

## Regras de trabalho
1. **PRs pequenos** — 1 item do backlog por PR sempre que possível.
2. Antes de cada merge: `validate-framework` canônico em Python com 0 erros (o gate roda igualmente em Windows/Linux via CI; não existe wrapper PowerShell desde a W5.8). `validate-links` sem referência quebrada.
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
- [x] W5.7 ✅ (2026-07-15, decisão do dono) AI Stack no allowlist + fallback vira **ordem total**.
  - **AI Stack ativado pelo dono** (2026-07-13): catálogo interno do Itaú (`@ai-stack/cli`, 500+ skills/MCPs/toolkits entre squads) adicionado ao allowlist org em `knowledge/external-catalogs.md`; skill built-in `skills/ai-stack-finder/`. Este repo é o fork corporativo (`itau-corp/itau-sq9-modules-alfred-v2`).
  - **Ordem total** (2026-07-15): o fallback deixa de ser roteado por tema e passa a ser **AI Stack → AWS → Context7**, para **qualquer** tema, parando no primeiro que responde. **Supera** a regra AWS-first/Context7-fallback de W5.5 e o texto "HUB→framework→Context7" de W5.6. Motivo: o roteamento por tema deixava o empate indefinido — "Athena/Hive" é simultaneamente tópico AWS e plataforma interna Itaú — e exigia adivinhar o tema; a ordem total remove o palpite. Dispara **só no passo de fallback** (nenhuma skill ativa cobre), nunca como preâmbulo de turno (`rules/common/tool-discovery-policy.md`).
  - **Fonte única:** a ordem é declarada **uma vez** em `knowledge/external-catalogs.md`; `skills/skills.md` (gerado), `docs/skills-activation.md`, `templates/hub/skills.md`, `install.sh` e os exemplos **apontam**, nunca transcrevem — a cadeia estava copiada em 7 lugares que já discordavam entre si (viola `rules/common/content-validation.md` "reference it, do not transcribe").
  - **Dois gates fechados:** (a) *pin granularity* — o ref pinado é o **conteúdo** (`<name>@<version>` resolvido), não o **cliente** (`@ai-stack/cli` é transporte, como o binário do Context7 MCP, que nunca foi pinado); (b) *discovery ≠ adoption* — consultar é dado (4 gates), **instalar é adoção** (ponteiro no `004-skills.md` da sigla, ref pinado, confirmação humana para `install -s` **e** `mcp install`).
  - **Registro de admissão do `ai-stack-finder`** (regra *Eval before skill*, `skills/skills.md`: gap observado + 2-3 casos concretos, nunca especulativo — não havia registro em lugar nenhum): **gap observado** — squads reimplementam integrações com sistemas internos que já existem prontas e testadas no catálogo, e sem ele o Alfred não tem caminho para descobrir capacidade interna. **Casos:** (1) Figma-to-code — skill pronta no catálogo vs. implementação do zero; (2) ServiceNow/GMUD/RITM — MCP existente vs. integração manual com a API; (3) Athena/Hive — o caso que expôs o empate AWS vs. AI Stack e motivou a ordem total.
- [x] W5.8 ✅ (2026-07-15, decisão do dono) Instalador **bash-only**; `install.ps1` removido em definitivo ("no ambiente nao usamos .ps1 somente .sh"). Caminho Windows = **Git Bash** (`install.sh` já trata `MINGW*|MSYS*|CYGWIN*`; skill instalada em `~/.agents/skills` em toda plataforma). **Supera** a nota de instaladores OS-native. D3 preservado: D3 restringe host/modelo/API/CI/UI, não shell — e o `install/README.md` nomeia Git Bash como o caminho Windows. Novo `assert_bash_only_installer_policy` em `validate-framework.py` transforma "bash-only" de ausência em contrato verificável (escopo fixo de docs vivos; `CHANGELOG.md` e `docs/plan/*` são registro histórico e mantêm a menção).

Aceite: `validate-skills-registry` 0 erros. Não mexer: os 5 agentes (não criar agentes novos).

### Wave 6 — Métricas e evidências
Objetivo: provar valor da squad híbrida com dados.
- [x] W6.0 ✅ (2026-07-05) **Simulado de adoção 2.0.0** (`006-simulado-adocao-v2` no exemplo sq9-pilot): ensaio ponta a ponta offline da linha 2.0.0 exercitando classify-risk, requirements por prioridade, formato único de decisions, spec completa (lado app), carimbo 2.0.0 e JSONL HUB+App — **`validate-demand --strict` 0 erros / 0 avisos nos 2 runtimes**. Vira eval de regressão permanente. De quebra, `validate-demand` ganhou `--app-repo-path`/`--app-current-commit` (encaminhados ao staleness check — lacuna real de uso).
- [ ] W6.1 Medir em ≥5 demandas reais: retrabalho, aceite de 1ª, % aguardando humano, custo (campos D43 já definidos em `metrics/metrics.md`).
- [x] W6.2 **Devin destravado sem API** ✅ (2026-07-20): o transcript local do DEVIN CLI (`cli/transcripts/<sessao>.json`) carrega `prompt_tokens`/`completion_tokens` **exatos por step**, com timestamp real, `model_name` e fronteira de interação (`source: user`) — e a soma reconcilia com `final_metrics` (verificado: 4.968.055 / 27.297). `attribute-usage-devin.py` emite `usage_attributed` por step, dedup por step id, idempotente. **Supera** a premissa de que Session Insights/Consumption API eram pré-requisito: a API continua necessária só para **ACU/custo**, que o Devin publica apenas na web UI. Custo permanece `null` — tokens nunca são convertidos em ACU (o Devin não fatura por token, então qualquer coeficiente seria inventado); USD só via ACU medido × rate card aprovada.
- [ ] W6.2 restante (custo): `import-ccusage.py` ativo para Claude/Codex local CLI com logs duraveis; atualiza `001-state.md` com `cost source: ccusage` / `cost confidence: estimated` / `cost granularity: session` para toolbar, sem gravar totais de sessao no JSONL. `apply-usage-rate-card.py` calcula custo de interacao somente a partir de uso exato + rate card aprovada, em evento separado `usage_cost_attributed`. Devin Session Insights + Consumption API segue pendente de acesso/export aprovado; `normalize-usage-cost` continua para exports genericos com granularidade de interacao.
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
- [x] W8.3 ✅ (2026-07-18) Memória operacional markdown-first: observações estreitas `decision|gotcha`, índice determinístico com custo visível, consulta `startup/search/timeline/get`, detalhe JIT, detecção de fonte stale e confirmação humana na destilação.
- [x] W8.4 ✅ (2026-07-05) `alfred-boot` (2 runtimes) ordena demandas abertas por prioridade de retomada (checkpoint pendente > em andamento > bloqueada, depois última atividade) e imprime "Suggested next" com o motivo — dica de ordenação; o humano escolhe.
- [ ] W8.5 Sugestão automática de model-policy a partir de metrics (humano ratifica — D46).
- [ ] W8.6 **Rubrica LLM-as-judge** (evolução D): grader baseado em modelo para qualidade de spec/summary, calibrado por humano antes de valer.
- [ ] W8.7 **Retrospectiva com transcripts** (evolução E): após N demandas fechadas, analisar audit/JSONL e propor melhorias em regras/perguntas; humano ratifica (estende o padrão D46).

### Wave 9 — Hardening para execução majoritária no Devin ✅ código (2026-07-18)
Objetivo: fechar lacunas de custo, orçamento, contexto, ambiente e verificação
encontradas na avaliação cruzada das práticas oficiais do Devin, Claude Code e
Claude-Mem.

- [x] W9.1 Estado de consumo `alfred.usage.v2`, parser estrito de `/usage`, reset de ciclo, rate card aprovado compartilhado e migração idempotente.
- [x] W9.2 Orçamento com unidade compatível, cinco fases canônicas e guardrails SAFE/aceite/segurança invioláveis.
- [x] W9.3 Progressive disclosure: memória em três níveis, exploração estrutural, read advisor não bloqueante e benchmark de token+recall.
- [x] W9.4 Devin: permissões mínimas, segredos fora de argv/YAML, blueprints por tier, health/pin/rollout, reinjeção pós-compaction e capability probe sem inferência por versão.
- [x] W9.5 Loop de verificação executável, revisor fresco, worktrees para escritores paralelos, CI Ubuntu/Windows e checksum obrigatório para RTK externo.
- [x] W9.5a ✅ (2026-07-18) Refinamento ManagerWorker: correção guided→corrective→strict-minimal, relatório compacto de exploração com evidências, delegação condicional e eval A/B antes de alterar o roteamento padrão.
- [ ] W9.6 Executar os cinco pilotos reais de `docs/hardening-pilot-matrix.md` e anexar evidências.
- [ ] W9.7 Administrador torna o check de CI obrigatório em `main`; humano cria tag estável somente após W9.6.

Aceite do código: testes unitários e `validate-framework` verdes. Aceite de
release: W9.6/W9.7 concluídos com evidência externa; não inferir sucesso.

### Wave 10 — Correções das auditorias cruzadas ✅ código (2026-07-19)
Objetivo: fechar a distância entre o que os contratos prometem e o que o runtime
garante, a partir de 3 auditorias independentes cruzadas (interna + 2 externas,
cada alegação verificada no código antes de aceita).

- [x] W10.1 State como fonte única: `write_state_fields` sem duplicação (substitui a última ocorrência e remove duplicatas), dedup no `migrate-state-v2`, erro de chave duplicada no `validate-demand`.
- [x] W10.2 Fechamento governado: aceite tipado (Rejeitar/Solicitar ajustes nunca concluem), evidências por lane (Standard: PR/merge/reviewer; SAFE: + approvals/rollback/security), validação estrita inclui o App, audit do aceite.
- [x] W10.3 Checkpoint sem auto-update (aviso via cache; adoção só no boot/comando explícito), transição sequencial com `--complete` por fase, SDD gate na entrada de Execution (Standard/SAFE), `--force` auditado.
- [x] W10.4 `demand start` atômico: staging + `os.replace`, guarda contra sobrescrita de demanda App, draft preservado até o fim, rollback em falha parcial.
- [x] W10.5 Observabilidade v1 canônica no CLI (o "v2" sem spec foi abandonado); eventos com `ts`/`event_type`/`event_id`/sequência.
- [x] W10.6 Governança executável: lane derivada dos critérios de risco (reuso `shared/risk.py` + confirmação humana com justificativa auditada), demand type/urgência/owner no draft, sigla derivada (nunca perguntada), pergunta de App em texto livre.
- [x] W10.7 Adapter de e-mail: anexos restritos (raízes/extensão/tamanho), envio ativo aborta sem audit persistido, telemetria sanitizada por allowlist de campos (sem user@hostname, sem paths absolutos, sem linhas não parseadas; destino org inalterado por decisão do dono).
- [x] W10.8 Instalador: `mode: dry-run` (o `auto` não existia no adapter), update bloqueado não aborta reinstalação, gate `--quiet`, versões npm resolvidas logadas.
- [x] W10.9 Robustez Windows: subprocess UTF-8 em todo o CLI, toolbar degrada a ASCII em console não-UTF-8, erros do CLI sem traceback cru.
- [x] W10.10 Consistência documental: agente fantasma "Code Generator", sub-atividade fantasma `units-generation`, glob `scripts/*/workflow/`, "FAST sem Design" reconciliado, teto de tentativas unificado no verification-loop, commons completas no `rules/README.md`, refs root-relative, mapa artefato→template, headings EN nos templates (conteúdo pt-BR, D47).
- [x] W10.11 ✅ (2026-07-19) Regras de governança para casos de borda (Onda 5 do plano de auditoria): **desempate entre humanos** em `core/squad.md` (dono por eixo decide; empate só cruza eixos → pausa, ambas posições em `decisions`, Sponsor decide; segurança não é empate) + hard trigger em `escalation-triggers.md`; **estabilização de emergência que falha/piora** em `rules/demand-types/operational.md` (eleva severidade, força SAFE, 2º ciclo com uma ação autorizada por vez, post-mortem cobre os dois ciclos); **replanejamento × cancelamento** em `rules/lifecycle/lifecycle.md` (`replanejada` mantém id/histórico e exige `--force` auditado; reverter entrega é questão separada, via contrato `vcs`) + ponteiro em `session-continuity.md`.
- [x] W10.12 ✅ (2026-07-19) E2E Standard completo em `tests/scripts/unit/test_governance_gates.py` (draft → start com lane derivada → `--complete` por fase com gate SDD na entrada de Execution → close com evidências de lane → rollup). **Achou 2 bugs reais no caminho que nenhum teste exercitava:** (a) `_transition_gate` quebrava com `TypeError` ao formatar os erros do SDD gate (tuplas `(severity, code, message)` unidas como string) — o gate de Execution nunca havia sido disparado de verdade; (b) `validate-context-budget.py` imprimia `OK budget 8453 <= 8400` porque o `else` estava ligado só ao cap de crescimento, escondendo estouro de orçamento.
- [x] W10.13 ✅ (2026-07-19, decisão do dono) Teto de contexto do cenário `fast-operational-execution` sobe de 9300 → 9400 tk para acomodar a regra de estabilização falha, que precisa morar em `operational.md` (o maior arquivo de demand-type). Continua **abaixo** do cap de crescimento de 10% (9548 sobre o baseline 8680), ou seja, a política de crescimento segue intacta; a decisão fica registrada em `metrics/context-budgets.json`.

Verificação final executada (2026-07-19): `validate-framework` exit 0 · 154 testes unitários verdes · re-simulação real do CLI no scratchpad (draft sem pergunta de sigla → lane FAST derivada 3/10·2/10 → 4 checkpoints → "Rejeitar" bloqueia com `status: rejeitada` → "Aceitar" fecha com exit 0), com `state`, toolbar, checklist e JSONL concordando e 0 chaves duplicadas · 7 eventos `alfred.observability.v1`, higiene 0 problemas, rollup com `cost usd: nao coletado` · telemetria dry-run sem hostname/cwd/paths absolutos e segredo descartado · `bash -n` no instalador OK · `knowledge/notification.md` intocado.

Backlog W10 (não nesta rodada; DH quando marcado):
- [ ] W10.B1 Execution-first executável no CLI (incidentes: investigação/autorização/post-mortem no runtime).
- [ ] W10.B2 Multi-App por demanda com lane override e artefatos por App.
- [ ] W10.B3 `sigla init` completo (skills ativos, knowledge, memória, parâmetros org).
- [ ] W10.B4 Journal transacional + locks por demanda + idempotency keys.
- [ ] W10.B5 Modo `outlook-com` real no adapter de e-mail (pywin32).
- [ ] W10.B6 Consolidar as 8 políticas de contexto/token sobrepostas em `rules/common/`.
- [ ] W10.B7 Alinhar numeração de artefatos HUB×App (mesmo índice, artefatos diferentes).
- [ ] W10.B8 Máquina de transição completa do lifecycle (gates por lane em todas as transições).
- [ ] W10.B9 (owner) Proteção da main + CI required + reviewer independente (W9.7) e 5 pilotos reais (W9.6).

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
| P2 | Allowlist AI Stack + fallback como ordem total (AI Stack → AWS → Context7), fonte única | W5.7 | ✅ concluído (2026-07-15) |
| P2 | Instalador bash-only (`install.ps1` removido; Windows = Git Bash) | W5.8 | ✅ concluído (2026-07-15) |
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
| P2 | Memória de decisões | W8.3 | ✅ concluído (2026-07-18) |
| P0 | Hardening Devin/context/custo/orçamento | W9.1–W9.5 | ✅ código concluído (2026-07-18) |
| P0 | Cinco pilotos reais de hardening | W9.6 | pendente (ambiente/credenciais) |
| P0 | CI obrigatório + tag estável | W9.7 | pendente (admin/humano) |
| P2 | Métricas de retrabalho/intervenção | W6 | pendente |
| P2 | Usage-cost real: desenho Devin-first + ccusage secundário | W6.2 | parcial: ccusage ativo; Devin API pendente |
| P3 | Adapter real (MCP candidato) | W7 | pendente (DH) |
| P3 | Avaliar Codebase Memory MCP para instalação corporativa + integração opcional no install do Alfred | W7.5 | pendente (DH: fonte aprovada, segurança, empacotamento, DEVIN CLI) |
| P3 | Sugestão de model-policy | W8.5 | pendente |
| P3 | Dashboard sobre JSONL | futuro | adiado |

## Organização de `scripts/` (pedido do dono, 2026-07-05)
- [x] ✅ Diretório reorganizado por responsabilidade nos 2 runtimes: `validators/` · `workflow/` · `metrics/` · `adapters/` (python-only). Referências atualizadas em todo o repo (CHANGELOG e plano conceitual preservados como históricos); smoke tests e validação estrita 0/0 pós-mudança. Nota de compatibilidade no CHANGELOG (paths de chamada mudaram; flags idênticos).
- [x] ✅ Política simplificada de runtime (pedido do dono, 2026-07-09): Python passa a ser o runtime canônico para lógica de helpers e para exemplos de uso. Instalador é **bash-only** (`install/install.sh`, inclusive no Windows via Git Bash) — o `install.ps1` foi removido na W5.8.
- [ ] Remover gradualmente helpers de runtime não canônico quando forem tocados, sem big-bang e sem quebrar instalações existentes.

### Migração SOLID dos scripts (observabilidade)
Objetivo: lógica reutilizável mora em `scripts/shared/observability/` (SOLID); comandos em `scripts/metrics/` são drivers finos. Boundary e regras em [`scripts-architecture.md`](../scripts-architecture.md), travadas por `validate-scripts-architecture.py`.
- [x] W-SOLID.1 ✅ (2026-07-12) **Núcleo de ingestão migrado.** Custo unificado em domínio (`domain/services/rate_card.py` `price_usage`, substituindo os dois `calculate_cost` duplicados) + carga de rate card em infra (`infrastructure/rate_cards/`). Parsing host-específico saiu dos comandos para adapters reais: `adapters/claude/transcript.py` (parse de transcript + `load_requests`), `adapters/claude/transcript_cursor.py` (cursor único, antes duplicado em 2 comandos), `adapters/claude/hook.py` (raw telemetry, helpers de artefato/redação/clock injetados) e `adapters/ccusage/session.py` (seleção de sessão). Os 4 comandos (`attribute-usage-transcript`, `claude-code-usage-hook`, `import-ccusage`, `apply-usage-rate-card`) viraram drivers finos via `shared.*` — contrato de CLI inalterado, saída byte-idêntica (fixtures ts-normalizadas) e `validate-observability-intelligence` verde. Enforcement endurecido: anti-stub, sem-parsing/pricing-inline no comando, comando-delega. Gate `validate-framework` 0 erros.
- [x] W-SOLID.2 ✅ (2026-07-12) **Classificador de artefato desduplicado.** As duas cópias divergentes de `classify_artifact` (domínio × `scripts/metrics/observability.py`) viraram uma só em `domain/services/artifact_classifier.py`, com a lista completa de tipos (prefixos de framework + nomes de demanda + extensões) e a melhoria de classificar teste antes de `source_code`. Equivalência provada contra a versão emitida (idêntica para todo caso não-teste). `scripts/metrics/observability.py` passou a reexportar do shared. Gate `validate-framework` 0 erros.
- [x] W-SOLID.3 ✅ (2026-07-12) **Helpers de `observability.py` consolidados em `shared`.** Redação e leitura de uso (puras) foram para o domínio (`domain/services/redaction.py`, `domain/services/legacy_usage.py`); construção de artefato (I/O) e dedup de eventos (json) foram para infra (`infrastructure/artifacts.py`, `infrastructure/legacy_events.py`). `scripts/metrics/observability.py` virou shim fino de reexport — todos os call sites (`from metrics.observability import …`) seguem inalterados; gate `validate-framework` 0 erros. `generate-metrics-rollup`/`generate-metrics-insights`/`normalize-usage-cost` seguem como drivers que consomem o shim (adelgaçamento direto fica sob demanda, sem ganho que justifique o risco).
- [ ] W-SOLID.4 (sob demanda) Preencher os adapters ainda stub (`codex/*`, `devin/*`) com parsing real quando houver fonte/fixture aprovada.

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
