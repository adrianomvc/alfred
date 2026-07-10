# Alfred — Planejamento Conceitual (modo Plan)

> **Cópia versionada (Wave 0 / 2.0.0).** Origem: `.claude/prompt-para-claude-ticklish-lemur.md`. Este é o documento fonte das decisões D1–D47 — **histórico e point-in-time**: caminhos e nomes citados refletem o desenho original, não a árvore atual (por isso este arquivo é excluído do `validate-links`, como o CHANGELOG).
>
> **Nota as-built (Fase 7):** a implementação evoluiu a nomenclatura do desenho original:
> - artefatos numerados com pastas de fase: `001-state.md`, `002-problem.md` … em `01-inception/` `02-design/` `03-execution/` `04-validate/` `05-operation/` (o plano cita `state.md`, `problem.md` soltos);
> - `context.md` do HUB foi absorvido pelo `001-index.md` (seções Sigla/Apps/Skills/Knowledge);
> - a pasta técnica dos apps é `.alfred-docs-app/` (o plano cita `.alfred/`); o HUB é `alfred-docs-hub/`;
> - a árvore real do repositório é a referência as-built; este documento permanece como fonte conceitual das decisões.

> Documento vivo. Acumula as 8 fases de desenho do Alfred.
> Nada vira estrutura/código real até a Fase 7-8 + autorização explícita do usuário.

## Contexto
O usuário está criando o **Alfred**: um **framework** para squads híbridas (humanos + agentes de IA) que **escolhe o nível de processo por risco e complexidade, não por preferência**. Base = AI-DLC (ciclo) + SDD (clareza) + Squad Híbrida (execução). Risk Mode (FAST/Standard/SAFE) é o seletor de governança por cima da base. HITL para decisão humana, JIT Context Loading para eficiência.

## Decisões de fundação (confirmadas pelo usuário)
- **D1 — Alfred = AI-DLC customizado.** O motor do Alfred é o AI-DLC (`D:\Projetos\aidlc-workflows`) **adaptado/customizado**: mantém o que serve (state, session-continuity, depth levels, stages condicionais, reverse-eng) e altera o que não serve (5 fases no lugar de 3, Risk Mode explícito, audit enxuto no lugar do raw, sem aprovação obrigatória por stage). Não roda o AI-DLC stock nem reinventa do zero — é uma versão do AI-DLC governada pelas decisões do Alfred.
- **D2 — Agentes = especialidades materializadas em artefatos.** Cada agente é um artefato versionado (papel + contexto JIT + formato de interação), carregado sob demanda. **Orquestração multi-agente faz parte do Alfred** (um Orchestrator roteia entre agentes) e há **acompanhamento de métricas dos agentes**.
- **D3 — Markdown agnóstico (invariante forte).** Sem dependência de tooling específico; funciona em qualquer IDE/agente. **Tudo no Alfred degrada para markdown/ASCII puro.** A representação oficial e portável é texto: o Process Toolbar é ASCII, os artefatos são `.md`, o estado é texto. Qualquer automação (coleta de métricas, custo em $/tokens, toolbar visual rico, renderização com ícones) é **camada opcional** sobre essa base — se não existir, o Alfred continua 100% funcional com preenchimento manual/aproximado. **Nada no framework pode exigir** um modelo, API, CI ou UI específicos. Os mockups visuais são ilustração, não a spec.
- **D4 — Rastreio.** `state` sempre; `decisions` em Standard/SAFE; **`audit` em TODOS os modos** (enxuto em FAST, completo em SAFE). **Compliance NÃO faz parte do Alfred** (sem papel nem gate de compliance); o `audit` existe para rastreabilidade técnica/operacional e para registrar quem decidiu o quê — não para aprovação regulatória.
- **D7 — Humano no controle e responsável pelas decisões.** O Alfred usa AI-DLC e agentes para acelerar, mas **a decisão é sempre humana e o humano é o responsável** por ela em todos os modos. A IA propõe, organiza, executa e registra; ela nunca "é dona" de uma decisão. Em FAST a responsabilidade é por delegação (o humano assume o que a IA fez, registrado em `audit`); em Standard/SAFE há checkpoint explícito antes.

## Premissas
1. Alvo = 1 squad usando agente de código. Não é plataforma multi-tenant.
2. Agentes = papéis/prompts sob demanda com fonte de verdade em artefato.
3. Artefatos = markdown versionado no repo do projeto.
4. Risk Mode classificado por demanda/unidade, não por projeto.
5. Herda mecanismos do AI-DLC onde já resolvem.
6. Humano é sempre o responsável pela decisão (D7). HITL com checkpoint explícito em Standard/SAFE; em FAST, responsabilidade por delegação + registro em audit.
7. Idioma (D47): interações com pessoas em pt-BR; arquivos do Framework em inglês; docs/artefatos gerados (HUB/App) em pt-BR.

## Pendências resolvidas
- **S1 — Brownfield SIM, com engenharia reversa PESADA.** Em brownfield, o Alfred exige compreensão profunda do produto antes de agir — herda o Reverse Engineering do AI-DLC como passo real. Princípio: **só mexer com certeza do que precisa ser feito.** Não é leitura pontual; é entendimento do produto.
- **S2 — Squad multi-humano.** Papéis humanos pesam: HITL distribuído (PM=escopo, Tech Lead=arquitetura/risco técnico, QA=aceite, Sponsor/Liderança=custo/estratégia). Handoffs importam.
- **S3 — Regulado SIM.** `audit` existe em **todos os modos** (enxuto→completo); SAFE adiciona `decisions` + audit completo — para rastreabilidade e registro de responsabilidade humana, **sem papel/gate de compliance** (Compliance fora do Alfred).

## D5 — Taxonomia de demandas (3 streams)
Alfred classifica toda demanda em um stream + tipo. O stream influencia o caminho no ciclo (não só o Risk Mode).
- **Produto:** nova feature · melhoria funcional · nova jornada · melhoria de UX · experimento · mudança de regra de negócio · evolução de produto.
- **Operacional:** bug · incidente · hotfix · alerta · falha em produção · erro em pipeline · degradação · rollback emergencial · suporte.
- **Engineering:** refactor · débito técnico · upgrade · migração · observabilidade · performance · segurança · FinOps · automação interna · melhoria de arquitetura · mudança por provedor.

## D6 — Caminho de emergência (Operacional crítico)
Incidente/hotfix/rollback podem ter **risco alto + tempo curtíssimo**. O ciclo linear não serve. Alfred prevê um **fluxo Execution-first**: estabiliza primeiro (com checkpoint humano mínimo de autorização), e completa Inception/Design/Validate *a posteriori* (post-mortem + decisions + spec retroativa). Risk Mode aqui mede risco normalmente, mas o **modo de tempo** é comprimido. Detalhe na Fase 2.

## D8 — Arquitetura de 3 camadas (3 repos)
O Alfred opera em três repositórios distintos:
1. **Repo do Framework** — o Alfred em si (princípios, risk-mode, lifecycle, agentes, skills, templates). **Fonte única, referenciada pelos usuários (não copiada para dentro do HUB/app)** — ver D15. Não contém dados de iniciativa.
2. **Repo HUB (1 por sigla)** — cada **sigla sistêmica** tem **seu próprio HUB**. Guarda o *o quê/por quê*, decisões e o `state`. Fonte de verdade do `state`.
3. **Repo da Aplicação** — código da app + artefatos **técnicos referentes àquele repo** (engenharia reversa, spec técnica, audit técnico, métricas do repo). Uma sigla pode ter **N apps**.

**Hierarquia (tudo dentro de 1 sigla — não há cross-sigla):**
`Sigla (HUB) → Iniciativa → Demanda`
- **Sigla** = sistema; tem 1 HUB e N apps.
- **Iniciativa** = uma solução; **pode ser multirepo** (envolver vários apps da sigla). Uma sigla tem **várias iniciativas**.
- **Demanda** = unidade de trabalho que pendura numa iniciativa; pode tocar 1+ apps da iniciativa. É onde mora o `state` e a classificação Risk Mode.

**Distribuição (dividido HUB+App):**
- **HUB (da sigla):** contexto da sigla + apps; por iniciativa: `initiative.md` (objetivo + repos envolvidos); por demanda: `state` (fonte de verdade), problem/escopo, `risk`, `decisions`, `audit`, `metrics`, `summary`. No nível da sigla: `index`, `skills` ativas.
- **App (por repo):** `reverse-eng`, `spec` técnica, `audit` técnico, `metrics` técnicas, `index` local, o PR.
- **Correlação:** o `id-demanda` é compartilhado entre o HUB e as apps; o `state` linka os artefatos técnicos em cada app que a demanda toca.

## D9 — Transparência de progresso (orientação a cada interação)
**A cada interação**, o usuário precisa saber **onde está no fluxo** e **quanto falta**. O Alfred sempre abre a resposta com um **cabeçalho de progresso** derivado do `state`:
- Sigla · id-demanda · Risk Mode · **modelo atual** (D46)
- Fase atual (X de 5) e etapa interna
- Barra/contador de progresso das 5 fases (✓ feito · ▶ atual · ◻ pendente)
- Próximo passo + próximo checkpoint HITL
- O que falta para concluir a fase atual

O **Orchestrator** é responsável por montar e exibir esse cabeçalho e por manter o checklist de progresso no `state`. Vale para todos os modos (em FAST, versão de 1 linha).

Exemplo (Standard):
```
ALFRED · SIGLA:PGTO · #142 "novo split de pagamento" · Modo: Standard
Fase 2/5 — Design  ▶   [✓ Inception] [▶ Design] [◻ Execution] [◻ Validate] [◻ Operation]
Etapa: gerando spec técnica (app: pgto-api)
Falta na fase: critérios de aceite + aprovação da spec (checkpoint: Tech Lead)
Próximo passo: revisar alternativas de roteamento
```
Exemplo (FAST, 1 linha):
```
ALFRED · SIGLA:PGTO · #143 · FAST · Execution (3/5) · falta: PR + merge
```

### Process Toolbar (visual) — Standard/SAFE
Bloco ASCII renderizado pelo Orchestrator no topo de cada interação. Substitui o "toolbar de evolução" (antes cortado). Mostra modo, % de progresso, trilha das 5 fases, etapa, checkpoint e próximo passo.
```
┌─ ALFRED ───────────────────────────────── SIGLA:PGTO · #142 ─┐
│ Modo: STANDARD            Progresso: ███████░░░░░░░░  45%      │
│                                                               │
│  ①Inception ✓ ── ②Design ▶ ── ③Execution ◻ ── ④Validate ◻ ── ⑤Operation ◻
│                                                               │
│ Etapa : gerando spec técnica (app: pgto-api)                  │
│ ⏸ HITL : aprovação da spec — Tech Lead                        │
│ → Next : revisar alternativas de roteamento                   │
└───────────────────────────────────────────────────────────────┘
```
Legenda dos marcadores: `✓` concluído · `▶` em andamento · `◻` pendente · `⏸` aguardando humano · `⚠` risco/bloqueio.
- **% de progresso** = fases concluídas + fração da fase atual (etapas internas marcadas no `state`).
- **Custo até agora** (D10): o toolbar mostra o custo acumulado de IA da demanda — `tokens` e `$ estimado` (e nº de interações). Atualizado pelo Metrics Agent a cada interação.
- **FAST**: usa só a linha única (não renderiza o bloco) para manter leveza — inclui o custo compacto.
- **Emergência (Execution-first)**: a trilha mostra Execution ▶ com Inception/Design marcados `⏳ pós` (pendentes de post-mortem).

Linha de custo no toolbar (exemplo):
```
Custo  : 312k tokens · ~US$ 4,80 · 18 interações
```

## D47 — Política de idioma
- **Interações com pessoas → pt-BR:** prompts, perguntas (requirements `[Answer]:`), toolbar (D9), mensagens/voz do mordomo (D17), checkpoints.
- **Arquivos do Framework → inglês:** `core/`, `rules/`, `agents/`, `skills/`, `connectors/`, `metrics/`, e os **templates** (o código-fonte do framework é EN — facilita reuso/contribuição).
- **Docs do usuário + artefatos gerados → pt-BR:** tudo que a squad lê/produz no **HUB/App** — `state`, `problem`, `tech-inception`, `requirements`, `spec`, `decisions`, `summary`, `audit` (legível), `metrics`/relatórios, email (D44), `docs/`.
- **Regra prática:** o template **mora em EN** (instruções/labels do framework), mas o Alfred **gera o conteúdo do artefato em pt-BR**. Termos técnicos consagrados podem permanecer em inglês.
- **Glossário (`core/glossary.md`):** mantém o de-para EN↔pt-BR dos termos do framework (sigla, lane, demand-type…) para consistência.

## D46 — Política de modelos por etapa (model routing)
O Alfred **define qual modelo usar por etapa** e pode **trocar durante a execução** (o Orchestrator escolhe por passo).
- **Política configurável** (`core/model-policy.md`): mapeia **fase/agente/lane/tipo** → preferência de modelo. Ex:
  - Design/arquitetura, SAFE, decisões → **modelo mais forte**.
  - FAST, refactor trivial, boilerplate → **modelo mais barato/rápido**.
  - Review/QA → **modelo intermediário**.
- **Regra de seleção (risco + etapa, não só etapa):** a chave é composta — **lane (risco/modo) + fase + agente + tipo**. O **risco (lane) impõe um PISO**: define o tier mínimo de modelo; a **fase/agente** ajusta **acima** do piso, **nunca abaixo**. Espelha o Risk Mode (risco define o piso — 2.1/2.3).
  - Ex: SAFE → piso "forte"; mesmo numa etapa trivial, não desce de forte.
  - Ex: FAST → piso baixo; Design pode subir o tier mesmo em FAST se a etapa pedir.
  - Conflito entre dimensões → **vence o mais alto** (segurança > economia), igual aos overrides duros (D22/2.3).
- **Quem aplica:** o **Orchestrator** seleciona o modelo no início de cada passo conforme a política (piso do risco + ajuste da etapa); pode mudar entre fases/units.
- **Dependência de host (D14):** a troca real exige que o host suporte seleção de modelo (Claude CLI, DEVIN, Copilot). **Agnóstico (D3):** se o host não permite trocar, usa o default e **registra qual modelo rodou** (D43) — a política vira recomendação.
- **Mecanismo: híbrido (declarado + sugestão automática).**
  - **Fonte de verdade = declarada** em `core/model-policy.md` — **cravada, versionada, transparente**: você sempre sabe qual modelo roda em cada etapa. É o que o Orchestrator obedece.
  - **Sugestão automática:** o Alfred analisa o `metrics` (modelo×custo×aceite-de-1ª, D43) e **propõe** ajustes na política (ex: "no Design, modelo X teve +20% de aceite por R$ menor"). **Não aplica sozinho.**
  - **Humano ratifica (D7/D41):** a mudança só entra se um humano aprovar — vira novo commit no `model-policy.md` (rastreável). Nunca troca silenciosa.
  - **Declarar a troca (transparência):** sempre que o modelo muda de uma etapa para outra, o Alfred **avisa a pessoa** (linha no toolbar/interação, em pt-BR — D47), ex: *"Mudando para <modelo> nesta etapa (Design/SAFE)."*. A troca também é evento no `audit` (D45).
  - **Escolha do usuário (override):** a pessoa pode **definir/trocar o modelo a qualquer momento** — pontual (uma etapa) ou fixo (a demanda toda). O Alfred respeita e registra no `state`/`audit`.
    - Se a escolha for **abaixo do piso de risco** (ex: modelo barato em SAFE), o Alfred **avisa o trade-off** (não bloqueia — humano no controle, D7) e registra a decisão. Subir o tier é livre.
  - **No toolbar:** mostra o **modelo atual** da etapa, para a pessoa saber sempre o que está rodando.
- **Formato declarado (exemplo `model-policy.md`):**
```markdown
## Piso por lane (risco) — não descer abaixo
| Lane     | Tier mínimo |
|----------|-------------|
| FAST     | <barato>    |
| Standard | <médio>     |
| SAFE     | <forte>     |

## Ajuste por etapa (sobe acima do piso, nunca abaixo)
| Fase/agente/tipo              | Ajuste            |
|-------------------------------|-------------------|
| Design · spec-design          | +1 tier (subir)   |
| Execution · boilerplate       | manter piso       |
| Validate · reviewer           | manter/＋1 se risco|
```
Resolução final = max(piso do risco, ajuste da etapa).
- **De-para tier → modelo real (por host, D14):** a política usa **tiers abstratos** (barato/médio/forte); este mapa traduz para o modelo concreto de cada host — é o principal ponto de customização. Se o host não tem o tier, usa o fallback (D3).
- **Tier OU modelo concreto (as duas formas):** qualquer célula da política pode ser **um tier** (`cheap/medium/strong`, portável entre hosts) **ou um modelo fixo** (ex: `claude-opus-4-8`, quando você quer cravar). Se for modelo fixo, o Alfred deriva o tier dele (de-para reverso) só para checar o **piso de risco**: se o modelo cravado ficar **abaixo do piso**, avisa o trade-off (não bloqueia — D7), como no override do usuário.

