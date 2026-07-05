# Notas de pesquisa — Anthropic × decisões do Alfred 2.0.0

> Documento de apoio à decisão (pt-BR). Fontes: artigos de engenharia e pesquisa da Anthropic, lidos em 2026-07-05. Cada seção mapeia o achado ao que ele **valida** no Alfred e ao que **recomenda mudar/decidir** — entradas alimentam `implementation-plan-2.0.0.md`.

## 1. Building Effective Agents (research, dez/2024)
- Workflows (caminhos predefinidos) vs agents (LLM dirige o processo); começar simples; só adicionar complexidade quando **melhora medida**.
- Padrões compostos: routing, parallelization, orchestrator-workers, evaluator-optimizer.
- **Valida:** Alfred é um "workflow governado" — Orchestrator roteia (routing), units em paralelo (orchestrator-workers, D13), Reviewer (evaluator-optimizer). Manter **5 agentes**; não criar PM/Tech-Lead agents (decisão são humanos, D7).
- **Recomenda:** qualquer item da Wave 8 só entra se uma métrica (Wave 6) provar ganho — "add complexity only when it measurably improves outcomes".

## 2. Effective Context Engineering for AI Agents (set/2025)
- JIT com "identificadores leves" (paths/links) em vez de pré-carregar; compaction ao se aproximar do limite; **structured note-taking** (memória fora do contexto); sub-agentes retornam resumos condensados (1–2k tokens).
- "Minimal viable context": o menor conjunto de tokens de alto sinal.
- **Valida:** D11 inteiro (índice em cascata, ponteiros, summary no fechamento = compaction), `001-state.md` = note-taking, D13 = sub-agentes com merge serializado.
- **Recomenda:** para W8.3 (memória de decisões), seguir o padrão note-taking: indexar por tema, recuperar sob demanda — nunca carregar histórico inteiro.

## 3. Equipping Agents with Agent Skills (out/2025; padrão aberto em dez/2025)
- Skill = pasta com `SKILL.md` (frontmatter YAML `name` + `description`) + arquivos/scripts; **progressive disclosure em 3 níveis** (metadados → SKILL.md → arquivos referenciados); scripts executáveis em vez de gerar por token; segurança: só instalar de fontes confiáveis, auditar conteúdo.
- **Valida:** o registry do Alfred (`skills/skills.md`) com "sections to load" já pratica progressive disclosure; pin por commit de skills externas alinha com a recomendação de segurança.
- **Recomenda (DH nova):** aproximar o formato das skills do Alfred ao **padrão aberto Agent Skills** (frontmatter `name`/`description`) — ganho de portabilidade entre hosts (Claude Code, Agent SDK, plataforma) sem perder o registry próprio.

## 4. How We Built Our Multi-Agent Research System (jun/2025)
- Multi-agente vence em buscas *breadth-first*; **má opção para coding** (pouco paralelizável, exige contexto compartilhado); custa ~15× tokens de um chat.
- Delegação exige: objetivo, formato de saída, limites e regras de escala explícitos; checkpoints + retomada do ponto de falha; tracing de produção.
- **Valida:** o paralelismo conservador do D13 (só tarefas isoladas, merge serializado) e a persistência granular do D37; o custo visível no toolbar (D10) é ainda mais importante em execução paralela.
- **Recomenda:** no handoff do Orchestrator, incluir **regra de escala** (demanda simples = sem units; complexa = N units com responsabilidades divididas) — hoje implícito no workflow-planning.

## 5. Effective Harnesses for Long-Running Agents (nov/2025)
- Falhas típicas: tentar tudo de uma vez e declarar concluído cedo demais. Antídotos: arquivo de progresso, commits descritivos por passo, **padrão de início de sessão** (verificar diretório → ler git/progresso → escolher próxima feature → rodar baseline → só então implementar); lista de features com status; **proibido remover/editar testes** para "passar".
- **Valida:** boot D16 + `001-state.md` + commit por passo (D37/D23) são exatamente o harness recomendado; checklist de units = feature list.
- **Recomenda:** adicionar a regra "nunca remover/afrouxar teste para satisfazer o gate" ao coding-standard/knowledge (guardrail barato, alto valor).

