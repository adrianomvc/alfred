# Progresso — Otimização de contexto/tokens (revisão de arquitetura 2026-07)

> Log de handoff fechado (pt-BR). Objetivo: qualquer agente (humano ou IA — Claude, Codex, Copilot, DEVIN) audita o que foi feito lendo **só este arquivo** + o plano aprovado. Novas ações entram pelo plano 2.0.0. Branch de trabalho: `alfred/context-optimization`.

## O que é este trabalho
Revisão de arquitetura aprovada pelo dono em 2026-07-08: reduzir o custo fixo de sessão de ~8,2k para ~3,3k tokens (-60%) e o overhead por demanda em ~53%, sem trocar a estratégia JIT (que está correta). Plano completo com diagnóstico, fases e verificação: seção "Plano aprovado" abaixo.

**Decisões do dono registradas (2026-07-08):** as 6 DHs aprovadas — (1) split do welcome.md, (2) adiar risk-mode.md para a Inception, (3) adiar model-policy.md para a seleção de modelo, (4) cheat-sheet da toolbar, (5) contrato de skills enxuto, (6) shims de host gerados de template. Relatório final registrado em `docs/plan/architecture-review-context-2026-07.md`.

## Status por fase
| Fase | Status | Commit |
|---|---|---|
| Pré: corrigir baseline da toolbar (drift do d2b18b7) | ✅ concluída | `fix(toolbar): mirror borderless redesign...` |
| 0 — Higiene (worktrees stale, __pycache__, .gitignore) | ✅ concluída | `chore: remove stale worktrees...` |
| 1 — Single-sourcing (dedup lei suprema, layout, terminologia, gates, README de rules) | ✅ concluída | `refactor(core,rules): single-source...` |
| 2 — Dieta do kernel (welcome split, adiar risk-mode/model-policy, toolbar-quick) | ✅ concluída | `refactor(core): load presentation and policy context JIT` |
| 3 — Metadados (frontmatter em rules/, knowledge/knowledge.md, skills enxutas, generate-registry) | ✅ concluída | `refactor(rules,skills): generate metadata registries` |
| 4 — context-manifest nos 2 runtimes | ✅ concluída | `feat(rules): add context manifest helper` |
| 5 — Shims gerados de template | ✅ concluída | `refactor(hosts): generate shims from template` |
| 6 — Ordenação cache-friendly + baselines em metrics/ | ✅ concluída | `docs(metrics): record context optimization baseline` |
| Relatório architecture-review-context-2026-07.md + índice + backlog | ✅ concluída | `docs(plan): close context optimization review` |