## D45 — Telemetria contínua (durante as fases, não só no fim)
A medição é **contínua**: cada passo/fase/checkpoint **emite um evento**, não só o fechamento.
- **Quando captura:** a cada interação relevante — transição de fase, passo/unit, checkpoint, decisão, pausa, escalonamento (mesma cadência da persistência D37).
- **O que cada evento registra:** timestamp · ator (humano/agente) · fase · modo · **modelo usado** · tokens/custo · status · **"onde parou"** (próximo passo).
- **Onde:** append no `audit` (rastro) + atualização do `metrics` da demanda; o `state` já guarda **última atividade + progresso** (D28/D9) = a foto de "onde parou agora". O evento dá a **linha do tempo**.
- **Para que serve (a sua pergunta):** saber **se a pessoa está usando**, **em que fase parou**, tempo por fase, retomadas, adoção — em tempo real, por demanda e no **rollup** (sigla/org, D43).
- **Cadência:** captura **contínua** (todo evento → audit/metrics), mas **email só em pontos estratégicos** (D44: conclusão, checkpoint crítico, escalonamento, incidente) — nunca por interação. Dashboards (futuro) leem o fluxo de eventos.
- **Agnóstico (D3):** evento = linha markdown no audit/metrics; enriquecimento automático (tokens/modelo) é camada opcional — sem ela, captura o essencial (fase/status/tempo) manual/aprox.
- **Entrega via API (evolução futura):** haverá uma **API para o Alfred enviar os logs/eventos** a um backend central de observabilidade. Entra como **connector `telemetry`** (`enviar_eventos(lote)`), plugável (D40) — quando existir, é só o adapter; até lá, os eventos ficam no `audit`/`metrics` (markdown) e/ou vão por email (D44). Sem reescrever regras.

## D44 — Destino da saída + notificação por email
**Destino da saída (recap D8 — versionado nos repos, não no local de quem executa):**
- **App (`.alfred/`):** artefatos técnicos do repo (spec técnica, investigation, audit técnico, **métricas técnicas** do app).
- **HUB:** consolidado/fonte de verdade (state, decisions, **metrics consolidadas + rollup/insights** D43, summary).
- Quem executa (DEVIN/pessoa) **commita na branch da demanda** (D23/D37); nada fica só local.

**Notificação por email (artefatos + logs):**
- **NÃO é a cada interação** (isso é telemetria contínua, D45, que fica no audit/metrics). O email ocorre **só em pontos estratégicos** que façam sentido:
  - **Demanda concluída** (Operation) — relatório final.
  - **Checkpoint crítico** que precisa de ação humana (aprovação de spec/arquitetura, aceite).
  - **Escalonamento/risco** (gatilho D27, mudança de Risk Mode, bloqueio).
  - **Incidente** declarado e estabilizado (D34).
  - (Opcional) **resumo periódico** de status, se a sigla quiser.
- Os pontos são **configuráveis** no `knowledge` (a sigla escolhe quais disparam email) — default enxuto para evitar ruído.
- **Envio transparente (autorização durável):** destino + pontos são aprovados **uma vez** na config (`knowledge`); depois o Alfred **envia automaticamente** nesses pontos, **sem perguntar a cada vez** — o usuário não precisa ser interrompido. A **transparência vem do registro no `audit`** (o quê/para quem/quando), não de um prompt.
- **Salvaguarda (D41/D7):** o auto-envio vale **só** para o destino e os pontos já configurados. Se algo **foge da config** (destino novo, conteúdo fora do padrão, dado sensível inesperado), o Alfred **para e pergunta**. Mudar destino/gatilhos = alteração de config (humano).
- **Endereço vem do `knowledge`** (org/sigla, D42), não hardcoded.
- **Autorização durável (transparente):** a aprovação é dada **na config** (destino + pontos no `knowledge`), não a cada envio. Nos pontos configurados, envia **automaticamente e transparente** (sem interromper o usuário); registra no `audit`. Só pede confirmação se **fugir da config** (D41).
- **Connector `notification` (D40):** `enviar(destino, assunto, anexos)`. **Sem connector/acesso → o Alfred lembra o humano de enviar manualmente** (degrada, D3).
- O envio é registrado no `audit` (o quê, para quem, quando).

**Configuração (estruturada; canal a definir):**
- **Destino registrado:** `adriano.vilela-costa@itau-unibanco.com.br` (no `knowledge` org — `knowledge/notification.md`).
- **Conteúdo:** métricas (`metrics`/rollup, D43) + logs (`audit`) + artefatos da demanda.
- **Gatilho:** fechamento da demanda (Operation), com confirmação humana.
- **Canal:** `<A DEFINIR>` — SMTP interno · Microsoft Graph/Outlook · AWS SES · MCP de email. O **adapter é plugável** (DIP/Open-Closed, D40): definir o canal preenche só o `connectors/notification-email.md`, sem tocar regras.
- **Enquanto o canal não existe:** degrada para **lembrete manual** (D3) — o Alfred avisa "envie X para o email" e registra no audit.

**Padrão do email (template `templates/email.md`):**
- **Assunto (fixo):** `[Alfred-Framework][<SIGLA>][<id-demanda>] <evento> — <título curto>`
  - `<evento>` = `Demanda concluída` · `Checkpoint <fase>` · `Incidente` · `Status` (conforme gatilho).
  - Ex: `[Alfred-Framework][PGTO][PGTO-142] Demanda concluída — novo split de pagamento`
- **Corpo (curto — só resumo + ponteiros; NÃO colar conteúdo de arquivo):**
  1. **Cabeçalho:** sigla · iniciativa · id · stream/tipo · **modo** · fase · responsável · data · versão framework (D26).
  2. **Resumo:** o `summary` (D11) — o que foi feito/evoluiu (poucas linhas).
  3. **Destaques de métricas & custo (D43):** modelos · tokens/$ · lead time · aceite de 1ª (números-chave, não a tabela inteira).
  4. **Ponteiros:** links para `state`/PR no repo (referência rápida).
  5. **Pendências/débitos** e próximos passos.
- **Anexos (os arquivos vão ANEXADOS, não no corpo):** `metrics.md` · `audit.md` (logs) · artefatos relevantes da demanda (ex: `summary.md`). Logs/métricas **sempre como anexo**.
- Assunto **sempre** começa com `[Alfred-Framework]` (filtro/rastreio no inbox).

## D43 — Observabilidade e insights do Alfred (auto-medição)
O Alfred **gera métricas e observabilidade da própria operação** para medir eficiência (Alfred medindo o Alfred). Estende D10 (custo) + D32 (baselines).
- **O que captura (por demanda → agente/fase):**
  - **Modelos usados** (id do modelo por agente/fase — DEVIN/Claude/Copilot, D14), nº de interações.
  - **Custo:** tokens in/out · $ estimado · custo por modelo/fase/agente/modo.
  - **Eficiência:** lead time, retrabalho (ciclos até aceite), aceite de primeira, reclassificações de modo, % de tempo aguardando humano.
  - **Qualidade:** defeitos pós-release, % de saída da IA aproveitada por agente.
- **Agregação (rollup):** demanda → iniciativa → sigla → org. Cada nível soma os insights.
- **Insights típicos:** mix de modelos (%), custo por modelo/modo/stream, tendência temporal, distribuição FAST/Std/SAFE (cruza baselines D32), eficiência por agente.
- **Onde:** `metrics` por demanda (HUB) + agregação no nível da sigla (`metrics/` do HUB ou `context`); definição/insights no Framework (`metrics/`).
- **Agnóstico (D3):** os dados são markdown; **coleta automática** (tokens/$/modelo) é camada opcional via host/connector — sem ela, fica aproximado/manual, nunca bloqueia.
- **Captura contínua (D45):** os dados são coletados **durante as fases** (eventos por passo/checkpoint), não só no fechamento — permite ver uso/onde parou em tempo real.
- **Dashboards = evolução futura;** o **dado** é capturado desde já. O Metrics Agent (D-5) produz; o humano decide ações (D7).

## D42 — Base de conhecimento / políticas (guardrails) — distinta de skill
Há um terceiro tipo de conteúdo além de skill (capacidade) e connector (acesso): **base de conhecimento = políticas/fatos sempre em vigor** (guardrails). Ex: "criar repo só via ISSUE", regras de acesso, naming, ambientes, fluxos de aprovação internos.
- **Skill ≠ KB:** skill é *capacidade que se aplica* (opt-in, JIT); KB é *restrição/fato que se respeita* (sempre em vigor no escopo, hard constraint).
- **3 escopos:**
  - **Org/empresa** → `knowledge/` no **Framework** (camada org, preenchida na adoção — D15; o framework é entregue agnóstico/vazio aqui).
  - **Sigla/sistema** → `knowledge/` no **HUB** da sigla.
  - **Squad** → também no HUB (a squad é dona do HUB). **Sim, a squad cria a KB do seu Alfred no HUB.**
- **Precedência (guardrail):** org é **mandatória**; sigla/squad podem **adicionar/endurecer**, nunca **relaxar** o que a org define. Conflito → escala para humano/governança (D7/D41).
- **Carregamento:** indexada (D11), carregada **por tema** quando relevante, mas as políticas do escopo são **always-in-force** (não opt-in). Entram como restrição dura nas decisões dos agentes.
- **Liga à lei suprema (D41):** se uma política impede uma ação (ex: criar repo), o agente **não burla** — segue a política (abre ISSUE via connector/tracker) ou **para e pergunta**. Nunca inventa um caminho.
- **Formato:** markdown enxuto, 1 política por bloco, referenciada pelo índice; cresce por adição (Open/Closed, D40).

## D41 — Política anti-alucinação: não inventar, na dúvida parar e perguntar (lei suprema)
Regra **inegociável**, acima de tudo (vale em todos os modos, inclusive FAST — sobrepõe autonomia):
- **Não inventar nada:** fatos, requisitos, decisões, APIs, contratos, caminhos de arquivo, dados, nomes — **se não souber ou não puder verificar, não cria**.
- **Não decidir sozinho** sobre nada material — decisão é humana (D7). A IA propõe; o humano resolve.
- **Na dúvida, PARE e PERGUNTE** (gate). Não adivinhar, não "preencher lacuna". Dúvida **rebaixa** a autonomia do FAST → escala para humano (liga D27).
- **Fundamentar antes de afirmar:** toda afirmação sobre o código/sistema vem de fonte verificável — `reverse-eng` (S1/D21), connectors (D40), artefatos. **Verificar existência** de arquivo/função/flag antes de usar.
- **Marcar o incerto:** o que não é fundamentado vai como **"inferido / a confirmar"** (D31), nunca como fato. Suposição explícita > invenção silenciosa.
- **Sem fonte → sem ação:** se falta contexto/credencial/log (ex: incidente sem acesso ao connector, D34), pedir ao humano em vez de supor.
- **Enforcement:** materializada em `rules/common/overconfidence.md` (herdada do AI-DLC) + reforçada na persona (D17: o mordomo pergunta, não presume) e nos limites de cada agente (4.x "Não faz").
Resumo: **é melhor parar e perguntar do que avançar errado.** Esta política protege contra o maior risco de um framework com IA — alucinar com confiança.

## D40 — SOLID aplicado à arquitetura do Alfred
A arquitetura do próprio Alfred segue SOLID:
- **S (Single Responsibility):** 1 razão de mudar por módulo (`core`/`rules`/`skills`/`connectors`/`metrics`) e por artefato (`state`≠`decisions`≠`audit`≠`metrics`); cada agente dona de 1 fase; "~1 tela, split quando cresce" (D11).
- **O (Open/Closed):** estende-se **adicionando** (skill, connector, demand-type, lane) **sem tocar o core**. `skills/`, `connectors/`, `demand-types/`, `lanes/` são pontos de extensão.
- **L (Liskov):** membros de uma família são substituíveis: lanes (fast/standard/safe), connectors (cloudwatch↔datadog), hosts (DEVIN↔Claude↔Copilot, D14). Exige que o consumidor dependa do **papel**, não do concreto.
- **I (Interface Segregation):** cada consumidor carrega **só o necessário** = JIT/índice em cascata (D11). Nenhum agente vê o catálogo inteiro.
- **D (Dependency Inversion):** alto nível depende de **abstração**: `lifecycle` pede "uma lane"/"um connector de observability", não FAST/CloudWatch; agentes comunicam pelo **`state`** (barramento), não entre si.
**Refinamento exigido por L+D — contratos:** cada família plugável declara um **contrato** no seu registry:
- `connectors.md` — contrato por tipo (ex: observability: `get_logs(query)→entradas`; vcs: `branch/commit/PR`; tracker: `get_demand(id)`).
- `skills.md` — contrato da skill (gatilho, entradas, saída esperada).
- `agents/*` — contrato de I/O via `state` (lê/escreve).
- `lanes/*` — contrato uniforme: DoD + checkpoints + artefatos por modo (D25).
Regra: **as regras (`demand-types`, `lifecycle`) referenciam o contrato/papel, nunca o concreto** — trocar CloudWatch por Datadog é trocar o connector, sem tocar a regra.

## D39 — Layout modular do repo do Framework (variante C — sem prefixo)
Escolhido: modular por responsabilidade, **sem prefixo** (o repo já é `alfred/`). Repo dedicado ao framework.
- **`core/`** — kernel/entrada: README, welcome (D17), boot (D16), principles, risk-mode (seletor), architecture, glossary.
- **`rules/`** — o **AI-DLC customizado = motor** (D1/D38), agnóstico (sem AWS, A.3):
  - `common/` — question-format (D18), content-validation, overconfidence (S1), session-continuity, terminology.
  - `demand-types/` — **streams × tipos** (D5/3.6): produto, operacional (inc. incidente/Execution-first D6/D34), engineering.
  - `lanes/` — **modos do Risk Mode** (governança): fast, standard, safe (DoD D25, checkpoints).
  - `lifecycle/` — passos por **fase** (D19/D38), carregados JIT: inception, design, execution, validation, operations.
  - `agents/` — orchestrator, discovery, spec-design, reviewer, metrics (D2).
- **`skills/`** — capacidades plugáveis, opt-in/JIT (D12/D22/D36): registro + coding-standard (SOLID) + lang-* + externas (ponteiros).
- **`connectors/`** — **acesso a sistemas externos** (opcional, D3/D14): observability (CloudWatch p/ D34), git (D23), tracker (D20). Connector = *acesso*; skill = *conhecimento* (distinção dura).
- **`metrics/`** — definição de métricas (D10) + baselines tunáveis (D32).
- **`templates/`** — moldes hub/ + app/ (5.3).
- **`scripts/`** — automação **opcional** (D3 — tudo degrada para manual; nada obrigatório).
- **`docs/`** — documentação humana. **`examples/`** — sigla/iniciativa/demanda de exemplo (onboarding D30, piloto).
- **Dois eixos explícitos:** `demand-types` (caminho, por stream) × `lanes` (governança, por modo) — ortogonais; uma demanda combina um de cada.
- **Nota:** nomes genéricos assumem **repo dedicado**; se um dia o framework for misturado a outro conteúdo, reavaliar prefixo.

## D38 — O AI-DLC customizado mora dentro do Framework (motor)
Como Alfred = AI-DLC customizado (D1), o **motor adaptado fica no repo do Framework**, em **`rules/`** (layout D39) — é o AI-DLC de `D:\Projetos\aidlc-workflows` já passado pelo diff do Apêndice A (reaproveitar/adaptar/cortar).
- **`rules/common/`** — regras comuns: `question-format` (D18), `content-validation` (leve), `overconfidence-prevention` (S1), `session-continuity`, `terminology`.
- **`rules/lifecycle/<fase>/`** — passos operacionais por fase: inception, design, execution, validation, operations (requirements, Planning+Generation, build-and-test etc., já customizados — D19).
- **`rules/demand-types/` e `rules/lanes/`** — os dois eixos (stream × modo) que modulam o motor.
- **Relação com o resto:** `core/risk-mode.md` e `core/principles.md` são a camada distintiva do Alfred **sobre** o motor; o motor é carregado JIT (só a fase/regra ativa — D11).
- **Sem AWS (A.3):** conteúdo AWS-específico não entra — vira skill/connector opcional (D34). Motor agnóstico (D3).
- **Versão (D26):** o carimbo de versão no `state` cobre motor + camada Alfred juntos.

## D37 — Granularidade de persistência do state (garante a retomada)
A retomada sem recomeçar depende de gravar o `state` com frequência suficiente. Regra:
- **Gravar o `state` (e o que mudou):** ao concluir **cada unit/passo**, em **cada transição de fase**, em **cada checkpoint HITL**, a cada **decisão** e ao **pausar**. Nunca acumular muito trabalho sem persistir.
- **Commitar na branch da demanda (D23):** os artefatos do HUB/app precisam ser **commitados** para sobreviver entre sessões/máquinas/pessoas. Recomendação: commit ao fim de cada passo significativo (não só no fim).
- **Granularidade de perda:** se a sessão cair, retoma-se do último `state` gravado — perde-se no máximo o passo em andamento, nunca a demanda.
- **Conteúdo mínimo p/ retomar:** o `state` sempre tem fase, modo, progresso, próximo passo e links — suficiente para o boot (D16) reconstruir o contexto sem reler tudo (D11).
- **Verificação:** critério de aceite do Alfred (8.3) inclui "retomar após perder contexto lendo só o `state`".

## D36 — Padrão de codificação (SOLID) com override por skill de linguagem
O Alfred codifica seguindo um **padrão baseado em SOLID**, com precedência:
- **Base:** skill interna `skills/coding-standard` (SOLID + boas práticas gerais, agnóstica de linguagem).
- **Override:** se houver **skill da linguagem** ativa que **define SOLID/padrões** (ex: `skills/lang-java`, `skills/lang-python`), **usa a da skill** — mais específico vence (precedência D22).
- **Aplicação:** o agente de Execution gera/modifica código conforme o padrão efetivo; o **Reviewer** valida o código contra esse mesmo padrão (na Validate).
- **Complementaridade:** SOLID/padrão = **princípios**; template (D35) = **estrutura concreta** a espelhar; reverse-eng = estado atual. Os três se somam sem conflito.
- **Agnóstico (D3):** tudo é skill markdown/ponteiro; sem skill de linguagem, vale o coding-standard base. Carregado JIT (só as seções relevantes).