## 6. Writing Effective Tools for Agents (2025)
- Consolidar operações em ferramentas de alto nível (ex.: `schedule_event` em vez de 3 chamadas); namespacing consistente; respostas com formato `concise`/`detailed`; erros **acionáveis** (dizem como corrigir); avaliar ferramentas com transcripts reais e iterar usando o próprio agente.
- **Recomenda (W7):** ao implementar o primeiro adapter real, acrescentar ao contrato de connector duas seções: **response format** (conciso por padrão) e **error guidance** (erro diz o próximo passo). Avaliar o adapter com transcripts antes de `active`.

## 7. Claude Code Best Practices (docs vivas)
- Regra mestra: contexto degrada quando enche — instruções persistentes **enxutas** ("would removing this cause mistakes? if not, cut"); explore → plan → code → commit; **verificação com evidência** que o agente pode rodar (teste/build/screenshot); revisão adversarial em **contexto fresco**; "interview me" para gerar spec antes de executar.
- **Valida:** as 5 fases; `validation-evidence`; perguntas em arquivo (D18) ≈ interview-to-spec; Reviewer separado do executor.
- **Recomenda:** (a) quando o host suportar sub-agentes, o Reviewer deve rodar em **contexto limpo** (só diff + critérios, sem o raciocínio de quem escreveu); (b) manter knowledge/guardrails podados como um CLAUDE.md — instruções demais são ignoradas.

## 8. Code Execution with MCP (nov/2025)
- Carregar centenas de definições de tools no contexto é caro; expor tools como **arquivos descobríveis** (progressive disclosure) e filtrar dados no ambiente de execução economiza ~98% de tokens no exemplo.
- **Valida:** o modelo markdown-first/filesystem do Alfred é a mesma filosofia; MCP = camada de adapter (nunca core), como o Alfred já posiciona.
- **Recomenda (W7):** MCP é forma legítima do primeiro adapter; manter as definições fora do contexto (ponteiros), coerente com D11.

## 9. Demystifying Evals for AI Agents (jan/2026)
- Começar com 20–50 tarefas reais (bugs/falhas viram casos de teste); separar **capability evals** (medem avanço) de **regression evals** (têm que ficar ~100%); graders em 3 camadas (código, modelo, humano); métricas pass@k / pass^k; ler transcripts; evitar grading rígido por sequência de passos.
- **Valida:** os validadores do Alfred são *code-based graders*; os exemplos validados (`examples/`) já funcionam como **suíte de regressão**.
- **Recomenda (W6/W8):** tratar as demandas-exemplo como regression evals formais; para o score de confiança (W8.1) e o classify-risk (W3), calibrar com transcripts reais antes de confiar; medir aceite-de-1ª como pass@1.

## 10. Claude Code Auto Mode (mar/2026)
- Autonomia com classificador revisando **a ação, não o argumento** (remove o raciocínio do agente para ele não "convencer" o revisor); categorias bloqueadas: destrutivo/irreversível, degradação de segurança, cross-boundary (credenciais achadas), bypass de infra compartilhada; **falso positivo sobrevivível** (nega e continua); escalada ao humano após **3 negações consecutivas ou 20 totais**; risco residual declarado.
- **Valida:** os gatilhos de escalonamento do Alfred (D27) cobrem quase 1:1 as categorias; audit por ação (não por narrativa) e o aviso de trade-off do model-policy seguem o mesmo espírito.
- **Recomenda:** adicionar aos escalation-triggers um **limiar numérico** de escalada (N falhas/negações consecutivas → checkpoint humano), hoje descrito como "após N tentativas" sem número.

## 11. Scaling Managed Agents — brain/hands/memory (abr/2026)
- Agente = cérebro (modelo) + mãos (execução/tools) + memória (sessões/estado), **desacoplados porque evoluem em relógios diferentes**; cada peça substituível sem jogar o resto fora.
- **Valida:** é a arquitetura do Alfred dita com outras palavras — brain = modelo do host (D46), hands = connectors/scripts (D14/D40), memory = `state`/HUB (D8/D37). Reforça a decisão de não ter runtime próprio.