## Feito até agora (detalhe)
9. **Fechamento — relatório + índice + backlog:** criado `docs/plan/architecture-review-context-2026-07.md` com resumo executivo, diagnóstico, estratégias rejeitadas, riscos/trade-offs, arquitetura recomendada, fluxo níveis 0–7, roadmap e recomendação final. Indexado em `docs/README.md` e registrado em `docs/plan/implementation-plan-2.0.0.md` como W1.9/backlog concluído, incluindo as 6 DHs aprovadas em 2026-07-08. Verificação: `python scripts/validators/validate-framework.py -Root .` com 0 erros.
8. **Fase 6 — Cache + medição:** (a) `core/boot.md` ganhou a orientação cache-friendly: carregar kernel estável, índices/registries/manifests, regras/skills e só então `state`/artefatos voláteis. (b) `hosts/README.md` registra a mesma ordem para hosts com prompt cache/persistent context, preservando degradação D3 quando o host não expõe cache. (c) `metrics/baselines.md` registra os baselines arquiteturais antes/depois: início de sessão ~8,230→~3,300 tk, adicional por demanda ~2,630→~2,100 tk, demanda de 5 sessões ~43,800→~20,500 tk. Os números estão marcados como baseline de planejamento, não medição exata de tokenizer de host. Verificação: `python scripts/validators/validate-framework.py -Root .` com 0 erros.
7. **Fase 5 — Shims gerados de template:** (a) adicionado `hosts/_template/shim.md` como corpo comum dos shims e `hosts/_template/hosts.json` como deltas por host (frontmatter, instalação, acesso ao framework, política de modelo, extras de MCP/telemetria). (b) `generate-host-shims.py` gera e checa os 4 entrypoints commitados (`claude-code/SKILL.md`, `devin-cli/SKILL.md`, `github-copilot/copilot-instructions.md`, `codex/AGENTS.md`). (c) Os shims gerados foram compactados e passaram a apontar para `context-manifest`/índices para carregamento JIT; `hosts/README.md` documenta que os entrypoints são gerados, mas continuam commitados para copy/install simples. (d) `validate-framework` inclui os novos arquivos obrigatórios e roda `generate-host-shims --check`. Verificação: `python scripts/validators/validate-framework.py -Root .` com 0 erros.
6. **Fase 4 — context-manifest:** (a) adicionado `scripts/workflow/context-manifest.py` com interface `--phase`, `--lane`, `--demand-type`, `--agent` e `--sub-activity` opcional. (b) A saída é uma lista mínima e ordenada de arquivos: princípios, índices, lei suprema, lifecycle, demand type, lane, phase, agent e sub-atividade quando indicada. (c) `core/boot.md` e `rules/README.md` registram o uso opcional do helper e o fallback manual via `rules/README.md` + `rules/rules-index.md` (D3). (d) Adicionados fixtures para Standard×product×Design, FAST×operational×Execution e SAFE×engineering×Inception em `examples/context-manifest-fixtures/`, com validador chamado pelo `validate-framework`. Verificação: `python scripts/validators/validate-framework.py -Root .` com 0 erros.
5. **Fase 3 — Metadados + registries gerados:** (a) arquivos-folha de `rules/` ganharam frontmatter `name`/`description`/`load`/`triggers` para fase, lane, demand type e agent; `README.md` continua como navegação. (b) `rules/rules-index.md` passou a ser gerado a partir desses metadados. (c) `skills/*` ficaram enxutas: `trigger` e `sections_to_load` foram movidos para o frontmatter, e o corpo mantém `purpose`, `inputs`, `expected output` e a orientação carregada JIT. (d) `skills/skills.md` agora é registry gerado; `validate-skills-registry` valida o novo contrato e rejeita metadados duplicados no corpo. (e) `knowledge/knowledge.md` registra políticas por escopo/gatilho e entrou em `validate-knowledge`. (f) `generate-registry.py` foi adicionado em `scripts/workflow/`, com drift-check no `validate-framework`. Verificação: `python scripts/validators/validate-framework.py -Root .` com 0 erros.
4. **Fase 2 — Dieta do kernel:** (a) `core/welcome.md` ficou só com persona/voz/tom; o bloco visual rico e as regras de degradação foram movidos para `core/presentation/welcome-screen.md`, carregado apenas no momento de renderização. (b) `core/boot.md`, `core/README.md` e `core/presentation/README.md` registram o carregamento JIT da tela de boas-vindas e da toolbar. (c) `core/presentation/toolbar-quick.md` virou o cheat-sheet diário, e `core/presentation/toolbar.md` foi reconciliado com o formato borderless real e com os fixtures. (d) Os 4 shims de host (`hosts/claude-code/`, `hosts/codex/`, `hosts/devin-cli/`, `hosts/github-copilot/`) deixaram de carregar `core/risk-mode.md` no boot; agora carregam JIT na Inception via `rules/lifecycle/inception/sub-activities/risk-mode-proposal.md`. (e) `core/model-policy.md` passou a ser carregado apenas na seleção/troca de modelo. (f) `validate-framework.py` inclui os novos arquivos obrigatórios. Verificação: `python scripts/validators/validate-framework.py` com 0 erros.
3. **Fase 1 — Single-sourcing:** (a) lei suprema canônica só em `core/principles.md`; `rules/common/overconfidence.md` virou stub (ponteiro + gate + "How agents enforce it"); a lista de gatilhos FAST que vivia no overconfidence foi reconciliada em `rules/common/escalation-triggers.md` (novos hard triggers: risco sobe→reclassificar, operação destrutiva, teto de custo/tokens; gate da lei suprema é o 1º gatilho). (b) Layout canônico de artefatos (com filenames exatos) só em `core/architecture.md`; `core/glossary.md` e `rules/common/terminology.md` viram ponteiros. (c) Glossary mantém tabela EN↔pt-BR + ids; terminology só regras de uso + D47. (d) `skills/skills.md` §Discovery reduzido a ponteiro para `knowledge/external-catalogs.md`, que agora declara ser a fonte única dos 4 gates (era referência circular). (e) 5 fases canônicas já estavam em `rules/lifecycle/lifecycle.md`; demais arquivos só citam em 1 linha — nada a mudar. (f) `rules/README.md` desambiguado: "always in force" = lei suprema + DoD da lane; demais `common/` carregam por evento (mapa evento→arquivo adicionado). (g) `validate-links.{py,ps1}`: este log entrou no EXCLUDE (o plano aprovado cita entregáveis futuros; mesmo precedente do conceptual-plan). **Pendência conhecida (pré-existente, verificada no baseline via stash):** alguns exemplos históricos não passam em `validate-demand --strict` (ex.: falta `03-execution/012-execution-plan.md`) — anterior a este trabalho; hoje eles ficam no tier ilustrativo/non-strict até migração explícita.
2. **Fase 0 — Higiene:** removidos os 2 worktrees git stale (`git worktree remove`, ambos limpos/detached) e os `__pycache__/` locais em `scripts/**`. Nenhum `.pyc` estava commitado (`git ls-files`); `.gitignore` já cobre `__pycache__/` e `*.py[cod]` — nada a adicionar. `.claude/`/`.devin/` não são rastreados. Criado este log de handoff (pedido do dono: outra IA pode retomar) e indexado em `docs/README.md`.
1. **Correção de baseline (pré-fase):** o commit `d2b18b7` ("ajuste d toolbar") aplicou o redesign borderless da toolbar no `render-toolbar.py`; os 4 fixtures ficaram para trás, quebrando `validate-toolbar-fixtures`. Fixtures regenerados. Paridade texto/rich/forecast verificada por diff; `validate-framework` 0 erros. **Pendência conhecida:** `core/presentation/toolbar.md` (spec) ainda descreve o formato ANTIGO com bordas — reconciliar na Fase 2 junto com o `toolbar-quick.md`.