## D35 — Repos de template/referência (espelhar o padrão da casa)
A squad pode ter **repos de template** (boilerplate, scaffold, padrões de estrutura/convenções). O Alfred **pergunta se existem** e os usa como espelho no desenvolvimento, para o código gerado seguir o padrão.
- **Quando perguntar:**
  1. No **onboarding da sigla** (D30): "Há repos de template/referência para este sistema/stack?".
  2. No **Design** de uma demanda: confirmar qual template se aplica (pode haver mais de um — API, front, lib).
- **Registro:** no `context.md` da sigla (lista de templates + para que serve cada um) e, se específico, no `index`/app. É **ponteiro** (não cópia) — agnóstico (D3), JIT (D11).
- **Uso:** em Design/Execution, o agente carrega **só as seções relevantes** do template (estrutura de pastas, convenções, exemplos) e **espelha** ao gerar/modificar código. Combina com reverse-eng (S1): template = alvo/padrão; reverse-eng = estado atual.
- **Distinção:** template ≠ skill. Skill é capacidade/conhecimento; template é **código concreto a espelhar**. Ambos plugáveis e referenciados.
- **Sem template:** o Alfred segue as convenções inferidas do próprio repo (reverse-eng) e registra que não havia template.

## D34 — Investigação exploratória de incidente (via skill)
Incidente (Operacional emergência) entra com **número + descrição** e exige análise exploratória **antes** de estabilizar (você precisa achar o problema para corrigir).
- **Entrada:** nº do incidente + descrição.
- **Investigação exploratória:**
  1. Busca em observabilidade — **se AWS, CloudWatch da conta** (logs/alarms/métricas) → varre para localizar o erro/stack trace.
  2. **Mapeia erro → repos** afetados (cruza com a lista de apps da sigla + reverse-eng S1).
  3. Abre os códigos suspeitos e produz **análise detalhada da causa provável** (`investigation.md`).
- **Agnóstico (D3, crítico):** o acesso a CloudWatch/AWS é **skill plugável** (D12), não core — `skills/incident-aws-cloudwatch`. A *capacidade* é "investigação de logs/observabilidade"; outras stacks (Datadog, GCP, ELK) são outras skills. **Sem a skill/acesso, o humano fornece os logs** e o Alfred segue a análise.
- **Ordem (concilia com D6):** a investigação exploratória é a primeira etapa do Execution-first — *triagem* rápida que localiza o problema; estabilização vem logo após, com autorização mínima do on-call.
- **Alimenta:** a estabilização (o que corrigir/reverter) e o **post-mortem** (causa raiz já documentada na `investigation`).
- **Carimbo/custo:** a varredura conta no custo (D10) e registra no `audit` o que foi consultado.

## D33 — Inception em duas lentes (negócio importada × técnica)
A Inception tem **duas lentes**: **negócio** (o quê/por quê) e **técnica** (como será entendido em tecnologia: o que é afetado, restrições, riscos técnicos).
- **Produto:** a lente de **negócio normalmente chega pronta de um agente externo** (problem statement, objetivo, escopo, stories, requisitos de negócio). O Alfred **não refaz** esse discovery — ele:
  1. **Ingere** os artefatos externos (guarda/linka como entrada — `inception-input`);
  2. **Valida completude** (se falta algo de negócio, pergunta ao humano/origem — não inventa);
  3. **Aplica a Inception técnica** (lente do Alfred): sistemas/apps afetados (cruza com reverse-eng S1), pontos de integração, restrições e riscos técnicos, viabilidade, **perguntas técnicas** (gate D18) — produz `tech-inception`.
- **Engineering/Operacional:** normalmente originadas internamente/tecnicamente — a lente de negócio é mínima e o Alfred faz as duas (ou só a técnica).
- **Alimenta:** a Inception técnica + a importada alimentam o Risk Mode (D31) e o Design.
- **Artefato:** `inception-input` (importado, quando houver) + `tech-inception` (visão técnica do Alfred). Em FAST, inline; Std/SAFE, arquivo.
- **Princípio:** o Alfred agrega **compreensão de tecnologia** sobre uma intenção de negócio já definida — sem duplicar o trabalho do agente externo.

## D32 — Baselines de métricas (régua tunável, não regra dura)
As métricas (D10) só ajudam se houver régua. Defaults **sugeridos e ajustáveis por squad** (ficam no `context.md` da sigla):
| Sinal | Baseline sugerido | O que indica / ação |
|---|---|---|
| **% SAFE** numa janela (ex: 20 demandas) | > ~25% | medo, não risco → revisar critérios (trava anti-SAFE, 2.3) |
| **% FAST** | > ~70% **com** reclassificações frequentes | classificação leve demais → revisar checklist |
| **Reclassificações/demanda** | > 1 em média | intent analysis fraco (D18/D31) → melhorar perguntas |
| **Retrabalho** (ciclos de revisão até aceite) | > 2–3 | spec/clareza insuficiente (SDD/D29) |
| **Aceite de primeira** | < ~60% | qualidade de saída da IA caindo → revisar agentes/skills |
| **Custo/demanda vs. teto do modo** | acima do teto | dispara gatilho de escalonamento (D27) |
Regras:
- São **defaults**, não gates rígidos — cada squad calibra. O objetivo é **conversa**, não punição.
- O Metrics Agent sinaliza desvios no fechamento (summary) e em revisão periódica; **quem decide agir é o humano** (D7).
- Sem tooling de coleta, ficam aproximados (D3) — a régua continua útil como referência qualitativa.

## D31 — Mapeamento intent analysis → Risk Mode
As respostas do intent analysis (D18) **pré-preenchem** o checklist de Risk Mode (2.2); o humano só confirma/ajusta. Correspondência:
| Saída do intent (D18) | Alimenta no checklist (2.2) |
|---|---|
| **Escopo** (1 arquivo → cross-system) | Componentes afetados + Blast radius |
| **Complexidade** (trivial → complexo) | Novidade técnica + Esforço estimado |
| **Clareza** (clara/vaga/incompleta) | Ambiguidade do requisito |
| **Tipo/stream** (D5) | Dicas de override: Engineering=migração/arquitetura→SAFE; Operacional crítico→eixo de tempo (2.4) |
| **Integrações citadas** nas respostas | Integrações |
| **Dados/cliente** citados nas respostas | Dados sensíveis/regulado + Impacto em cliente (gatilham overrides duros 2.3) |
Regras:
- A IA preenche o que as respostas permitem e **marca como "inferido"** os campos não cobertos (pede confirmação).
- O resultado é o **modo proposto** (D2.10: IA propõe, humano confirma).
- Campos de risco alto (dados/irreversível/cliente) **nunca** são auto-confirmados em FAST — sempre sobem para revisão humana (liga D27).

## D30 — Onboarding de uma sigla (primeiro uso)
Fluxo repetível para adotar o Alfred num sistema novo (uma vez por sigla):
1. **Referenciar o framework** (D15) — apontar para o repo do Alfred (sem copiar).
2. **Criar o HUB da sigla** — `context.md` (descrição do sistema + **lista dos repos de app** + **repos de template/referência**, D35), `index.md` vazio, `skills.md` (ativar skills relevantes ao sistema). **Perguntar:** "Há repos de template para o Alfred espelhar?" (D35).
3. **Inicializar `.alfred/` em cada app** da sigla + **engenharia reversa pesada** (S1/D21) — maior custo de entrada (brownfield); fica cacheado com carimbo de commit.
4. **Registrar apps↔sigla** no `context.md`/`index`.
5. Pronto para a **primeira demanda**.
- **Custo concentrado no onboarding:** o reverse-eng pesado roda uma vez; demandas seguintes só revalidam se o app mudou (D21). Pode ser paralelizado por app (D13).
- **Mordomo (D17):** conduz o onboarding como setup guiado ("Vamos preparar a casa: quais repos pertencem a esta sigla?").

## D29 — SDD como trava de clareza (invariante, não mecanismo novo)
SDD é pilar da base, mas sua força é **negativa**: *nenhuma Execution relevante começa sem clareza mínima.* Não cria mecanismo novo — **consolida** os existentes:
- **A trava:** o agente **não entra em Execution** sem o DoD de Design do modo (D25) satisfeito. Em Standard/SAFE isso significa spec + critérios de aceite + decisões; em FAST, basta o problema/abordagem claros (a "spec" é o PR).
- **De onde vem a clareza:** requirements respondidos no gate da Inception (D18) + spec no Design (template 5.3.2).
- **O que o SDD impede (as dores):** IA codar sem entender; começar sem critério de aceite; decisão não registrada.
- **Escala por modo:** a profundidade da spec é regulada pelo Risk Mode (não é "spec gigante para tudo") — FAST quase inline, SAFE completa.
- **Exceção controlada:** emergência (D6) inverte a ordem (Execution-first), mas a clareza não é dispensada — é **adiada** (spec retroativa no post-mortem). SDD adiado ≠ SDD pulado.
Resumo: SDD = o "freio de clareza" que o Risk Mode dosa e o DoD aplica.

## D28 — Estados da demanda e retomada (pausar é normal)
Pausar uma demanda e retomá-la depois é **fluxo normal** — a pessoa pode tocar várias em paralelo. O Alfred **nunca** declara abandono por inatividade.
- **Estados do `state`:** `em andamento` · `em espera` (pausada — 1ª classe, retomável a qualquer momento) · `bloqueada` (depende de externo) · `aguardando checkpoint` · `concluída` · `cancelada` (só por decisão humana explícita).
- **Multi-demanda do mesmo humano:** várias podem estar `em andamento`/`em espera` ao mesmo tempo. O `id` + `state` por demanda mantêm cada uma isolada e retomável.
- **Nada é esquecido:** no boot (D16), o Alfred **lista as demandas abertas da sigla** (em andamento/em espera/bloqueada) com última atividade — o "welcome back" do mordomo (D17): *"Há 2 demandas em espera: #142 (Design) e #097 (Execution). Retomar alguma?"*.
- **`última atividade`** (data) no `state` ajuda a notar demandas paradas há muito — **mas quem decide** cancelar/retomar é o humano (D7). Sem auto-cancelamento.
- **Cancelar (explícito):** gera mini-`summary` (por quê) + atualiza `index` (sai dos ativos) — só aí arquiva. Pausar **não** arquiva.

## D27 — Gatilhos de escalonamento (limite da autonomia)
Em FAST (autonomia delegada), a IA **deve parar e chamar o humano** ao detectar qualquer um destes — torna o D7 aplicável na prática:
1. **Escopo cresceu** além do pedido original (surgiu requisito novo).
2. **Risco subiu** — descobriu que toca dados sensíveis, ação irreversível ou impacto direto em cliente → dispara reclassificação (2.8).
3. **Custo passou do teto** definido (D10).
4. **Operação destrutiva/irreversível** — apagar dados, `drop`, migração de schema, `force push`, mexer em produção.
5. **Segurança/credenciais** envolvidas.
6. **Ambiguidade que a IA não resolve** sozinha.
7. **Efeito cross-app** não previsto (toca outra app/sigla).
8. **Falha repetida** — testes/abordagem falhando após N tentativas: não entrar em loop; parar e reportar.
Ao disparar: a IA **pausa, registra no `state`/`audit`** e apresenta ao humano (vira checkpoint). Vale como piso em todos os modos; em Standard/SAFE os checkpoints já são explícitos.

## D26 — Carimbo de versão (rastreabilidade)
Três carimbos de versão coerentes, todos registrados:
- **Framework:** versão/commit do Alfred sob o qual a demanda rodou → campo no `state` (carimbado no boot, D16; congelado na demanda até concluir, D15/D16).
- **App:** commit/versão do app no `reverse-eng` e no PR (D21).
- **Demanda:** o próprio `id` + branch (D20/D23).
Resultado: dá para reconstruir "esta demanda foi feita com Alfred vX, sobre o app no commit Y". O `audit` referencia esses carimbos; nenhum exige tooling (D3) — são linhas no markdown.

## D25 — Definition of Done por fase × modo (gate de avanço)
Cada fase só avança quando seu DoD está satisfeito. Itens **acumulam** por modo (SAFE inclui Standard, que inclui FAST).

| Fase | FAST | Standard (+ FAST) | SAFE (+ Standard) |
|---|---|---|---|
| **Inception** | problema + objetivo claros; Risk Mode proposto | requirements respondidos (gate D18); escopo/fora-de-escopo; riscos iniciais | stakeholders; análise de risco; modo confirmado por papel |
| **Design** | abordagem clara (inline) | spec + critérios de aceite + decisões; plano de execução; modo revalidado | alternativas; dependências; rollout/rollback; arquitetura aprovada (Tech Lead) |
| **Execution** | PR pequeno; auto-revisão; audit enxuto | revisão técnica ok; units [x] (D24); sem escopo novo não aprovado; testes durante | gestão de dependências; aprovações de papel; evidências |
| **Validate** | testes locais passam | critérios de aceite ✓; regressão; **PR pronto p/ merge** (D23) | suíte completa; evidências formais; sign-off; segurança |
| **Operation** | merge feito; nota opcional | release notes; métricas básicas; `summary` + `index` (D11) | monitoramento; rollback ativo; post-mortem (se emergência) |

Regras: o agente **não declara a fase concluída** sem o DoD do modo; o item faltante aparece no toolbar ("falta na fase…", D9). DoD é checklist no `state`, não documento à parte.

## D24 — Demanda × Units of work (decomposição de execução)
- **A demanda é a unidade de governança:** 1 `state`, 1 Risk Mode base, checkpoints, aceite/merge. (override de risco continua por app — 2.11.)
- **No Design, a demanda pode ser decomposta em N units** (herdado de units-generation): partes menores e mais isoladas. **Cada unit é menos complexa** → executada com **profundidade/esforço menor** (depth-levels) e, se independentes, **em paralelo** (D13).
- **Units NÃO criam state próprio:** são **itens de checklist no plano de execução** dentro do `state` da demanda → alimentam progresso e toolbar (D9), com rastro unit→PR/arquivos.
- **Quando decompor:** demanda que toca múltiplos componentes/apps ou tem partes independentes. Senão, demanda sem units (FAST/simples).
- **Aceite continua na demanda:** units são concluídas internamente; o merge/aceite é da demanda como um todo (D23).

## D23 — Modelo de branch/merge e concorrência (branches protegidas)
Restrição real: `develop`/`main` são **protegidas**; o agente (DEVIN/Alfred) **não faz merge** nelas. O modelo se apoia nisso:
- **Branch por demanda/pessoa** (ex: `alfred/<id-demanda>` ou `alfred/<pessoa>/<id-demanda>`). O agente commita **só na branch da demanda** — nunca em develop/main.
- **Merge para develop = via PR aprovado por humano.** Esse merge **é o checkpoint HITL de aceite** (Validate) — a branch protegida *força* a aprovação humana (garantia técnica do D7).
- **Vale para HUB e apps** (os dois são repos versionados com o mesmo fluxo).
- **Concorrência:**
  - Artefatos **por demanda** (pasta isolada) → não conflitam entre demandas paralelas.
  - Arquivos **compartilhados da sigla** (`index`, `skills`, `context`, `initiative`): edits **pequenos e em seções distintas** (append/seção por iniciativa-demanda) para minimizar conflito; o que conflitar é resolvido **no PR, por humano**. O Orchestrator lê fresh (pull) antes de escrever.
- **Framework (D16):** é só leitura (pull/clone); não entra no fluxo de merge das demandas.
- **Resolvido (ver `connectors/git.md`):** promoção é `branch da demanda → develop` (PR = aceite, branch protegida força aprovação humana) → `main` (promoção de release na Operation, humana, fora do ciclo da demanda; IA nunca mergeia protegida). HUB e App usam o mesmo fluxo branch-por-demanda + PR; proteção do HUB pode ser mais leve (markdown, não código de produção), com garantia mínima de review humano em arquivos compartilhados (`index`, `initiative`, `skills`, knowledge).

## D20 — Identidade da demanda (`id-demanda`)
- **Herda do tracker existente** (issue/ticket) — não cria id paralelo. Formato: `<SIGLA>-<numero>` (ex: `PGTO-142`).
- Sem tracker → sequencial por sigla no HUB (`<SIGLA>-0001`).
- O mesmo `id` correlaciona HUB ↔ `.alfred/<id>/` nas apps (D8).

## D21 — Staleness da engenharia reversa
- O `reverse-eng` de cada app registra **o commit/versão do app analisado** + data.
- Ao iniciar demanda brownfield, o Alfred **compara o commit atual com o registrado**; se divergiu (ou tocou áreas relevantes à demanda), **revalida (incremental)** antes de agir — princípio "só mexer com certeza" (S1).
- Sem divergência → reusa o reverse-eng existente (JIT, sem reprocessar). Evita custo desnecessário (D10).

## D22 — Precedência entre skills em conflito
Quando duas skills se contradizem, a ordem é:
1. **Mais restritivo/seguro vence** (skill de segurança/risco prevalece sobre conveniência).
2. **Mais específica > genérica** (skill da app/sigla sobrepõe a do framework).
3. **Empate → humano decide** (checkpoint), registrado em `decisions`.
A skill ativa e o motivo da precedência vão para o `audit`.