## Impacto nas decisões humanas pendentes
| Decisão pendente (plano 2.0.0) | O que a pesquisa indica |
|---|---|
| Nomes de fase EN + apelidos pt-BR | Manter canônico + glossário; instruções persistentes enxutas (item 7) desaconselham duplicar nomenclatura |
| Primeiro adapter real | MCP validado como camada de adapter (itens 6/8); começar por tracker ou vcs com response-format conciso |
| Papéis SRE/Security/FinOps | Item 10 reforça donos humanos para categorias de alto risco → incluir enxuto em SAFE |
| Formato das skills | Aproximar do padrão aberto Agent Skills (item 3) — nova DH sugerida |
| Wave 8 (inteligência) | Só com métrica provando ganho (itens 1/9); começar por score de confiança + regression evals |

## Ajustes sugeridos ao backlog (aprovados em 2026-07-05)
1. **W2+:** guardrail "nunca remover/afrouxar teste para passar no gate" (item 5).
2. **W7+:** seções `response format` e `error guidance` no contrato de connectors (item 6).
3. **W8.1+:** contador **acumulado** de escalada nos escalation-triggers (item 10). *Correção da auditoria:* o limiar de falhas consecutivas já existe (`rules/common/escalation-triggers.md`, "validation fails twice for the same reason" é hard trigger); falta só o contador acumulado por demanda (auto mode usa 20 totais).
4. **DH:** frontmatter compatível com Agent Skills nas skills do Alfred (item 3).
5. **W6+:** formalizar os exemplos como suíte de regressão (regression evals) e medir aceite-de-1ª como pass@1 (item 9).

## Auditoria de aderência (2026-07-05)
Verificação recomendação-por-recomendação contra o repo: **~15 recomendações centrais aplicadas** (JIT/ponteiros, note-taking via `state`, padrão de boot, commit por passo, sub-agentes com merge serializado, audit por ação, categorias de bloqueio ≈ gatilhos D27, procedimento de erro com severidade sem loop, 5 fases, perguntas em arquivo, toolbar, instruções enxutas, brain/hands/memory desacoplados, isolamento multi-demanda, congelamento de versão). Recursos de host (checkpoints/rewind, fan-out headless, context-window awareness) ficam fora por D3/D14 — correto.

### Evoluções adicionais encontradas (além dos 5 ajustes)
| # | Evolução | Fonte | Prioridade sugerida |
|---|---|---|---|
| A | **Guardrail anti prompt-injection para conteúdo externo** — dado vindo de connector/artefato externo (issue, log, doc, inception-input, skill externa) é *dado, não instrução*; instrução embutida em dado externo = gatilho de escalonamento | item 10 (input-layer probe) | **P1** (Wave 1) |
| B | **Enforcement determinístico opcional via hooks do host** — documentar em `hosts/` como ligar validadores existentes como hooks (regras advisórias × hooks determinísticos); degrada (D3) | item 7 | P2 |
| C | Skills podem referenciar scripts executáveis próprios (instruções + código) | item 3 | P2 (junto do ajuste 4) |
| D | Grader baseado em modelo (rubrica LLM-as-judge) para qualidade de spec/summary, calibrado por humano | item 9 | P2 (Wave 8) |
| E | Loop de auto-melhoria com transcripts: retrospectiva de N demandas propõe melhorias em regras/perguntas; humano ratifica (estende o padrão D46) | itens 4/6 | P2 (Wave 8) |
| F | Instruções de compaction mid-demand: o que deve sobreviver à compactação (path do state, arquivos modificados, próximo passo, checkpoint) | itens 2/7 | P1 (3 linhas em session-continuity) |
| G | Disciplina "eval antes de skill": skill nova nasce de lacuna observada + 2–3 casos de teste | item 3 | P2 (Wave 5) |