## Como auditar ou reabrir
1. Ler este arquivo + a seção "Plano aprovado" abaixo.
2. Conferir `git log --oneline` na branch `alfred/context-optimization` para ver o que já entrou.
3. Para novas ações, abrir item no `docs/plan/implementation-plan-2.0.0.md` em vez de reativar fases já concluídas aqui.
4. Após qualquer ajuste relacionado: `python scripts/validators/validate-framework.py` — 0 erros; commit pequeno.
5. Atualizar este arquivo só se o ajuste mudar o registro histórico do pacote de otimização de contexto.

## Plano aprovado (íntegra)

### Metas numéricas
| Carga | Antes | Depois (alvo) |
|---|---|---|
| Início de sessão | ~8.230 tk | ~3.300 tk (-60%) |
| Adicional por demanda | ~2.630 tk | ~2.100 tk (+1.318 de risk-mode 1× na Inception) |
| Demanda de 5 sessões (overhead de framework) | ~43,8k tk | ~20,5k tk (-53%) |

### Fase 0 — Higiene
Remover `.claude/worktrees/{infallible-mclean-58ed7f,peaceful-shannon-5e7d5a}/` e `__pycache__/` em `scripts/**`; conferir `.pyc` commitados via `git ls-files`; garantir `__pycache__/` no `.gitignore`.

### Fase 1 — Single-sourcing
1. Lei suprema canônica em `core/principles.md`; `rules/common/overconfidence.md` vira stub (~500 B) com ponteiros + "How agents enforce it". Reconciliar as 2 listas de gatilhos em `rules/common/escalation-triggers.md` (sobreposição ~70%).
2. Layout de artefatos canônico só em `core/architecture.md`; `core/glossary.md` e `rules/common/terminology.md` viram ponteiros.
3. Glossary mantém tabela EN↔pt-BR + ids; terminology só regras de uso + D47.
4. `skills/skills.md` §Discovery → 2 linhas + ponteiro para `knowledge/external-catalogs.md`.
5. 5 fases canônicas em `rules/lifecycle/lifecycle.md`; lanes em `rules/README.md`; demais arquivos só referenciam.
6. Desambiguar `rules/README.md`: "always in force" = overconfidence (stub) + DoD da lane; demais common/ por gatilho.