## D19 — Herança do AI-DLC por fase (mapa)
Cada fase do Alfred reusa um conceito do AI-DLC customizado:
- **Depth-levels → Risk Mode.** "Quando a fase executa, cria seus artefatos; o *detalhe* adapta à complexidade." No Alfred isso é o Risk Mode regulando profundidade (não pular fase — D1.4). Princípio herdado: *"exatamente o detalhe necessário — nem mais, nem menos."*
- **Conditional stages → sub-atividades de Design/Execution.** O que no AI-DLC são stages (application-design, units-generation, functional-design, NFR, infrastructure-design) viram **sub-atividades opcionais dentro de Design** (não fases novas — respeita o ciclo de 5). Executam por gatilho (novo componente? dados? integração?) e por modo.
- **Workflow-planning → plano de execução (Design).** Análise de impacto, skip/execute com justificativa, sequência e **paralelização** (liga ao D13), risco. Sai no plano de execução da spec.
- **Two-part Planning+Generation → Execution.** Plano numerado com checkboxes (fonte única) → geração passo a passo marcando [x]; brownfield modifica in-place (nunca `arquivo_v2`); rastro story→código.
- **Build-and-test → Validate.** Estratégia de testes por necessidade (unit/integração/performance/e2e/contrato/segurança) + summary + gate.
- **Completion message → checkpoint HITL padronizado.** Toda transição relevante usa o padrão de 2 opções: **"Request Changes" / "Approve & Continue"** (sem menus emergentes). Em FAST, implícito; em Standard/SAFE, explícito.
- **Two-level checkbox → progresso (D9).** Checkbox no plano (detalhe) + no `state` (fase) — alimenta o toolbar.
- **Operations (placeholder no AI-DLC) → Operation real.** Alfred preenche o que o AI-DLC deixou em aberto (release, métricas, summary/D11, post-mortem).
Detalhe nas fases 3.2–3.5.

## D18 — Inception orientada a requirements (formato AI-DLC)
A Inception adota o mecanismo de requirements do AI-DLC (customizado):
1. **Intent analysis:** classifica clareza (clara/vaga/incompleta), tipo (mapeado aos streams D5), escopo (1 arquivo → cross-app) e complexidade. **Essa saída alimenta direto o checklist de Risk Mode (2.2)** — sem retrabalho.
2. **Perguntas em arquivo, não no chat:** quando há ambiguidade, o Discovery gera um `requirements.md` (ou `questions`) com perguntas de **múltipla escolha** (`A/B/C… + "Other"`) e tags **`[Answer]:`**. Portável entre hosts (D14) e resiliente (sobrevive à perda de contexto — D-resiliência).
3. **Gate:** não avança para Design até as respostas estarem preenchidas e validadas.
4. **Detecção de contradição/ambiguidade:** ao ler as respostas, gera follow-up se houver inconsistência (ex: "bug" + "afeta todo o sistema").
5. **Profundidade por modo:** FAST = poucas/nenhuma pergunta, inline; Standard = conjunto de esclarecimento; SAFE = abrangente + traceabilidade.
Consolidado vira o `problem`/requirements da demanda. Herdado de `inception/requirements-analysis.md` e `common/question-format-guide.md` do AI-DLC (D1).

## D17 — Persona: Alfred, o mordomo (identidade do framework)
Alfred **sabe que é o Alfred** — o mordomo (inspirado no mordomo do Batman). Isso é a identidade e a voz do framework, e reforça o D7:
- **Serve, não manda.** Antecipa necessidades, organiza, prepara o terreno e aconselha — mas **a squad/a pessoa decide**. O mordomo nunca toma a decisão da pessoa dona da decisão. (= D7 virado caráter.)
- **Discreto e competente.** Direto, cordial, sóbrio; sem floreio nem bajulação. Resolve o trivial sozinho (FAST/autonomia delegada) e traz o relevante à squad/à pessoa (checkpoints).
- **Leal e zeloso.** Cuida do contexto, do rastro (audit) e da casa (artefatos) sem ser lembrado; protege a squad/a pessoa de risco (overrides de Risk Mode, escalcustação).
- **Proativo, não intrusivo.** Sugere o próximo passo e o que falta (toolbar/D9), mas não atropela.
- **Voz:** aparece nas boas-vindas (D16) e no tom das interações. Tratamento cordial e neutro (ex: "Às ordens.", "Permita-me sugerir…", "Tudo pronto."), **sem exagero** — clareza sempre acima do personagem. Não usar "senhor", "senhora" ou "senhor(a)"; preferir nome conhecido, "você", "a pessoa" ou "a squad". Agnóstico (D3): é só tom nos prompts/artefatos, não muda mecânica.

## D16 — Boot de sessão (início do Alfred)
Toda sessão começa com uma sequência fixa antes de qualquer trabalho:
1. **Boas-vindas** — mensagem curta de abertura **na voz do mordomo (D17)**, exibida 1x por sessão.
2. **Detecção de contexto (HUB ou APP)** — o Alfred identifica em que repo está, para saber **quais artefatos ler e como**:
   - **HUB** se encontra `context.md` + `<iniciativa>/<demanda>/` (artefatos de iniciativa).
   - **APP** se encontra `.alfred/` + código da aplicação (artefatos técnicos).
   - (Framework, se encontra `principles.md`/`agents/` — modo de edição do próprio Alfred.)
   - Não identificou → pergunta ao humano.
3. **Atualização do Alfred local (CLI)** — se rodando via CLI, faz **pull do framework** para garantir a versão mais recente (adoção do D15) e **avisa se houve atualização** (o quê mudou, em 1 linha). Em hosts sem CLI/sem acesso, registra que não verificou.
   - **Salvaguarda (demanda em andamento):** se há atualização **e** uma demanda ativa, o Alfred **avisa e pergunta** — aplicar agora ou só na próxima demanda. A demanda registra **a versão do framework usada** e a mantém congelada até concluir, salvo decisão humana. Reconcilia adoção central (D15) com previsibilidade.
4. **Carga JIT** — lê `index` → `state` (resume se existir; nova se não) → links do tema → skills ativas. Monta o toolbar de progresso (D9).

Detalhe operacional na Fase 6.8. Herda o espírito do `workspace-detection` + `session-continuity` do AI-DLC (D1).

## D15 — Distribuição e evolução do framework (separação dura)
- **O HUB guarda SÓ artefatos** (contexto/iniciativas/demandas). **Nada do framework** é copiado para o HUB ou para os repos de app.
- **O framework vive no seu próprio repo** (fonte única). HUB e app **consomem/referenciam** o framework — não o duplicam.
- **Evolução/customização é central e adotada pelos usuários:** quando o framework evolui (nova regra, agente, skill, ajuste de Risk Mode) ou é customizado, **quem usa o Alfred passa a adotar** essa versão. Não há cópias divergentes espalhadas por HUBs.
- **Implicação de versão:** os artefatos podem registrar contra qual versão do framework foram produzidos (rastreabilidade), mas a referência ativa é sempre o repo do framework. Mecanismo de "como referenciar" (submodule, pin de versão, fetch) fica para a implementação, respeitando D3 (agnóstico).

## D14 — Modelo de execução (hosts, sem runtime próprio)
O Alfred **não tem runtime/daemon próprio**. É um conjunto de instruções/artefatos markdown **consumido por agentes host**: principalmente **DEVIN (CLI e Web)**, e também **Claude CLI** e **GitHub Copilot**. O host lê os arquivos do Alfred e **age como o Orchestrator/agentes**.
- **Portabilidade é requisito (D3):** tudo precisa funcionar igual nesses hosts; nada pode depender de recurso exclusivo de um deles. Onde um host tem recurso a mais (ex: subagentes p/ paralelismo D13), é aceleração opcional — degrada para sequencial nos demais.
- **Boot de sessão:** o host carrega `index` → `state` da demanda → links do tema → skills ativadas (JIT). Sem isso, comporta-se como sessão nova lendo o `state`.
- **Implicação:** "Orchestrator", "paralelismo" e "toolbar" são **comportamentos que o host executa seguindo as instruções**, não serviços rodando.

## D13 — Paralelismo controlado (multi-agente)
Quando **possível e seguro**, o Orchestrator pode acionar **vários agentes/tarefas em paralelo** e consolidar os resultados. Ele é o único controlador do fan-out.
- **Quando vale:** trabalho **independente** — ex: reverse-eng de N apps da demanda, revisão de múltiplos arquivos, exploração de alternativas, demanda que toca N apps (1 agente por app).
- **"Seguro" significa:** sem dependência de ordem entre as tarefas; **sem escrita concorrente na mesma fonte de verdade**. Cada tarefa escreve no seu próprio artefato (ex: `.alfred/<id>/` da sua app); **só o Orchestrator** consolida no `state`/`audit` do HUB (serializa o merge). Sem isso → executa sequencial.
- **Limites:** checkpoints HITL **não** são paralelizados (a squad decide em série); em SAFE, o Orchestrator restringe o paralelismo a tarefas claramente isoladas; mudanças no mesmo arquivo de código nunca em paralelo.
- **Agnóstico (D3):** paralelismo é capacidade do runtime se existir; se não houver, **degrada para sequencial** sem perder corretude. O `audit` registra o que rodou em paralelo (rastreabilidade).
- **Custo/métricas:** o custo (D10) soma as execuções paralelas; o toolbar pode indicar "N tarefas em paralelo".

## D12 — Skills (internas e externas) plugáveis
O Alfred aceita **skills** — módulos de capacidade/conhecimento (ex: revisão de segurança, teste baseado em propriedade, guia de domínio, padrão de arquitetura). Duas origens:
- **Internas:** vivem no repo do Framework (`skills/`).
- **Externas:** vivem em **outros repos** e são **passadas ao Alfred** (ponteiro: caminho/URL/sigla) para ele considerar.
Mecânica (alinhada a JIT/D11 e ao opt-in do AI-DLC):
- Um **registro de skills** (`skills.md`/entrada no `index`) lista skills disponíveis: nome, propósito, **quando aplicar** (stream/tipo, Risk Mode, fase) e **onde está** (link). Não carrega o conteúdo — só o ponteiro.
- **Ativação opt-in por demanda:** o humano/Orchestrator ativa as skills relevantes; o agente da fase carrega **só a(s) skill(s) ativada(s)** (JIT por referência).
- **Agnóstico (D3):** skill é markdown (ou ponteiro para repo markdown). Sem dependência de tooling; uma skill externa é só um repo que o Alfred lê.
- **Sem hipercontexto:** skill entra pelo índice e é carregada só quando seu gatilho casa com a demanda; ao fechar, vai para o `summary` o que a skill produziu/decidiu.
Detalhe de carregamento na Fase 6.7.

## D11 — Anti-hipercontexto: índice + JIT por referência + sumarização
Combate à hipercontextualização em todo o Alfred: (a) **Context Index** (`index.md` por sigla/app) mapeia tema→localização; agentes carregam o índice + só os links do tema (JIT por referência), nunca a pasta inteira. (b) **Artefatos referenciam, não transcrevem**; entradas curtas, split quando crescem. (c) **Sumarização no fechamento**: ao concluir a demanda, gera `summary.md` enxuto e atualiza o `index.md`; o detalhe é arquivado e linkado, não carregado. Detalhe na Fase 6.4–6.6.

## D10 — Custo acumulado visível
O Alfred rastreia e **exibe o custo de IA acumulado** por demanda (tokens + $ estimado + nº de interações), no toolbar a cada interação e consolidado no `metrics`. Objetivo: dar à squad noção de custo/benefício em tempo real (liga à dor "medir se a IA ajudou"). Opcional/futuro: alerta quando o custo passar de um teto definido no `risk`/`state`.
**Agnóstico (D3):** o campo de custo é texto no `metrics`/`state`; a captura automática de tokens é camada opcional. Sem tooling, o custo fica em branco ou aproximado — nunca bloqueia o fluxo.

---

# FASE 1 — Foundation Discovery

## 1.1 Definição curta
**Alfred é o framework que faz uma squad híbrida (humanos + IA) conduzir cada demanda pelo nível certo de processo — leve quando o risco é baixo, rigoroso quando é alto — usando AI-DLC como ciclo, SDD como trava de clareza e Risk Mode como seletor de governança.**

Frase-âncora: *Alfred não escolhe processo por preferência. Alfred escolhe processo por risco e complexidade.*

## 1.2 Definição expandida
Alfred é um **framework de governança adaptativa + operação de squad construído sobre o AI-DLC**. Ele não substitui o agente de código nem o ciclo de vida; ele decide, para cada demanda, *quanta* clareza (SDD), *quantos* checkpoints (HITL), *quais* artefatos e *qual* profundidade de cada fase aplicar — e materializa as especialidades (discovery, design, spec, review...) como artefatos de interação carregados sob demanda (JIT). O objetivo é evitar dois fracassos simétricos: burocracia em demanda simples e descontrole em demanda crítica.

## 1.3 Pilares
1. **AI-DLC** — espinha dorsal do ciclo (5 fases: Inception → Design → Execution → Validate → Operation).
2. **SDD** — nenhuma entrega relevante começa sem problema entendido, spec mínima, critérios de aceite, riscos e decisões registradas.
3. **Squad Híbrida** — papéis humanos e agentes claros; agentes são artefatos de especialidade.
4. **Risk Mode** — seletor adaptativo (FAST/Standard/SAFE) que regula profundidade, artefato e checkpoint por demanda.
5. **HITL** — humano decide o que é crítico (escopo, arquitetura, risco, custo, segurança, aceite final).
6. **JIT Context Loading** — contexto carregado sob demanda por fase/agente/modo, nunca tudo sempre.

## 1.4 Risk Mode (resumo conceitual; detalhe na Fase 2)
Mecanismo que classifica risco × complexidade da demanda e seleciona um de três modos:
- **FAST** — baixo risco/complexidade. Processo leve, spec mínima, autonomia delegada, poucos checkpoints. State + audit enxuto; sem decisions formais.
- **Standard** — risco/complexidade média. Discovery básico, spec clara, critérios de aceite, revisão técnica, 1 checkpoint humano, validação antes de release. State + decisions + audit.
- **SAFE** — alto risco/impacto. Mais governança, gestão de dependências, análise de risco, rollout/rollback, aceite formal, rastreabilidade. State + decisions + audit completo. NÃO copia SAFE; é só o modo de governança forte.

Princípio anti-degeneração: **Risk Mode nunca pula fase — regula profundidade.** Toda demanda passa pelas 5 fases conceitualmente; o que muda é peso.

## 1.5 Critérios iniciais de risco e complexidade (rascunho p/ Fase 2)
- **Risco**: reversibilidade, impacto em usuário/cliente, segurança, dados sensíveis/regulado, custo, dependências externas, impacto organizacional.
- **Complexidade**: nº de componentes/sistemas afetados, novidade técnica, ambiguidade do requisito, esforço estimado, nº de pontos de integração.
- Risco e complexidade são **eixos distintos**: algo simples pode ser altíssimo risco (deletar tabela de produção) e algo complexo pode ser baixo risco (refactor amplo com testes). Risk Mode pega o **maior** dos dois eixos como piso.

## 1.6 As 5 fases (resumo; detalhe na Fase 3)
1. **Inception — O quê?** Entender a demanda. Saídas: problem statement, objetivo, escopo/fora de escopo, riscos iniciais, Risk Mode inicial.
2. **Design — Como?** SDD forte. Saídas: solução, spec, critérios de aceite, decisões, dependências, plano de execução/teste.
3. **Execution — Fazer.** Executar alinhado à spec, alterações pequenas/rastreáveis, revisão técnica.
4. **Validate — Validar.** Critérios de aceite, testes, regressão, aprovação humana.
5. **Operation — Operar e evoluir.** Release, métricas, feedback, aprendizado, débitos.

## 1.7 Dores que o Alfred resolve
- IA codando sem entender → SDD trava clareza antes de Execution.
- Toda demanda no mesmo processo → Risk Mode adapta.
- Processo pesado p/ simples e leve p/ crítico → FAST vs SAFE.
- Perda de contexto entre sessões → `state` + session-continuity (herdado do AI-DLC).
- Prompts soltos sem rastreabilidade → agentes viram artefatos versionados.
- Decisões não registradas → `decisions` em Standard/SAFE.
- Excesso de doc inútil → artefato só existe se tem uso; audit enxuto em FAST, completo em SAFE.
- Agente com contexto demais/de menos → JIT Loading + anti-hipercontextualização.
- Falta de checkpoint humano → HITL por modo.
- Difícil escalar IA na squad → modelo operacional repetível.
- Falta de padrão p/ specs → SDD com template mínimo.
- Difícil medir se IA ajudou → métricas na fase Operation.
- Falta de conexão demanda→spec→código→teste→validação→operação → rastro pelas 5 fases + state.

## 1.8 Antiobjetivos (o que o Alfred NÃO é)
Clone de SAFE; cópia de FAST; só prompts; só pasta; burocracia de markdown; processo pesado; substituto do humano; framework que exige muitos arquivos p/ começar; rito único pesado p/ tudo; agente que carrega todo contexto; doc que ninguém usa.

## 1.9 Princípios fundamentais
**Não inventar — na dúvida, parar e perguntar (D41, lei suprema)** · Simplicidade (nascer pequeno) · Clareza (1 responsabilidade por artefato) · Baixa redundância (1 fonte de verdade, referenciar não duplicar) · Resiliência (state retomável) · JIT Context Loading · Anti-hipercontextualização (split quando crescer) · **Humano no controle e responsável pela decisão em todos os modos (D7)** · Rastreabilidade (audit em todos os modos).

## 1.10 Escopo do Alfred
**Dentro:**
- Risk Mode com classificador (checklist de risco × complexidade → FAST/Standard/SAFE).
- As 5 fases com profundidade variável por modo.
- SDD (template de spec + critérios de aceite + decisões).
- `state` vivo por demanda (resiliência).
- Engenharia reversa pesada em brownfield (compreensão do produto antes de agir).
- **Orquestração multi-agente** (Orchestrator roteia entre agentes por fase/modo).
- **Acompanhamento de métricas dos agentes** (Metrics Agent — ver Fase 5).
- Agentes materializados como artefato (ver abaixo).
- HITL por modo.
- Reuso do state/continuity/reverse-engineering do AI-DLC.

**Agentes:** Orchestrator, Discovery (Inception), Spec/Design (Design+SDD), Reviewer (Execution+Validate), Metrics (Operation). Detalhe e validação na Fase 4.

**Fora do Alfred:**
- **Compliance** (papel e gate regulatório) — não faz parte do Alfred.
- Documentation Agent dedicado (doc é subproduto, não agente próprio).
- Plataforma/tooling próprio (markdown agnóstico basta).
- Dashboards visuais (métricas existem como dado/artefato; visualização é evolução futura).

## Evolução futura
- Toolbar de evolução, playbooks por stream/tipo, dashboards de métricas.

## 1.11 Riscos do próprio Alfred
- Virar mais um framework-documento que ninguém usa → mitigar com escopo inicial enxuto e uso real imediato.
- Risk Mode degenerar (tudo vira FAST por preguiça ou tudo vira SAFE por medo) → Fase 2 precisa de gatilhos objetivos.
- Reescrever o AI-DLC em vez de envolvê-lo → D1 mantém wrapper.

## 1.12 Perguntas críticas pendentes
S1 (brownfield), S2 (solo vs squad), S3 (regulado) — ver topo.

---

# FASE 2 — Risk Mode Design

## 2.1 Risco ≠ Complexidade (dois eixos independentes)
- **Risco = consequência se der errado.** Reversibilidade, blast radius, segurança/dados sensíveis, dados sensíveis, custo, impacto em cliente, impacto organizacional.
- **Complexidade = dificuldade de fazer certo.** Nº de componentes/sistemas, novidade técnica, ambiguidade do requisito, esforço, pontos de integração, nº de pessoas envolvidas.
- Regra: **o modo é definido pelo MAIOR dos dois eixos** (piso). "Simples e perigoso" (drop em tabela de produção) = alto risco → não é FAST. "Complexo e seguro" (refactor amplo com testes) = pode subir de modo por complexidade, mas com governança focada em técnica, não em compliance.

## 2.2 Critérios de avaliação (checklist objetivo)
Cada critério pontua 0/1/2. Soma separada por eixo.

**Eixo RISCO**
| Critério | 0 | 1 | 2 |
|---|---|---|---|
| Reversibilidade | trivial de reverter | reversível com esforço | difícil/irreversível |
| Blast radius | local | 1 sistema/squad | multi-sistema/squad |
| Dados sensíveis/regulado | nenhum | PII leve | regulado/sensível |
| Impacto em cliente | interno | indireto | direto em produção |
| Custo/risco financeiro | baixo | médio | alto |

**Eixo COMPLEXIDADE**
| Critério | 0 | 1 | 2 |
|---|---|---|---|
| Componentes afetados | 1 | poucos | muitos |
| Novidade técnica | conhecido | parcial | inédito |
| Ambiguidade do requisito | claro | algumas dúvidas | vago |
| Integrações | nenhuma | 1 | várias/externas |
| Esforço estimado | horas | dias | semanas |

## 2.3 Escala de pontuação → modo
Pega-se o **maior** dos dois somatórios (0–10 cada):
- **0–3 → FAST**
- **4–6 → Standard**
- **7–10 → SAFE**

**Overrides duros (forçam o modo acima, independente do score):**
- Qualquer critério de risco = 2 em *dados sensíveis/regulado* OU *irreversível* OU *impacto direto em cliente* → **mínimo Standard; se 2+ desses, SAFE.**
- Mudança arquitetural ou multi-squad → **SAFE**.
Isso evita "coisa crítica tratada como FAST".

**Trava anti-SAFE (evita que tudo vire SAFE):**
- SAFE exige **justificativa explícita** registrada em `decisions` (qual override/score disparou). Sem justificativa → cai para Standard.
- Revisão periódica: se a squad está classificando >X% como SAFE, é sinal de medo, não de risco → reavaliar critérios.

## 2.4 Eixo de TEMPO (novo — por causa do stream Operacional)
Risk Mode mede *governança*. Para Operacional crítico (incidente/hotfix/rollback) há um eixo ortogonal: **urgência**.
- **Normal:** ciclo completo na profundidade do modo.
- **Emergência:** fluxo **Execution-first** (ver D6). Estabiliza com autorização humana mínima; Inception/Design/Validate viram *post-mortem* obrigatório depois (spec retroativa + decisions + lição aprendida). O Risk Mode (governança) continua valendo — só a *ordem* e o *timing* mudam.
- Regra de ouro: emergência **nunca dispensa** o registro; só o **adia**. Sem post-mortem, a demanda não fecha.

## 2.5 O que muda por modo

| Dimensão | FAST | Standard | SAFE |
|---|---|---|---|
| Inception | 1 parágrafo (problema+objetivo) | problem statement + escopo + riscos | + stakeholders, impacto org., análise de risco |
| Design/SDD | spec mínima inline | spec + critérios de aceite + decisões | + alternativas, dependências, rollout/rollback |
| Execution | autônomo, PR pequeno | PR + revisão técnica | + gestão de dependências, aprovações |
| Validate | testes locais | critérios de aceite + regressão | + aceite formal, segurança/dados sensíveis |
| Operation | nota de release opcional | release notes + métricas básicas | + monitoramento, plano de rollback ativo |
| Checkpoints HITL | autonomia delegada (humano responsável via audit) | 1 (aprovação de spec) + aceite final | múltiplos (escopo, arquitetura, risco, aceite) |
| Rastreio | state + audit enxuto | state + decisions + audit | state + decisions + audit completo |

## 2.6 Checkpoints HITL por modo
- **FAST:** autonomia delegada — a IA executa e **registra em audit** (humano permanece responsável). Chamada explícita ao disparar qualquer **gatilho de escalonamento (D27)**.
- **Standard:** 1 checkpoint na transição Design→Execution (aprovar spec) + 1 aceite final em Validate.
- **SAFE:** checkpoint em cada transição de fase + aprovações por papel (PM=escopo, Tech Lead=arquitetura/risco técnico, QA=aceite, Sponsor=custo/estratégia).

## 2.7 Artefatos mínimos por modo
- **FAST:** `state` (1 entrada) + `audit` enxuto + PR. Spec é o próprio título+descrição do PR.
- **Standard:** `state` + `spec` (problema, solução, critérios de aceite) + `decisions` + `audit` + PR.
- **SAFE:** tudo acima + análise de risco + plano de rollout/rollback + registro de aprovações + `audit` completo.

## 2.8 Reclassificação durante o ciclo
- O Risk Mode é **inicial em Inception** e **revisado em Design** (gatilho explícito: "o modo continua correto?").
- Pode subir a qualquer momento se um gatilho de override aparecer (ex: descobriu-se que toca dados sensíveis) → a IA **deve** pausar e escalar para humano.
- Descer de modo exige **aprovação humana** (evita que se afrouxe governança por conveniência).
- Toda mudança de modo vira entrada em `decisions` com o motivo.

## 2.9 Anti-degeneração (resumo)
- Tudo vira SAFE → exige justificativa registrada + revisão de % por período.
- Crítico vira FAST → overrides duros + reclassificação obrigatória ao detectar gatilho.
- Emergência vira desculpa p/ pular registro → post-mortem obrigatório fecha a demanda.

## 2.10 Quem classifica (confirmado)
**IA propõe, humano é responsável.** A IA roda o checklist e sugere o modo. Em **FAST** segue por autonomia delegada (humano responsável, registrado em audit). Em **Standard/SAFE** um humano confirma/ajusta antes de avançar. Checklist de 10 critérios mantido como está.

## 2.11 Escopo do modo: por demanda, override por app (confirmado)
A demanda tem um **modo base** (a classificação geral). Quando toca várias apps, uma app específica pode **subir de modo** no seu escopo (ex: app de pagamento vira SAFE mesmo numa demanda Standard). Regras:
- O override **só sobe**, nunca desce (governança não afrouxa por app).
- Cada override é registrado no `risk.md` com justificativa (qual app, qual gatilho).
- A app executa no seu modo efetivo (base ou elevado); os artefatos técnicos daquela app seguem o modo elevado.
- O toolbar mostra o modo base; quando numa app elevada, indica "app X: SAFE".

# FASE 3 — Lifecycle Design

## Princípio transversal
As 5 fases são **conceituais e sempre existem**; o Risk Mode regula profundidade, e o stream regula o caminho. FAST colapsa fases em minutos; Operacional-emergência usa Execution-first (D6). Nenhuma fase é "pulada" — ela pode ser comprimida a uma linha ou adiada (post-mortem).
O **"critério para avançar"** de cada fase abaixo é a forma resumida do **DoD por modo (D25)** — fonte única do gate; não repetir régua, referenciar.

## 3.1 Inception — O quê?
- **Objetivo:** entender a demanda antes de desenhar solução.
- **Entrada:** pedido cru + contexto do produto (JIT).
- **Duas lentes (D33):** negócio (importada de agente externo no stream **Produto**) + técnica (sempre feita pelo Alfred). Em Produto, ingere o `inception-input` e aplica a **Inception técnica** (`tech-inception`) sem refazer o discovery de negócio.
- **Mecanismo (D18 — requirements):** intent analysis → perguntas de esclarecimento em arquivo (múltipla escolha + `[Answer]:`) → gate aguardando respostas → detecção de contradição → consolida requisitos. O intent analysis alimenta o checklist de Risk Mode (D31).
- **Saída:** problem statement, objetivo, escopo/fora de escopo, riscos iniciais, **Risk Mode proposto** (checklist), stream/tipo, `requirements` consolidado.
- **Papéis humanos:** PM (escopo/valor), Especialista de Domínio (contexto). Sponsor só em SAFE.
- **Agentes:** Discovery Agent.
- **Checkpoint HITL:** confirmar Risk Mode (Std/SAFE); confirmar escopo (SAFE).
- **Artefatos mín.:** FAST=1 parágrafo no state · Standard=problem statement+riscos · SAFE=+stakeholders+análise de risco.
- **Critério p/ avançar:** problema claro o suficiente p/ desenhar; modo confirmado.
- **Diferença por modo:** ver 2.5.
- **Risco de burocracia:** discovery longo p/ demanda óbvia. **Gatilho p/ simplificar:** se FAST e problema claro, Inception é só registrar intenção e seguir.

## 3.2 Design — Como? (SDD forte)
- **Objetivo:** definir como resolver antes de executar.
- **Entrada:** saída de Inception.
- **Herança AI-DLC (D19):** sub-atividades **opcionais por gatilho/modo** — application-design (novo componente), units-generation (decompor), functional-design (lógica nova), NFR (perf/segurança/escala), infrastructure (deploy). Mais o **workflow-planning** (impacto, skip/execute justificado, sequência, paralelização D13). Tudo dentro de Design, não como fases.
- **Template/referência (D35):** confirmar qual repo de template se aplica (API/front/lib) para **espelhar o padrão** na Execution.
- **Saída:** solução escolhida, spec, critérios de aceite, decisões, dependências, plano de execução/teste; **revalidação do Risk Mode**.
- **Papéis humanos:** Tech Lead (arquitetura/decisões), PM (aceite de escopo).
- **Agentes:** Spec/Design Agent.
- **Checkpoint HITL:** aprovação da spec (Standard/SAFE); aprovação de arquitetura e alternativas (SAFE).
- **Artefatos mín.:** FAST=spec inline no PR · Standard=spec+critérios+decisions · SAFE=+alternativas+dependências+rollout/rollback.
- **Critério p/ avançar:** spec aprovada (Std/SAFE) ou clara (FAST); critérios de aceite definidos.
- **Risco de burocracia:** spec gigante p/ mudança pequena. **Gatilho p/ simplificar:** FAST não tem fase Design separada — funde com Execution.

## 3.3 Execution — Fazer
- **Objetivo:** executar alinhado à spec, em alterações pequenas e rastreáveis.
- **Entrada:** spec aprovada (ou intenção, em FAST/emergência).
- **Herança AI-DLC (D19):** padrão **Planning+Generation** — plano numerado com checkboxes (fonte única) → geração passo a passo marcando [x]; **brownfield modifica in-place** (nunca `arquivo_v2`); rastro requisito→código; código automation-friendly (`data-testid` etc.).
- **Loop por unit (D24):** se a demanda foi decomposta, Execution roda **por unit** (cada uma menos complexa; independentes em paralelo — D13); units são checklist no `state`, não states novos.
- **Espelhar template (D35):** ao gerar/modificar código, segue a estrutura/convenções do repo de template aplicável (carrega só as seções relevantes, JIT).
- **Padrão SOLID (D36):** codifica conforme o coding-standard (SOLID) — usa o da **skill da linguagem** se houver (override D22), senão o base.
- **Saída:** código/alteração, evidências, state atualizado, desvios registrados, revisão técnica, PR.
- **Papéis humanos:** Developer, Tech Lead (revisão).
- **Agentes:** Code Generator (execução), Reviewer Agent.
- **Checkpoint HITL:** revisão técnica do PR (Standard/SAFE); aprovações de dependências (SAFE). FAST: só se escopo crescer.
- **Artefatos mín.:** PR sempre; evidências em Std/SAFE.
- **Critério p/ avançar:** PR pronto, revisão passada, sem aumento de escopo não aprovado.
- **Risco de burocracia:** revisão cerimoniosa em mudança trivial. **Gatilho p/ simplificar:** FAST = auto-revisão + PR pequeno.
- **Especial (emergência):** Execution-first — estabiliza com autorização mínima; Inception/Design viram post-mortem.

## 3.4 Validate — Validar
- **Objetivo:** confirmar que a execução atende spec, objetivo e critérios de aceite.
- **Entrada:** PR + critérios de aceite.
- **Herança AI-DLC (D19):** estratégia de testes do **build-and-test** por necessidade (unit/integração/performance/e2e/contrato/segurança) + summary de testes + gate. Profundidade por modo (FAST = testes locais; SAFE = suíte completa + evidências).
- **Saída:** resultado de testes, checklist de aceite, evidências, pendências, decisão aprovação/reprovação.
- **Papéis humanos:** QA, PM (aceite final).
- **Agentes:** QA/Evaluator (parte do Reviewer no Alfred).
- **Checkpoint HITL:** aceite final (Standard/SAFE); aceite formal + sign-off (SAFE). **O merge do PR na develop É o aceite** (branch protegida força aprovação humana — D23).
- **Artefatos mín.:** FAST=testes locais ok · Standard=checklist de aceite+regressão · SAFE=+evidências formais+sign-off.
- **Critério p/ avançar:** critérios de aceite atendidos; aprovação registrada.
- **Risco de burocracia:** checklist formal p/ FAST. **Gatilho p/ simplificar:** FAST = testes passaram = validado.

## 3.5 Operation — Operar e evoluir
- **Objetivo:** acompanhar em uso e capturar aprendizado.
- **Entrada:** entrega validada.
- **Herança AI-DLC (D19):** o AI-DLC deixa Operations como *placeholder* — o Alfred **preenche** (release, métricas, post-mortem, summary/D11). É onde o Alfred mais estende o AI-DLC.
- **Saída:** release notes, métricas, feedback, incidentes, lições aprendidas, débitos, próximas melhorias. **Post-mortem** (se veio de emergência). **`summary.md` + atualização do `index.md`** (D11 — sumarização de contexto).
- **Papéis humanos:** PM (métricas/feedback), Tech Lead (débitos), Liderança (SAFE).
- **Agentes:** Metrics Agent (coleta métricas dos agentes e da entrega).
- **Checkpoint HITL:** go/no-go de release (SAFE); rollback ativo (SAFE).
- **Artefatos mín.:** FAST=nota opcional · Standard=release notes+métricas básicas · SAFE=+monitoramento+rollback.
- **Critério p/ fechar:** entregue, observado, aprendizado registrado; post-mortem feito se aplicável.
- **Risco de burocracia:** relatório de métricas p/ FAST. **Gatilho p/ simplificar:** FAST encerra ao mergear; Operation é opcional.

## 3.7 Checkpoint HITL padronizado (herdado do AI-DLC)
Toda transição relevante de fase apresenta **2 opções** (sem menus emergentes):
- **🔧 Request Changes** — pedir ajustes antes de avançar.
- **✅ Approve & Continue** — aprovar e seguir para a próxima fase.
Em **FAST** o checkpoint é implícito (autonomia delegada, registrado em audit); em **Standard/SAFE** é explícito, com o papel-dono nomeado (4.1). O Alfred sempre antecede com um resumo factual do que foi feito (sem instruções de workflow infladas). Voz do mordomo (D17): "Tudo pronto. Deseja que eu prossiga ou ajuste algo?".

## 3.6 Caminhos por stream (fluxos concretos)
Mesmo ciclo de 5 fases; o stream muda **ênfase, sub-atividades e ordem**. (Sementes dos futuros playbooks por stream.)

### Produto (feature, jornada, UX, experimento, regra de negócio)
- **Ênfase:** Design/SDD (spec + critérios de aceite) e Validate (aceite de usuário).
- **Sub-atividades típicas:** user-stories (jornada/UX), application-design (novo componente).
- **Modo:** tende Standard; SAFE se toca cliente final/dados sensíveis/multi-app.
- **Experimento:** atalho — FAST com hipótese clara; o aprendizado é capturado em Operation (métricas + summary), não vira spec pesada.

### Engineering (refactor, débito, upgrade, migração, performance, segurança, FinOps, arquitetura, provedor)
**Traços comuns:** Inception curto (problema técnico claro) com **lente técnica forte** (`tech-inception`, D33); **reverse-eng pesa** (S1/D21); Design ênfase em **decisions/ADR**; Validate ênfase em **regressão**; geralmente sem Inception de negócio externa.