### Fase 2 — Dieta do kernel (DHs 1–4 aprovadas)
1. `core/welcome.md` fica só persona/voz/tom (~1,2 KB); bloco rich + degradação → novo `core/presentation/welcome-screen.md` (carregado só ao renderizar). Registrar em `core/README.md`.
2. Remover leitura eager de `core/risk-mode.md` dos 4 shims; JIT via `rules/lifecycle/inception/sub-activities/risk-mode-proposal.md`.
3. `core/model-policy.md` carregado só na seleção/troca de modelo.
4. Novo `core/presentation/toolbar-quick.md` (~1 KB); reconciliar `toolbar.md` com o formato borderless real.
5. `core/boot.md` aponta persona + screen condicionalmente. Adicionar arquivos novos a `REQUIRED_PATHS` nos 2 validate-framework.

### Fase 3 — Metadados + registries gerados (DH-5 aprovada)
1. Frontmatter YAML nos arquivos-folha de `rules/`: name, description, `load:`, `triggers: {phase, lane, demand-type, agent}`.
2. Novo `knowledge/knowledge.md` (registry: scope + trigger por policy).
3. Skills: remover `## name`/`## link` do corpo; `trigger`/`sections to load` para o frontmatter; reescrever REQUIRED_SECTIONS em `validate-skills-registry.{py,ps1}`.
4. Novo `scripts/{powershell,python}/workflow/generate-registry.{ps1,py}`: gera tabela de skills.md + `rules/rules-index.md`; drift-check no validate-framework.

### Fase 4 — context-manifest
`scripts/{powershell,python}/workflow/context-manifest.{ps1,py}`: `--phase --lane --demand-type --agent [--sub-activity]` → lista mínima ordenada de arquivos. Degrada para as tabelas de `rules/README.md` (D3). Wire-in de 1 linha em `core/boot.md` e `rules/README.md`. Fixture de teste no validate-framework.

### Fase 5 — Shims de template (DH-6 aprovada)
`hosts/_template/shim.md` + deltas por host; `generate-host-shims.{ps1,py}`; shims continuam commitados; drift-check. Aplicar cortes das Fases 1–2 no template (~2 KB → ~1,4 KB).

### Fase 6 — Cache + medição
Parágrafo advisory em `core/boot.md` + notas em `hosts/README.md` (kernel estável primeiro, state volátil por último). Baseline antes/depois em `metrics/`.

### Relatório
`docs/plan/architecture-review-context-2026-07.md` (pt-BR): resumo executivo, diagnóstico (números acima), comparação de estratégias, rejeitadas (RAG obrigatório, grafo, sumarização LLM, mega-prompt, orquestração adaptativa — e porquês), riscos/trade-offs, arquitetura recomendada, fluxo em níveis 0–7, roadmap, quick wins, recomendação final. Indexar em `docs/README.md`; registrar DHs no `implementation-plan-2.0.0.md`.

### Verificação (após cada fase)
- `validate-framework` 0 erros nos 2 runtimes; `validate-demand --strict` 0/0 no exemplo de regressão `006-simulado-adocao-v2`. Os exemplos históricos com falha strict seguem como pendência pré-existente registrada acima.
- Fase 4: fixtures do context-manifest (Standard×product×Design, FAST×operational×Execution, SAFE×engineering×Inception) nos 2 runtimes.
- Fase 2/5: smoke test de boot num repo de exemplo.
- Alvo final: cadeia de boot ≤ ~3,5k tk; baseline registrado em `metrics/`.

### Diagnóstico-resumo (por que cada fase existe)
- Sessão carrega ~8,2k tk fixos; `welcome.md` (1.950 tk) é ~60% arte ASCII; `risk-mode.md` (1.318 tk) só é usado 1× por demanda; `model-policy.md` (740 tk) só na troca de modelo.
- Lei suprema repetida em 14 arquivos; gatilhos de escalação em 2; layout de artefatos em 2; terminologia em 2; shims 90% idênticos ×4; gates de catálogo em 2; metadado de skill 3×.
- `rules/` (98 KB) e `knowledge/` sem a camada de metadados que `skills/` já tem; `rules/README.md` ambíguo sobre o que é "always in force"; JIT é 100% advisory.
- O que NÃO mudar: cascata JIT, state de ~1,3 KB, artefatos de 0,4–2 KB, distribuição por stub, quarentena do plano conceitual, contratos por papel.