Sub-fluxos por tipo:
- **Refactor / débito técnico:** comportamento **preservado**. Critério de aceite = "testes passam + comportamento inalterado". SOLID/template (D36/D35) no centro. Modo Standard; refactor amplo (muitos componentes) sobe por complexidade.
- **Upgrade (dependência/framework):** risco vem de **breaking changes**. Passos: revisar changelog/compat → atualizar → **regressão** → plano de rollback. Override **SAFE** se major/breaking ou muitos dependentes.
- **Migração (tech/plataforma/provedor):** **alto risco → SAFE**. Irreversibilidade + multi-componente. Exige **rollout faseado** (strangler/parallel-run), cuidado com **migração de dados**, e **rollback** explícito. Reverse-eng essencial; costuma virar várias **units** (D24).
- **Performance:** exige **baseline antes/depois** (métricas) e **testes de performance** na Validate. Risco se toca hot path. Liga ao custo (D10/FinOps).
- **Segurança:** usa **skill de segurança** (D12, precedência D22); tende SAFE; se for vuln em produção, pode nascer como **incidente** (D34).
- **Observabilidade / automação interna / FinOps:** geralmente baixo risco/interno → FAST/Standard.
- **Mudança por provedor (deprecation):** tem **prazo externo**; risco pelo blast radius; tratar como upgrade/migração conforme o tamanho.
- **Modo (resumo):** tende Standard; **migração/arquitetura/segurança/upgrade-breaking → SAFE** (overrides duros 2.3).

### Operacional — normal (bug, suporte, alerta, degradação leve)
- Ciclo enxuto, FAST/Standard: reproduzir → corrigir → teste de regressão → PR/merge.
- Inception/Design comprimidos (1 linha cada); Validate foca regressão.

### Operacional — emergência (incidente, hotfix, rollback, falha em produção) — Execution-first (D6)
Entrada: **nº do incidente + descrição**. Passo a passo:
1. **Declarar incidente** — registro mínimo no `state`: o quê, severidade, on-call responsável. (Toolbar: Execution ▶, Inception/Design `⏳ pós`.)
2. **Investigação exploratória (D34)** — busca em observabilidade (se AWS, **CloudWatch** via skill) → localiza o erro/stack trace → **mapeia para os repos** afetados → abre os códigos → produz `investigation.md` (causa provável). Sem acesso à skill, o humano fornece os logs.
3. **Autorização mínima** do humano on-call — HITL **comprimido, não pulado** (D7).
4. **Estabilizar** — hotfix/rollback direto; o `audit` registra cada ação (D27: nada destrutivo sem ok).
5. **Validar estabilização** — smoke test / monitor; confirmar que o sangramento parou.
6. **Pós-incidente (obrigatório p/ fechar):** Inception/Design retroativos = **post-mortem** — causa raiz (já documentada na `investigation`), `decisions`, spec retroativa, lições.
7. **Operation** — registrar incidente, métricas, **débito/ação preventiva** (vira nova demanda se preciso).
Regra: sem post-mortem, a demanda **não fecha** (D6).

# FASE 4 — Hybrid Squad Operating Model

## 4.1 Papéis humanos (squad multi-humano)
| Papel | Decide | Quando atua |
|---|---|---|
| Sponsor/Liderança | custo, estratégia, prioridade | SAFE |
| PM | escopo, valor, aceite final | Inception, Validate |
| Tech Lead | arquitetura, decisões técnicas, risco técnico | Design, Execution |
| Developer | implementação | Execution |
| QA | aceite, testes, regressão | Validate |
| Especialista de Domínio | contexto, regras de negócio | Inception |

> **Compliance NÃO é papel do Alfred.** Demandas reguladas geram `audit` para rastreabilidade, mas a aprovação regulatória, se existir, é externa ao framework.

## 4.2 Papéis de agentes (= artefatos de especialidade, D2)
Orquestração multi-agente faz parte do Alfred: o **Orchestrator** roteia entre os agentes por fase/modo.
| Agente | Fase | Faz | Limite (não decide) |
|---|---|---|---|
| **Orchestrator** | todas | roteia entre agentes por fase/modo, mantém o `state` | não aprova nada; não executa domínio |
| **Discovery** | Inception | estrutura problema, propõe Risk Mode, levanta riscos/perguntas | não fecha escopo |
| **Spec/Design** | Design | gera spec, critérios de aceite, registra decisões, propõe alternativas | não aprova arquitetura |
| **Reviewer** | Execution+Validate | revisa código, roda checklist de aceite, aponta regressão/risco | não dá aceite final |
| **Metrics** | Operation | coleta métricas dos agentes e da entrega | não decide release |
| Code Generator (futuro) | Execution | gera código | — |

## 4.3 Limites da IA / decisões que exigem humano
IA **propõe, organiza, executa, revisa**. Humano aprova: escopo, arquitetura, riscos relevantes, custo, segurança, mudança de direção, aceite final, aumento de escopo, descida de Risk Mode.

## 4.4 Colaboração sem handoff pesado
- **Fonte de verdade única:** o `state` da demanda. Todo agente/humano lê e escreve nele — não há "passar pasta".
- **Sem sobreposição:** cada agente tem 1 fase-dona e 1 responsabilidade (4.2). Reviewer não escreve spec; Discovery não revisa código.
- **Handoff = atualizar o state**, não reunião. Próximo ator lê o state + carrega contexto JIT da sua fase.

## 4.5 Acompanhamento e aprendizado
- **Progresso:** campo de status no state (fase atual, modo, pendências, próximos passos).
- **Aprendizado:** `decisions` (por que) + lições aprendidas em Operation. Post-mortem em emergência.
- **Responsabilidade humana clara:** cada checkpoint HITL tem um papel-dono nomeado (4.1).

## 4.6 Estrutura do artefato de agente (D2)
Todo agente é um arquivo `agents/<nome>.md` com a MESMA estrutura. É o que a IA carrega (JIT) para "virar" aquele agente. Mantido curto (~1 tela).
```markdown
# Agente: <Nome>
- Fase-dona: <fase>      | Aciona quando: <gatilho>
- Propósito (1 linha): <...>

## Faz / Não faz
- Faz: <bullets>
- NÃO decide: <o que sempre volta ao humano — liga ao D7>

## Contexto JIT (o que carregar)
- Sempre: princípios + risk-mode + state da demanda
- Desta fase: <artefatos/seções específicas>
- NÃO carregar: <o que é de outra fase/agente>

## Entradas → Saídas
- Lê: <state + artefatos>
- Escreve/atualiza: <artefatos> (sempre atualiza o state + audit)

## Interação (formato)
- Como pergunta ao humano: <múltipla escolha / objetivo>
- Como propõe: <formato de output>
- Comportamento por modo: FAST <...> | Standard <...> | SAFE <...>

## Handoff
- Conclui escrevendo no state: próximo passo + próximo agente sugerido
```

## 4.7 Os 5 agentes (resumo do que cada artefato preenche)
- **Orchestrator** — Fase: todas. Lê o `state`, decide qual agente acionar conforme fase/modo/stream, garante que checkpoints HITL aconteçam, mantém o `state` e o `audit` coerentes, **valida os links HUB↔App a cada handoff**, **monta o cabeçalho de progresso (D9)** e **gerencia o paralelismo seguro (D13)** — fan-out de tarefas independentes e merge serializado no `state`. NÃO executa trabalho de domínio nem decide; só roteia, paraleliza e registra.
- **Discovery** — Fase: Inception. **Ingere a Inception de negócio externa** quando houver (Produto, D33) e produz a **Inception técnica** (`tech-inception`). Faz o **intent analysis**, gera as **perguntas de requirements em arquivo** (múltipla escolha + `[Answer]:`, D18), aguarda o gate, detecta contradições, roda o checklist de Risk Mode e **propõe** o modo, levanta riscos. Consolida no HUB. NÃO fecha escopo nem refaz discovery de negócio.
- **Spec/Design** — Fase: Design. Gera a `spec` (SDD), critérios de aceite, registra `decisions`, propõe alternativas (SAFE). Revalida o Risk Mode. NÃO aprova arquitetura (Tech Lead aprova).
- **Reviewer** — Fase: Execution + Validate. Revisa código contra a spec **e contra o padrão SOLID/coding-standard ativo** (D36), roda checklist de aceite, aponta regressão/risco, prepara evidências de validação. NÃO dá aceite final (QA/PM dão).
- **Metrics** — Fase: Operation. Coleta `metrics` (via tooling + qualitativo), registra lições aprendidas e post-mortem (se emergência). NÃO decide release.

## 4.8 Como evitam sobreposição
- 1 agente = 1 fase-dona = 1 responsabilidade. Reviewer não escreve spec; Discovery não revisa código.
- Comunicação só via `state` (sem "passar pasta"). O Orchestrator é o único que enxerga o fluxo inteiro.
- Cada agente carrega só seu contexto JIT (4.6) — reforça anti-hipercontextualização.

# FASE 5 — Artifact Model

## 5.1 Classificação
| Artefato | Status | Responsabilidade | Fonte de verdade |
|---|---|---|---|
| `state` (por demanda) | **essencial** | estado vivo: fase, modo, pendências, próximos passos | a própria demanda |
| `spec` (por demanda, Std/SAFE) | **essencial** | problema, solução, critérios de aceite | SDD da demanda |
| `decisions` (Std/SAFE) | **essencial** | o que foi decidido e por quê (inclui mudança de modo) | histórico de decisão |
| Risk checklist | **essencial** | classificação do modo | embutido no state |
| Agent artifacts (Orchestrator, Discovery, Spec/Design, Reviewer, Metrics) | **essencial** | papel+contexto JIT+interação | def. do agente |
| Reverse-engineering (brownfield) | **essencial** | compreensão do produto antes de agir | herdado do AI-DLC |
| `metrics` (por demanda/agente) | **essencial** | medir desempenho dos agentes e da entrega | Metrics Agent |
| README/princípios do Alfred | **essencial** | explica o framework | raiz do Alfred |
| Templates (spec/state/decision) | **essencial** | padronização | pasta de templates |
| `audit` | **essencial (todos os modos)** | rastreabilidade + registro de quem decidiu (enxuto FAST / completo SAFE) | log da demanda |
| Playbooks por stream/tipo | **evolução futura** | guia por tipo de demanda | — |
| Dashboards visuais de métricas | **evolução futura** | visualização (dado já existe em `metrics`) | — |
| Process Toolbar (visual, D9) | **essencial (todos os modos)** | acompanhamento visual do fluxo a cada interação | gerado do `state` pelo Orchestrator |
| `index.md` (Context Index, D11) | **essencial** | mapa tema→localização; base do JIT por referência | HUB por sigla + app local |
| `summary.md` (D11) | **essencial** | sumarização de contexto no fechamento | gerado em Operation |
| Skills + `skills.md` (D12) | **essencial** | capacidades plugáveis (internas/externas), opt-in JIT | Framework `skills/` + registro HUB |
| Compliance / Documentation Agent / checklists extensos | **fora do Alfred / cortar** | — | — |

## 5.2 Ciclo de vida de artefato
- **Criar:** quando a fase que o produz inicia (lazy).
- **Atualizar:** no fim de cada fase / a cada decisão / mudança de modo.
- **Arquivar:** ao fechar a demanda (Operation), o state vira histórico.
- **Dividir:** quando um artefato passa de ~1 tela ou mistura responsabilidades → split por fase/responsabilidade (anti-hipercontextualização).

## 5.3 Templates detalhados (campos)
Princípios dos templates: campos escalam por modo (FAST = mínimo, SAFE = completo). Tudo é markdown. O `state` é a fonte de verdade viva; os demais são derivados/históricos.

### 5.3.1 `state.md` — estado vivo da demanda (todos os modos)
Fonte de verdade do "onde estamos". Curto, sempre atualizado.
```markdown
# <id-demanda> — <título curto>          (sigla <SIGLA> · iniciativa <INI>)
- Alfred/framework: <versão|commit>  · branch: <alfred/id-demanda>   (D26/D23)
- Stream/Tipo: <Produto|Operacional|Engineering> / <tipo>
- Risk Mode: <FAST|Standard|SAFE>  (proposto por IA / confirmado por <humano>)
- Fase atual: <Inception|Design|Execution|Validate|Operation>
- Status: <em andamento|em espera|bloqueada|aguardando checkpoint|concluída|cancelada>  (D28)
- Responsável humano: <nome>
- Próximo passo: <1 linha>
- Pendências: <bullets curtos>
- Perguntas abertas: <bullets, ou "nenhuma">
- Riscos ativos: <bullets, ou "nenhum">
- Apps tocadas: <sigla/repo → .alfred/<id-demanda>/>  (1+; correlação técnica)
- Links HUB: problem | risk | decisions | audit | metrics
- Última atividade: <data> por <humano|agente>   (D28 — ajuda a notar paradas)

## Progresso (D9 — base do cabeçalho)
- [x] Inception     <resumo 1 linha>
- [ ] Design        <pendente: o que falta>
- [ ] Execution
    - units (se decomposta — D24): [ ] unit A · [ ] unit B · [ ] unit C
- [ ] Validate
- [ ] Operation
- Etapa interna atual: <ex: "Design → gerando spec">
- Próximo checkpoint HITL: <qual / quem>
```

### 5.3.2 `spec.md` — SDD (Standard/SAFE; em FAST é o PR)
```markdown
# Spec — <id-demanda>
## Problema  (o quê e por quê)
## Objetivo / valor esperado
## Escopo  /  Fora de escopo
## Solução proposta
## Alternativas consideradas        (SAFE)
## Critérios de aceite              (lista verificável)
## Dependências                     (Standard: simples · SAFE: + externas/squads)
## Impactos                         (usuário, sistemas, dados)
## Plano de execução / plano de teste
## Plano de rollout / rollback      (SAFE)
```

### 5.3.3 `decision.md` — registro de decisão (Standard/SAFE)
Uma entrada por decisão relevante (inclui mudança de Risk Mode). Append-only.
```markdown
## D<n> — <título da decisão>  (<data>)
- Contexto: <por que precisou decidir>
- Opções: <as consideradas, 1 linha cada>
- Decisão: <o que foi escolhido>
- Quem decidiu: <humano responsável>
- Consequências/trade-offs: <bullets>
```

### 5.3.4 `metrics.md` — métricas dos agentes e da entrega (todos os modos)
Coletado **automaticamente via tooling** (Metrics Agent + integração com git/CI puxa lead time, defeitos, nº de revisões; campos qualitativos como "% aproveitado" ficam semi-automáticos). Foco em "a IA ajudou ou atrapalhou?".

> **Tensão com D3 (markdown agnóstico):** a coleta automática introduz uma **camada de automação opcional** (scripts/hook lendo git/CI) só para métricas. O framework em si continua agnóstico — o `metrics.md` é markdown e pode ser preenchido à mão se a automação não existir. Decisão: automação é o alvo, markdown é o fallback. A definir na implementação: que tooling (git log, GitHub API, CI) e onde roda.
```markdown
# Métricas — <id-demanda>
## Processo
- Risk Mode acertou? (precisou reclassificar? quantas vezes)
- Retrabalho: nº de ciclos de revisão até aceite
- Aceite de primeira: sim/não
- Checkpoints humanos: quantos / quanto tempo aguardando
## Agentes
- Por agente (Discovery/Spec/Reviewer/...): nº de outputs, % aproveitado, correções humanas
## Entrega
- Lead time (Inception→merge)
- Defeitos pós-release / incidentes
- Esforço humano vs. esforço IA (estimativa)
## Custo (D10)
- Tokens acumulados (in/out) · custo $ estimado · nº de interações
- Custo por fase e por agente
- Custo vs. teto definido (se houver) · custo por demanda concluída
## Observabilidade (D43)
- Modelos usados por agente/fase (id do modelo · host) · mix %
- Custo por modelo/modo/stream · latência/interações
- Eficiência: lead time · retrabalho · aceite de 1ª · reclassificações · % aguardando humano
```

### 5.3.5 `audit.md` — rastro de responsabilidade (todos os modos; enxuto→completo)
Append-only. **FAST = enxuto** (não é log raw de input/output — é registro de ação + responsabilidade). **SAFE = completo**.
```markdown
## <data> — <fase> — <ator: humano|agente>
- Ação: <o que foi feito>
- Sob delegação de: <humano responsável>     (chave do D7)
- Decisão/aprovação relacionada: <link decision, se houver>
- [evento/D45] modelo: <id> · tokens: <in/out> · status: <...> · onde-parou: <próximo passo>
- [SAFE] Evidência: <link/arquivo>
```
**Campos mínimos no FAST:** data, ação, sob-delegação-de. Nada além — evita virar a burocracia do AI-DLC.
**Telemetria (D45):** cada entrada é também um **evento contínuo** (timestamp/fase/modelo/status/onde-parou) — alimenta a medição em tempo real, não só no fim.

# FASE 6 — Context & JIT Loading Design

## 6.1 Camadas de contexto
- **Sempre carregado (mínimo):** princípios do Alfred + Risk Mode (regras) + state da demanda atual. Pequeno e fixo.
- **Por fase:** só o artefato/agente daquela fase (Discovery em Inception, Spec em Design, etc.).
- **Por agente:** cada agente carrega só sua def + o que sua fase precisa.
- **Por modo:** FAST carrega o mínimo; SAFE carrega análise de risco, dependências, plano de rollout/rollback.
- **Por stream/produto:** playbook do stream (evolução futura) e contexto do produto só sob demanda.

## 6.2 Quando carregar o quê
| Artefato | Carregar quando |
|---|---|
| spec | entrando em Execution/Validate |
| decisions | revisando passado ou mudando de modo |
| histórico/state antigo | retomando demanda (session continuity) |
| métricas | só em Operation (evolução futura) |
| nada extra | FAST em execução fluida |

## 6.3 Regras anti-hipercontextualização
- Nenhum artefato > ~1 tela sem split.
- 1 fonte de verdade por informação; referenciar, nunca duplicar.
- Agente não lê artefato de fase que não é a sua.
- Contexto crítico (state) nunca é descartado — é a salvaguarda de resiliência.

## 6.4 Context Index (D11) — linkar, não carregar
O Alfred mantém um **índice de contexto** (`index.md`) por sigla (HUB) e por app (`.alfred/index.md`). É um mapa **tema → onde está**, não o conteúdo. Os agentes carregam **o índice + só o(s) link(s) relevantes** ao tema atual (JIT por referência), nunca a pasta inteira.
```markdown
# Index — <SIGLA>
## Temas
- pagamento/split  → demandas: #142, #097 · decisões: D12, D31 · apps: pgto-api
- autenticação     → demandas: #088 · reverse-eng: auth-svc/.alfred/reverse-eng
## Demandas ativas
- #142 split (Design) → hub/PGTO/142/state.md
## Glossário/links estáveis
- contrato de eventos → <link>
```
Regra: ao iniciar uma tarefa, o agente consulta o índice, escolhe os links do tema e **só então** abre esses arquivos. Evita varrer histórico.

**Índice em cascata (anti-inchaço):** o `index.md` da **sigla** aponta para as **iniciativas**; cada iniciativa tem seu **mini-índice** (temas/demandas dela); cada app tem seu `index` local. Carrega-se de cima para baixo, só o ramo necessário — nunca o índice inteiro da sigla de uma vez. Mantém o índice pequeno mesmo em sigla com muitas iniciativas (D11).

## 6.5 Sumarização no fechamento (D11)
Ao concluir a demanda (Operation), o Alfred **sumariza o contexto**: gera um `summary.md` curto (o que foi feito, o que mudou/evoluiu, decisões-chave com links, débitos) e **atualiza o `index.md`** da sigla. O histórico detalhado é arquivado, não carregado. Em demandas futuras, carrega-se o `summary` + índice — contexto menor, mas com ponteiro para o detalhe se precisar.
- **Por demanda:** `summary.md` (1 tela) substitui a leitura dos artefatos completos no futuro.
- **Por sigla:** o `index.md` acumula os temas/evoluções — vira a memória de longo prazo enxuta do sistema.
- Princípio: **detalhe arquivado e linkado > detalhe sempre carregado.**

## 6.6 Anti-hipercontexto nos artefatos do projeto
- Artefatos **referenciam** outros (link), não os transcrevem.
- `decisions`/`audit` são append-only de entradas curtas, não narrativas longas.
- Quando um artefato cresce, split por fase/tema e registra no índice.
- O que importa no longo prazo vai para `summary`/`index`; o resto é arquivo frio.

## 6.7 Carregamento de skills (D12)
Regra-mãe: **nunca carregar todo o contexto — só o necessário.** Vale para skills em todos os níveis.
- Início da demanda: o Orchestrator lê o **registro de skills** (`skills.md`) e propõe as relevantes pelo gatilho (stream/tipo · Risk Mode · fase). Humano confirma a ativação.
- O agente da fase carrega **só as skills ativadas** (JIT por referência), via link — nunca o catálogo inteiro.
- **JIT dentro da skill:** mesmo a skill ativada não é lida inteira — cada skill tem seu próprio índice/seções e carrega-se **só a seção que casa com a tarefa atual**. Skill grande → split por seção, igual aos demais artefatos (D11).
- Skills externas: o ponteiro (repo/URL/sigla) é resolvido só na ativação; lê-se só o trecho necessário, sob demanda.
- Ao fechar: o `summary` registra quais skills/seções foram usadas e o que produziram (rastro sem recarregar o detalhe depois).

**Resolvido (ver `skills/skills.md`):** versão de skills externas — **pin por padrão** (resolve para branch+commit na ativação e registra no `state`/`audit`, congelado na demanda — reprodutibilidade, coerente com D26/D41). Opt-in **track-latest** re-resolve a cada ativação mas ainda registra o commit resolvido no `audit`; re-checa o ref como a staleness do reverse-eng (D21). Sem host para resolver o ref → humano fornece e Alfred registra o ref não resolvido (não inventa).

## 6.8 Boot de sessão (D16) — passo a passo
Ordem que o host segue ao iniciar (1x por sessão):
1. **Boas-vindas** (mensagem curta; só na 1ª interação da sessão).
2. **Detectar repo:** HUB (`context.md` + iniciativas) · APP (`.alfred/` + código) · Framework (`principles.md`/`agents/`) · senão, perguntar.
3. **Atualizar framework (se CLI):** `pull` do repo do framework → se mudou, avisar em 1 linha o que foi atualizado; se não há CLI/acesso, registrar "não verificado".
4. **Carregar contexto JIT (anti-hipercontexto):**
   - lê o `index` do repo detectado;
   - **lista as demandas abertas da sigla** (em andamento/em espera/bloqueada) com última atividade (D28) e pergunta qual retomar; senão, trata como **nova demanda**;
   - ao retomar → **resume** pelo `state` (mostra toolbar + "o que falta");
   - abre só os links do tema atual + skills ativas.
5. **Confirmar com o humano** o ponto de partida (continuar / nova / revisar) antes de agir.
Regra: o boot **nunca** carrega tudo — só index + state + o necessário (D11). O resto é sob demanda.

# FASE 7 — File Architecture (3 camadas / 3 repos)

> Markdown agnóstico, evolutivo. **Não criar até autorização.** Ver D8 para a divisão de responsabilidade entre camadas.

## 7.1 Repo do Framework (modular sem prefixo — variante C/D39; fonte única referenciada, não copiada — D15)
Contém o Alfred em si — sem dados de iniciativa.
```
alfred/
│
├── core/                     # kernel + entrada (invariantes)
│   ├── README.md             #   o que é / como usar
│   ├── welcome.md            #   boas-vindas, voz do mordomo (D16/D17)
│   ├── boot.md               #   detecção HUB/APP → pull → carga JIT (D16)
│   ├── principles.md         #   princípios + antiobjetivos
│   ├── risk-mode.md          #   checklist, escala, overrides (seletor — D31/2.x)
│   ├── architecture.md       #   as 3 camadas (D8)
│   ├── model-policy.md       #   modelo por fase/agente/lane (D46) — tunável
│   └── glossary.md           #   terminologia: sigla/iniciativa/demanda/unit/lane…
│
├── rules/                    # AI-DLC customizado = MOTOR (D1/D38); agnóstico (sem AWS, A.3)
│   ├── common/               #   anti-alucinação/overconfidence (D41) · question-format (D18) · content-validation · session-continuity · terminology
│   ├── demand-types/         #   STREAMS × tipos (D5/3.6)
│   │   ├── produto.md
│   │   ├── operacional.md    #     inclui incidente/Execution-first (D6/D34)
│   │   └── engineering.md    #     refactor/upgrade/migração/perf… (3.6)
│   ├── lanes/                #   MODOS do Risk Mode (governança) — DoD/checkpoints (D25)
│   │   ├── fast.md
│   │   ├── standard.md
│   │   └── safe.md
│   ├── lifecycle/            #   passos por FASE (D19/D38), carregados JIT
│   │   ├── inception/        #     requirements (D18) · duas lentes (D33)
│   │   ├── design/           #     spec/SDD · sub-atividades (app-design/units/NFR) (D19/D24/D29)
│   │   ├── execution/        #     Planning+Generation · SOLID/template (D19/D35/D36)
│   │   ├── validation/       #     build-and-test · DoD (D19/D25)
│   │   └── operations/       #     release · summary · post-mortem (D11/D19)
│   └── agents/               #   orchestrator · discovery · spec-design · reviewer · metrics (D2)
│
├── skills/                   # capacidades plugáveis, opt-in/JIT (D12/D22/D36)
│   ├── skills.md             #   registro + contrato (nome · propósito · gatilho · I/O · link)
│   ├── coding-standard.md    #   SOLID base (D36)
│   ├── lang-<linguagem>.md   #   padrão por linguagem (override D22/D36)
│   └── security-review.md …  #   internas; externas = ponteiros p/ outros repos
│
├── connectors/               # ACESSO a sistemas externos (opcional, D3/D14)
│   ├── connectors.md         #   registro + CONTRATO por tipo (D40): observability/vcs/tracker
│   ├── observability-cloudwatch.md  # acesso CloudWatch p/ investigação (D34)
│   ├── git.md                #   branch/PR (D23)
│   ├── tracker.md            #   id-demanda do tracker (D20)
│   └── notification-email.md #   envio de artefatos+logs p/ email (D44)
│
├── metrics/                  # observabilidade do Alfred (D10/D32/D43)
│   ├── metrics.md            #   o que medir (custo, modelos, eficiência, qualidade)
│   ├── baselines.md          #   réguas tunáveis (D32)
│   └── insights.md           #   agregações/rollup + insights (mix de modelos, custo, tendência — D43)
│
├── knowledge/                # POLÍTICAS/guardrails da ORG (D42) — preenchido na adoção; entregue vazio/agnóstico
│   ├── notification.md       #   destino de email + gatilho (D44): adriano.vilela-costa@itau-unibanco.com.br · canal A DEFINIR
│   └── <politica>.md         #   ex: repo-via-issue · acessos · naming · ambientes
│
├── templates/                # moldes dos artefatos
│   ├── hub/                  #   index · initiative · state · problem · inception-input · tech-inception · requirements · risk · decision · audit · metrics · summary
│   ├── app/                  #   index · spec · investigation · audit · metrics · reverse-eng
│   └── email.md              #   padrão de notificação [Alfred-Framework] (D44)
│
├── scripts/                  # automação OPCIONAL (D3 — tudo degrada p/ manual)
├── docs/                     # documentação humana
└── examples/                 # sigla/iniciativa/demanda de exemplo (onboarding D30, piloto)
```

## 7.2 Repo HUB (1 por sigla → iniciativas → demandas)
Cada sigla tem seu HUB. Fonte de verdade do `state`. Hierarquia: sigla → iniciativa → demanda.
```
alfred-docs-hub/                   # HUB da sigla (1 repo por sistema)
├── context.md                     # contexto do sistema + repos de app + repos de template/referência (D35)
├── index.md                       # Context Index (D11): tema→localização, iniciativas/demandas
├── skills.md                      # skills ativas p/ a sigla (D12): internas + externas (ponteiros)
├── metrics-rollup.md              # agregação de métricas/insights da sigla (D43)
├── knowledge/                     # base de conhecimento da SIGLA/SQUAD (D42): políticas/regras específicas
└── <iniciativa>/                  # iniciativa (pode ser multirepo)
    ├── initiative.md              # objetivo da iniciativa + repos/apps envolvidos
    ├── index.md                   # mini-índice da iniciativa (temas/demandas) — cascata D11
    └── <id-demanda>/
        ├── state.md               # FONTE DE VERDADE (fase, modo base, responsável, links p/ apps)
        ├── problem.md             # problema, objetivo, escopo/fora de escopo
        ├── inception-input.md     # Inception de negócio importada (Produto/agente externo) — quando houver (D33)
        ├── tech-inception.md      # Inception técnica do Alfred: sistemas afetados, integrações, riscos téc. (D33)
        ├── requirements.md        # intent analysis + perguntas (múltipla escolha + [Answer]:) + consolidação (D18)
        ├── risk.md                # Risk Mode: modo base da demanda + overrides por app (2.11)
        ├── decisions.md           # decisões de iniciativa/negócio (Std/SAFE)
        ├── audit.md               # rastro de responsabilidade
        ├── metrics.md             # métricas consolidadas da demanda
        └── summary.md             # gerado no fechamento (D11): o que evoluiu + links
```

## 7.3 Repo da Aplicação (técnico, por repo; 1 demanda pode tocar N apps)
```
<app-repo>/                        # repo da aplicação (sigla)
├── (código da aplicação)
└── .alfred-docs-app/
    ├── index.md                   # Context Index local (D11): tema→arquivo no repo
    ├── reverse-eng/               # engenharia reversa daquela app (estável)
    └── <id-demanda>/              # mesmo id que no HUB (correlação)
        ├── spec.md                # spec técnica para ESTE repo (Std/SAFE)
        ├── investigation.md       # análise exploratória de incidente: erro→causa→repos (D34)
        ├── audit.md               # audit técnico (ações no código)
        └── metrics.md             # métricas técnicas do repo (lead time, defeitos)
```

## 7.4 Correlação e regras
- **`id-demanda` compartilhado** entre HUB e cada app → o `state` (HUB) linka os `.alfred/<id-demanda>/` das apps tocadas.
- **Fonte de verdade do progresso:** sempre o `state` no HUB. App guarda só técnico.
- **Criar arquivo:** quando responsabilidade nova e estável surge (não para efêmero).
- **Dividir:** arquivo > ~1 tela ou 2+ responsabilidades.
- **Arquivar:** demanda fechada → marcar no `state` e congelar a pasta (HUB e apps).
- **Evolução futura:** playbooks por stream, dashboards de métricas, automação de coleta.

# FASE 8 — Implementation Plan

> **Não executar sem autorização explícita do usuário.**

## 8.1 Ordem de criação
**Camada 1 — Repo do Framework (primeiro; fonte única referenciada, ver D15):**
1. `README.md` + `principles.md` — fundação conceitual.
2. `architecture.md` — as 3 camadas (D8).
3. `risk-mode.md` — coração do Alfred (checklist+escala+overrides).
4. `lifecycle.md` — as 5 fases.
5. `templates/hub/` e `templates/app/` — para uso imediato.
6. `agents/` (orchestrator, discovery, spec-design, reviewer, metrics).

**Camada 2/3 — instanciação:**
7. Criar o **HUB de 1 sigla** + estrutura de demanda.
8. Inicializar `.alfred/` em 1 **repo de app** daquela sigla (incl. reverse-eng se brownfield).
9. Demanda-piloto real ponta a ponta (1 sigla, 1+ app), validada nos hosts-alvo (ao menos DEVIN e Claude CLI).

## 8.2 Conteúdo mínimo por arquivo
Cada arquivo nasce com o conteúdo já desenhado nas Fases 1–6 deste plano (condensado), nada além.

## 8.3 Critérios de aceite
- Uma demanda real é conduzida ponta a ponta em cada modo (FAST e Standard no mínimo), com `state` no HUB e artefatos técnicos no repo da app.
- Uma demanda que toca 2 apps mantém 1 `state` no HUB linkando os 2 `.alfred/<id>/`.
- Um incidente simulado roda no fluxo Execution-first com post-mortem.
- Retomar a demanda após "perder contexto" funciona só lendo o `state` (HUB).
- Nenhum arquivo passa de ~1 tela.

## 8.4 Checklist de validação
- [ ] Risk Mode classifica corretamente 3 demandas-exemplo (1 por modo).
- [ ] Overrides duros disparam em demanda crítica.
- [ ] FAST não exige spec formal.
- [ ] SAFE gera decisions + audit completo; FAST/Standard geram audit enxuto.
- [ ] State (HUB) permite retomada e correlaciona artefatos das apps.

## 8.5 Riscos e próximos passos
- **Risco:** Alfred virar doc não usado → mitigar com demanda-piloto imediata.
- **Risco:** Risk Mode degenerar → revisar % de modos após 10 demandas.
- **Risco:** drift entre `state` (HUB) e artefatos das apps → o Orchestrator valida links a cada handoff.
- **Próximo passo:** ao aprovar, criar a Camada 1 (repo do Framework) na ordem 8.1.

---

# APÊNDICE A — Diff conceitual AI-DLC → Alfred
Mapa do que vem do AI-DLC (`D:\Projetos\aidlc-workflows`) para a implementação. Três baldes: **Reaproveitar** (conceito serve como está), **Adaptar** (customizar), **Cortar** (não entra).

## A.1 Reaproveitar (quase como está)
- **session-continuity** → retomada por `state` (resiliência). Núcleo do boot (D16).
- **question-format-guide** (`[Answer]:` + múltipla escolha + "Other") → perguntas da Inception (D18) e de decomposição (D24).
- **requirements-analysis** (intent analysis + gate + detecção de contradição) → Inception (D18).
- **code-generation** padrão Planning+Generation + checkboxes + **brownfield in-place** + automation-friendly → Execution (D19).
- **two-level checkbox tracking** (plano + state) → progresso/toolbar (D9).
- **completion message** 2 opções + **NO EMERGENT BEHAVIOR** → checkpoint HITL padronizado (3.7/D25).
- **reverse-engineering** (análise pesada do brownfield) → S1/D21 (com carimbo de commit p/ staleness).
- **extensions opt-in** (carrega só o que o usuário ativa) → mecanismo das **skills** (D12).
- **overconfidence-prevention** → reforça "só mexer com certeza" (S1/D21).
- **ascii-diagram-standards** → base do Process Toolbar ASCII (D9).
- **content-validation** (validar antes de escrever) → manter, em versão leve.

## A.2 Adaptar (customizar para o Alfred)
- **3 fases (Inception/Construction/Operations)** → **5 fases** (Construction vira Design+Execution+Validate; Operations vira real).
- **depth-levels** (detalhe adaptativo) → **Risk Mode** explícito (D1.4/D19), nunca pular fase.
- **stages ALWAYS/CONDITIONAL** → as 5 fases nunca pulam; o condicional vira **sub-atividades de Design** (application-design, units, functional-design, NFR, infrastructure).
- **workspace-detection** → **boot/detecção HUB-APP** (D16) + detecção brownfield.
- **units-generation** → **D24** (units como checklist no `state`, sem multiplicar demandas; reusa as perguntas `[Answer]`).
- **workflow-planning** → **plano de execução** dentro do Design (impacto, skip/execute, sequência, paralelização D13).
- **build-and-test** → fase **Validate** (estratégia de testes por necessidade + gate).
- **aidlc-state.md** (1 arquivo central) → **`state.md` por demanda no HUB** (D8) + progresso (D9).
- **welcome-message** → boas-vindas na **voz do mordomo** (D16/D17).
- **diretório `aidlc-docs/` co-localizado** → **3 camadas** (Framework / HUB por sigla / app `.alfred/`) (D8/D15).
- **Operations (placeholder)** → **Operation real** (release, métricas, summary/D11, post-mortem).

## A.3 Cortar (não entra no Alfred)
- **audit.md raw** (log verbatim de todo input) → vira **audit enxuto** focado em ação+responsabilidade (D4/D7). O log cru é cortado.
- **Aprovação obrigatória em TODO stage** → só Standard/SAFE têm checkpoint; FAST é autonomia delegada (D7). Corta o gate universal.
- **Conteúdo AWS-específico** (CDK, Brazil build, Lambda, Smithy, Bedrock, CloudFormation) → **genérico/cortado** (Alfred é agnóstico de stack/cloud — D3). Vira skill opcional se alguém quiser.
- **Naming/estrutura de 3 fases** e mensagens com emojis fixos → adaptados ao estilo do Alfred.
- **Compliance/gates regulatórios** como parte do core → fora (D4); audit cobre rastreabilidade.

## A.4 Implicação para a Camada 1
Os arquivos do Framework (7.1) nascem **condensando A.1+A.2**, já sem o que está em A.3. Em especial:
- `lifecycle.md` = 5 fases (A.2) com sub-atividades condicionais herdadas.
- `risk-mode.md` = depth-levels formalizado.
- `agents/discovery.md` = requirements-analysis + question-format (A.1).
- `agents/spec-design.md` = application-design/units/NFR como sub-atividades (A.2).
- `agents/reviewer.md` = code-generation review + build-and-test (A.1/A.2).
- `templates/` = versões enxutas, sem audit raw nem AWS (A.3).

---

# APÊNDICE B — Sumário executivo das decisões (D1–D26)
Consolidação de referência rápida (mapa de 1 tela de tudo que foi decidido acima).

| # | Decisão | Essência |
|---|---|---|
| D1 | Alfred = AI-DLC customizado | motor é o AI-DLC adaptado (5 fases, Risk Mode, audit enxuto), não stock nem do zero |
| D2 | Agentes = artefatos de especialidade | inclui orquestração multi-agente e métricas dos agentes |
| D3 | Markdown agnóstico (invariante forte) | tudo degrada p/ markdown/ASCII; automação opcional; portável entre hosts |
| D4 | Rastreio | state sempre · decisions (Std/SAFE) · audit (todos os modos) · Compliance fora |
| D5 | Taxonomia de demandas | 3 streams: Produto · Operacional · Engineering |
| D6 | Caminho de emergência | Operacional crítico = Execution-first + post-mortem obrigatório |
| D7 | Humano no controle | decisão sempre humana e responsável, em todos os modos |
| D8 | 3 camadas / hierarquia | Framework · HUB (1 por sigla) · App; Sigla→Iniciativa→Demanda; demanda single-sigla |
| D9 | Transparência de progresso | toolbar a cada interação (fase X/5 + o que falta) |
| D10 | Custo acumulado visível | tokens + $ + interações no toolbar/metrics |
| D11 | Anti-hipercontexto | Context Index + JIT por referência + sumarização no fechamento; índice em cascata |
| D12 | Skills plugáveis | internas + externas (outros repos), opt-in, JIT |
| D13 | Paralelismo controlado | Orchestrator faz fan-out seguro; merge serializado no state |
| D14 | Execução sem runtime | hosts: DEVIN (CLI/Web), Claude CLI, GitHub Copilot |
| D15 | Distribuição/evolução | HUB só artefatos; framework no repo próprio; adoção central |
| D16 | Boot de sessão | boas-vindas → detectar HUB/APP → pull framework → carga JIT |
| D17 | Persona | Alfred, o mordomo (serve, não manda — encarna o D7) |
| D18 | Inception por requirements | intent analysis + perguntas em arquivo ([Answer]:) + gate |
| D19 | Herança AI-DLC por fase | depth-levels, conditional stages, Planning+Generation, build-and-test, checkpoint padrão |
| D20 | id-demanda | herda do tracker: `<SIGLA>-<numero>` |
| D21 | Staleness do reverse-eng | revalida só se o commit do app divergiu |
| D22 | Precedência de skills | mais restritivo/seguro > mais específico > humano decide |
| D23 | Branch/merge & concorrência | branches protegidas; agente só na branch da demanda; merge = aceite HITL |
| D24 | Demanda × Units | demanda governa; decompõe em N units (checklist no state, paralelizáveis) |
| D25 | DoD por fase × modo | checklist de "pronto" que escala FAST→SAFE; gate de avanço |
| D26 | Carimbo de versão | framework (state) + app (reverse-eng/PR) + demanda (id/branch) |
| D27 | Gatilhos de escalonamento | quando a autonomia FAST deve parar e chamar o humano (torna D7 aplicável) |
| D28 | Estados da demanda e retomada | pausar é normal; boot lista demandas abertas; só cancela por decisão humana |
| D29 | SDD como trava de clareza | invariante: sem DoD de Design (clareza) não entra em Execution; dosado pelo Risk Mode |
| D30 | Onboarding de uma sigla | fluxo de 1ª adoção: referenciar framework → criar HUB → reverse-eng por app → 1ª demanda |
| D31 | Intent analysis → Risk Mode | respostas do D18 pré-preenchem o checklist 2.2; humano confirma |
| D32 | Baselines de métricas | régua tunável p/ detectar degeneração de modo e custo alto; conversa, não gate |
| D33 | Inception em duas lentes | Produto importa Inception de negócio (agente externo); Alfred aplica Inception técnica |
| D34 | Investigação de incidente | nº+descrição → logs (CloudWatch via skill) → erro→repos → causa; agnóstico (skill, não core) |
| D35 | Repos de template/referência | Alfred pergunta se há templates e espelha o padrão da casa no código; ponteiro, JIT |
| D36 | Padrão SOLID + skill de linguagem | coding-standard base (SOLID); skill da linguagem sobrepõe (D22); Reviewer valida |
| D37 | Granularidade de persistência | grava/commita o state a cada passo/fase/checkpoint → retomada sem recomeçar |
| D38 | AI-DLC mora no Framework | motor customizado em `alfred-rules/`; agnóstico; carregado JIT |
| D39 | Layout modular do Framework (sem prefixo) | core · rules (common/demand-types/lanes/lifecycle/agents) · skills · connectors · metrics · templates · scripts · docs · examples |
| D40 | SOLID na arquitetura | core/rules/skills/connectors = SRP+OCP; famílias substituíveis (L); JIT=ISP; regras dependem de contrato, não do concreto (DIP) |
| D41 | Anti-alucinação (lei suprema) | não inventar nada; na dúvida parar e perguntar; fundamentar antes de afirmar; vale em todos os modos |
| D42 | Base de conhecimento / políticas | guardrails sempre-em-vigor (≠ skill); 3 escopos: org (framework) · sigla/squad (HUB); org manda, squad endurece |
| D43 | Observabilidade do Alfred | auto-medição: modelos usados, custo, eficiência; rollup demanda→sigla→org; dado já, dashboards depois |
| D44 | Destino da saída + email | saída versionada (HUB·App); email só em pontos estratégicos (não por interação), padrão [Alfred-Framework], anexos; auto/transparente por config (registrado no audit) |
| D45 | Telemetria contínua | mede durante as fases (eventos por passo/checkpoint): uso, onde parou, modelo, custo, tempo — não só no fim |
| D46 | Política de modelos por etapa | risco(lane)=PISO + etapa ajusta; declarada + sugestão automática; troca é DECLARADA à pessoa; usuário pode escolher/trocar (avisa se abaixo do piso); humano ratifica |
| D47 | Política de idioma | interações pt-BR · arquivos do Framework em inglês · docs/artefatos (HUB/App) pt-BR |

---

# APÊNDICE C — Passos por fase (`rules/lifecycle/*`)
Especificação dos passos operacionais de cada fase. Todos sujeitos à lei suprema (D41: na dúvida, parar e perguntar) e escalados pela lane (D25). "[x]" = checkbox no plano/state (D9/D37).

## C.1 inception/
1. Detectar stream/tipo (D5) e, se **Produto**, ingerir `inception-input` externo (D33) — não refazer discovery de negócio.
2. **Intent analysis** (clareza/tipo/escopo/complexidade — D18).
3. Produzir **`tech-inception`** (lente técnica: sistemas/apps afetados via reverse-eng, integrações, riscos técnicos — D33).
4. Gerar **perguntas de requirements** em arquivo (múltipla escolha + `[Answer]:`, D18) → **gate** aguarda respostas → detectar contradições.
5. Pré-preencher e **propor Risk Mode** (intent→checklist, D31); humano confirma em Std/SAFE (D2.10).
6. Consolidar `problem`/`requirements`; registrar riscos; **DoD Inception** (D25) → checkpoint.

## C.2 design/
1. Carregar requirements + tech-inception (JIT).
2. **Solution shaping** + alternativas (SAFE) → `spec` (SDD) + critérios de aceite (D29).
3. Sub-atividades **por gatilho** (D19): application-design / units-generation (D24) / functional-design / NFR / infrastructure.
4. **Plano de execução** (impacto, skip/execute, sequência, paralelização D13) + plano de teste.
5. Confirmar **template** aplicável (D35) e padrão **SOLID/linguagem** (D36).
6. Registrar `decisions`; **revalidar Risk Mode**; **DoD Design** → checkpoint (aprovação da spec).

## C.3 execution/
1. Carregar `spec` + template + coding-standard ativo (JIT).
2. **Planning:** plano numerado com checkboxes (fonte única, D19) → aprovação (Std/SAFE).
3. **Generation:** passo a passo / **loop por unit** (D24); **brownfield in-place** (nunca `arquivo_v2`); espelhar template (D35) + SOLID (D36).
4. Commit na **branch da demanda** a cada passo (D23/D37); atualizar `state`+`audit`; **gatilhos de escalonamento** vigiados (D27).
5. Revisão técnica (Reviewer); **DoD Execution** → PR pronto.

## C.4 validation/
1. Rodar estratégia de testes por necessidade (unit/integração/perf/e2e/contrato/segurança, D19).
2. Reviewer valida vs `spec` **e** vs SOLID/coding-standard (D36); checklist de aceite; regressão.
3. Evidências (Std/SAFE); **DoD Validation** → aceite.
4. **Merge do PR na develop = aceite HITL** (branch protegida, D23).

## C.5 operations/
1. Release / nota (escala por modo).
2. Coletar `metrics` (D10) + checar baselines (D32).
3. **`summary` + atualizar `index`** (sumarização de fechamento, D11).
4. Se veio de emergência: **post-mortem** obrigatório (D6/D34).
5. **Enviar artefatos + logs** ao email configurado (knowledge) — **automático/transparente** se for ponto+destino configurados (D44); registrar envio no `audit`. (Pede confirmação só se fugir da config.)
6. Registrar débitos/ações preventivas (viram novas demandas); fechar `state` (D28).

---

# APÊNDICE D — Agentes completos (`rules/agents/*`)
Cada agente segue a estrutura 4.6. Todos obedecem D41 (não inventar / parar e perguntar) e comunicam pelo `state` (barramento, D40-DIP).

## D-1 orchestrator
- **Fase:** todas. **Gatilho:** boot e cada handoff.
- **Faz:** lê `state`; decide próximo agente (fase/stream/modo); **seleciona o modelo por etapa** (model-policy, D46); garante checkpoints HITL; monta **toolbar** (D9); valida links HUB↔App; gerencia **paralelismo** (D13, merge serializado); mantém `state`+`audit` coerentes.
- **Não decide** nada de domínio; não executa; não aprova.
- **JIT:** core + `state` + índice; carrega regra/fase só ao rotear.
- **I/O:** lê tudo via índice; escreve `state` (progresso) + `audit`.

## D-2 discovery
- **Fase:** Inception. **Faz:** ingere `inception-input` (Produto, D33); intent analysis; `tech-inception`; perguntas de requirements (D18) + gate; propõe Risk Mode (D31); levanta riscos.
- **Não:** fecha escopo; refaz discovery de negócio.
- **I/O:** lê inception-input/reverse-eng/knowledge; escreve `problem`/`requirements`/`tech-inception`/`risk`.

## D-3 spec-design
- **Fase:** Design. **Faz:** solution shaping + alternativas; `spec`+critérios (D29); sub-atividades por gatilho (D24); plano de execução/teste; confirma template (D35) e SOLID (D36); registra `decisions`.
- **Não:** aprova arquitetura (Tech Lead aprova).
- **I/O:** lê requirements/tech-inception/knowledge/templates; escreve `spec`/`decisions`/plano.

## D-4 reviewer
- **Fase:** Execution + Validate. **Faz:** revisa código vs `spec` **e vs SOLID/coding-standard** (D36); checklist de aceite; aponta regressão/risco; prepara evidências.
- **Não:** dá aceite final (QA/PM); não faz merge (humano, D23).
- **I/O:** lê spec/código/coding-standard; escreve revisão/evidências em `audit`/validação.

## D-5 metrics
- **Fase:** Operation. **Faz:** coleta `metrics` (D10) via connector/host ou manual; checa baselines (D32); gera/atualiza `summary`+`index` (D11); custo acumulado.
- **Não:** decide release.
- **I/O:** lê audit/PR/connectors; escreve `metrics`/`summary`/`index`.

---

# APÊNDICE E — Contratos (D40)
Cada família plugável declara um contrato no seu registry; as regras dependem do **contrato/papel**, nunca do concreto (DIP). Tudo markdown; "interface" = seções obrigatórias do arquivo.

## E-1 connector (`connectors/connectors.md`)
Cada connector declara: `tipo`, `ativação` (como configurar/credencial), `operações`, `degradação` (o que fazer sem acesso → D3).
Contratos por tipo:
- **observability:** `get_logs(query, janela) → entradas` · `get_alarms()` — degradação: humano fornece logs (D34).
- **vcs:** `criar_branch(id)` · `commit(msg)` · `abrir_PR(base,head)` — NUNCA merge em protegida (D23).
- **tracker:** `get_demand(id) → {título,descrição,tipo}` · `abrir_issue(...)` — origem do `id-demanda` (D20); usado p/ "repo via ISSUE" (D42).
- **notification:** `enviar(destino, assunto, anexos)` — email de artefatos+logs (D44); destino vem do knowledge (registrado: adriano.vilela-costa@itau-unibanco.com.br); **canal A DEFINIR** (SMTP/Graph/SES/MCP) — adapter plugável; **auto/transparente nos pontos+destino configurados** (autorização durável); confirma só se fugir da config (D41). Degradação: lembrar o humano de enviar manual.
- **telemetry (evolução futura):** `enviar_eventos(lote) → ack` — envia logs/eventos (D45) à API central de observabilidade; plugável. Degradação: eventos ficam no `audit`/`metrics` (markdown) até a API existir.

## E-2 skill (`skills/skills.md`)
Cada skill declara: `nome`, `propósito`, `gatilho` (stream/tipo·modo·fase), `entradas`, `saída esperada`, `link`, `seções` (p/ JIT interno D12). Precedência D22.

## E-3 lane (`rules/lanes/*`)
Forma uniforme por modo: `DoD por fase` (D25) · `checkpoints HITL` (D2.6) · `artefatos mínimos` (D2.7) · `rastreio` (D4). O lifecycle pede "a lane ativa", não um modo fixo.

## E-4 agent (`rules/agents/*`)
Forma uniforme (4.6): `fase-dona` · `gatilho` · `faz` · `não-decide` · `JIT` · `lê/escreve no state` · `handoff`. Substituível desde que respeite o contrato de I/O.

## E-5 demand-type (`rules/demand-types/*`)
Declara: `tipos` cobertos · `ênfase de fase` · `sub-atividades típicas` · `tendência de modo` · `caminho especial` (ex: operacional→Execution-first D6). Referencia connector/skill por **papel**, não nome.

> Regra de ouro (DIP): trocar CloudWatch→Datadog = novo connector `observability`, **sem tocar** `demand-types/operacional`.

---

# APÊNDICE F — Convenções de código, PR e testes
Materializa SOLID/template (D35/D36) e o aceite por merge (D23). São **defaults** — podem ser endurecidos por knowledge da org/sigla (D42, precedência > defaults).

## F-1 Código
- Segue **template aplicável** (D35) + **coding-standard/SOLID** ativo (D36, override por skill de linguagem D22).
- **Brownfield in-place** (nunca `arquivo_v2`); mudanças pequenas e rastreáveis.
- Código **automation-friendly** (`data-testid` etc., herdado AI-DLC).
- Não inventar API/lib/caminho (D41): verificar no reverse-eng/repo antes.

## F-2 Branch e PR (D23)
- Branch por demanda: `alfred/<id-demanda>` (ou `alfred/<pessoa>/<id>`).
- **Commits pequenos** a cada passo/unit (D37) — mensagem referencia o `id-demanda`.
- **PR contra develop**; descrição linka `state`/`spec`; **merge só por humano** (= aceite, D23).
- PR pequeno por demanda; se cresceu → reavaliar escopo (D27).

## F-3 Testes por modo (Validate, D25)
| Modo | Mínimo de testes |
|---|---|
| **FAST** | testes locais relevantes passam; sem suíte formal |
| **Standard** | unit + **regressão** dos pontos tocados + critérios de aceite ✓ |
| **SAFE** | + integração/contrato/e2e/performance/segurança conforme aplicável + evidências formais |
- Estratégia escolhida **por necessidade** (não rodar tudo sempre); refactor/migração priorizam **regressão**; performance exige **baseline antes/depois** (3.6).
- Reviewer valida testes contra a `spec`; falha repetida → parar e escalar (D27).
