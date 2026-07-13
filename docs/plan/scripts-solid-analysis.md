# Analise SOLID dos scripts Python

> Estado levantado em 2026-07-12. Baseline executado: `python scripts/validators/validate-framework.py` retornou sucesso. Nao existe ainda diretorio `tests/`; as regressoes atuais estao concentradas em validators e fixtures em `examples/`.

## Escopo e mapa atual

Os scripts Python sao automacoes opcionais. O framework continua operavel por Markdown/JSONL quando eles nao rodam.

| Arquivo | Responsabilidade atual | Chamadores principais | Classificacao |
|---|---|---|---|
| `scripts/_common.py` | leitura texto, campos Markdown, phase helpers, state parser, JSONL, scan de observability logs | quase todos os entrypoints via `sys.path.insert` | SHIM DE COMPATIBILIDADE |
| `scripts/adapters/mcp-email-server.py` | servidor MCP stdio e CLI para notification/email, config, allowlist, audit, outbox, SMTP, telemetry | MCP hosts, CLI, installers, `validate-email-adapter`, `validate-tool-discovery-policy` | DIVIDIR |
| `scripts/workflow/alfred-boot.py` | detectar repo, listar demandas, priorizar retomada, renderizar preview | manual, host boot, `validate-framework` | REVISAR |
| `scripts/workflow/render-toolbar.py` | parse state, register active demand, reconciliar uso/custo, render rich/text/web | manual, boot, host shims, docs, hook setup via active demand | DIVIDIR |
| `scripts/workflow/context-manifest.py` | selecionar arquivos JIT por fase/lane/tipo/agente | manual, fixture validator | REVISAR |
| `scripts/workflow/generate-registry.py` | gerar registries de rules/skills | manual, `validate-framework --check` | REVISAR |
| `scripts/workflow/generate-host-shims.py` | gerar shims de host a partir de template | manual, `validate-framework --check` | OK |
| `scripts/workflow/sync-host-shims.py` | copiar shims para homes nativos e instalar hook Claude | manual, install docs, `validate-framework` dry-run | REVISAR |
| `scripts/workflow/classify-risk.py` | calcular proposta de lane por checklist | manual/documentado | REVISAR |
| `scripts/workflow/confidence-score.py` | score heuristico pre-Execution | manual/documentado | REVISAR |
| `scripts/workflow/spec-vs-impl.py` | comparar criterios com evidencias por heuristica textual | manual/documentado | REVISAR |
| `scripts/metrics/attribute-usage-transcript.py` | transcript Claude -> eventos request/interaction, dedup, anchors, rate card, cursor | manual, `claude-code-usage-hook`, validators | DIVIDIR |
| `scripts/metrics/claude-code-usage-hook.py` | Stop hook non-blocking, raw log, policy snapshot, subprocess para attribution | Claude Code hook, `sync-host-shims`, validators | DIVIDIR |
| `scripts/metrics/import-ccusage.py` | ccusage subprocess/file -> state update e snapshot | manual/host resume, `validate-framework` fixture | DIVIDIR |
| `scripts/metrics/apply-usage-rate-card.py` | uso exato + rate card -> eventos de custo | manual, `validate-framework`, observability validator | DIVIDIR |
| `scripts/metrics/collect-observability.py` | coletar JSONL locais em batch | manual, telemetry fallback docs | REVISAR |
| `scripts/metrics/generate-metrics-rollup.py` | ler logs e renderizar rollup Markdown | manual, fixtures/validators | DIVIDIR |
| `scripts/metrics/generate-metrics-insights.py` | gerar propostas de insights | manual, observability validator | REVISAR |
| `scripts/metrics/normalize-usage-cost.py` | export generico -> eventos canonicos legacy | manual/documentado | REVISAR |
| `scripts/metrics/observability.py` | shim de compatibilidade para helpers movidos a `shared` | entrypoints metricos legados | SHIM DE COMPATIBILIDADE |
| `scripts/validators/validate-framework.py` | gate unico, lista obrigatoria, politicas literais, subprocess de validators e fixtures | humano/CI/local gate | DIVIDIR |
| `scripts/validators/validate-demand.py` | validacao de demanda HUB/App, JSONL, SDD, staleness | manual, `validate-framework` | DIVIDIR |
| `scripts/validators/validate-scripts-architecture.py` | guardrails de arquitetura scripts/shared/observability | `validate-framework` | REVISAR |
| `scripts/validators/validate-observability-intelligence.py` | fixtures integradas de transcript, hook, rate card, rollup, insights | `validate-framework` | DIVIDIR |
| demais `scripts/validators/validate-*.py` | checks documentais, fixtures e contratos especificos | manual, `validate-framework` | REVISAR |

Modulos `scripts/shared/observability/` ja formam um primeiro subdominio:

| Grupo | Responsabilidade | Problemas principais |
|---|---|---|
| `domain/models.py`, `domain/enums.py` | modelos de uso, custo, eventos, capabilities | `AdapterCapabilities` nao expressa gaps/status experimental |
| `domain/services/*` | calculo puro de uso, custo, forecast, rate card, redacao, legacy usage, artifact classifier | `legacy_usage.py` mantem dicionarios legados no dominio |
| `application/ports/*` | repositorios, clock, runner, adapters | `repositories.py` importa `Path`; `AdapterRegistry` e amplo demais |
| `application/use_cases/reconcile_usage_summary.py` | summary de uso/custo para toolbar/relatorios | boa separacao, mas depende de eventos legados normalizados |
| `infrastructure/repositories/*` | JSONL e summary JSON | leitura integral de logs; sem interface incremental |
| `infrastructure/adapters/claude/*` | transcript/cursor/raw hook Claude | real, mas cursor em infra host-especifica e reutilizado por CLI |
| `infrastructure/adapters/ccusage/session.py` | selecao de sessao e evento canonico session-scoped | real, mas registry tipa como `ObservabilityAdapter` quando nao implementa esse contrato |
| `infrastructure/adapters/codex/*`, `devin/*` | wrappers de `GenericJsonlAdapter` | stubs registrados como se fossem completos |
| `presentation/toolbar_presenter.py` | view model de uso/custo para toolbar | ainda fica dentro de observability embora toolbar tenha dominio proprio |

## Categorias de execucao

- Manuais/documentados: `alfred-boot`, `render-toolbar`, `classify-risk`, `confidence-score`, `spec-vs-impl`, `context-manifest`, `collect-observability`, `generate-metrics-rollup`, `generate-metrics-insights`, `normalize-usage-cost`, `import-ccusage`, `attribute-usage-transcript`, `apply-usage-rate-card`, validators, `mcp-email-server` CLI.
- Boot/resume Alfred: `alfred-boot`; host shims orientam `import-ccusage` e `render-toolbar -RegisterActive`.
- Hooks: `claude-code-usage-hook.py`, instalado por `sync-host-shims.py -InstallHooks`; ele chama `attribute-usage-transcript.py` via subprocess.
- MCP: `mcp-email-server.py`.
- Usados por validators: quase todos os validators; `validate-framework.py` chama subprocess para validators, registry/shim generators, toolbar, ccusage import, rate-card, boot e demand validation.
- Chamadas via subprocess: `validate-framework.py`, `validate-demand.py`, `validate-email-adapter.py`, `validate-observability-intelligence.py`, `validate-reverse-eng-staleness.py`, `claude-code-usage-hook.py`, `import-ccusage.py`, `shared/observability/infrastructure/subprocess_runner.py`.
- Imports dinamicos por path: `alfred-boot.py` -> `render-toolbar.py`; `validate-toolbar-fixtures.py` -> `render-toolbar.py`; `validate-context-manifest-fixtures.py` -> `context-manifest.py`; `validate-demand.py` -> `validate-sdd-gate.py`; `validate-tool-discovery-policy.py` -> `mcp-email-server.py`.

## Grafo de dependencias

Resumo real:

```text
workflow entrypoints
  -> _common
  -> shared.observability (render-toolbar)
  -> dynamic import workflow/render-toolbar (alfred-boot)

metrics entrypoints
  -> _common
  -> metrics.observability shim
  -> shared.observability domain/infrastructure
  -> subprocess/git/ccusage/attribute command at edges

validators entrypoints
  -> _common
  -> workflow modules by importlib
  -> adapters/mcp-email-server by importlib/subprocess
  -> metrics/workflow/validators by subprocess

adapters entrypoints
  -> stdlib only today
  -> duplicated markdown/jsonl helpers instead of shared/common

shared.observability
  domain -> pure stdlib plus legacy dict readers
  application -> domain + ports
  infrastructure -> domain/application + filesystem/json/subprocess/host adapters
  presentation -> domain/application summaries
```

Achados:

- Dependencia invertida correta em boa parte de observability: dominio nao importa infra. O validator atual ja trava isso.
- Dependencia invertida incompleta em adapters: `AdapterRegistry` espera `ObservabilityAdapter`, mas registra `ClaudeTranscriptAdapter` e `CcusageSessionAdapter`, que implementam contratos segregados (`read_transcript`, `read_session_usage`) e nao `read_usage`.
- Imports circulares nao apareceram no escopo analisado.
- `shared` nao importa entrypoints, mas entrypoints importam `metrics.observability`, que e um shim de compatibilidade.
- `sys.path.insert` e usado como mecanismo padrao por entrypoints; isso e aceitavel como compatibilidade, mas deve migrar para composition/CLI modules sob `shared`.
- `importlib` e usado para importar scripts por filename em validadores/boot. Isso acopla comportamento a layout fisico e impede testes mais simples.
- Subprocess desnecessario: hook -> attribution poderia chamar use case; `validate-demand` -> staleness poderia chamar funcao; parte de `validate-framework` poderia compor validators Python diretamente. Subprocess continua justificavel para validar comportamento real de CLI, MCP e hooks.
- Acoplamento concreto: Claude, Codex, Devin, DEVIN, ccusage aparecem em composition registry, host shims, hook, docs e policy checks. O acoplamento deveria ficar em adapters/composition e documentos host-specific.

## Problemas arquiteturais

1. Entry points grossos:
   - `render-toolbar.py` tem 505 linhas e mistura parsing de state, I/O runtime, summary de observability e renderers.
   - `attribute-usage-transcript.py` tem 474 linhas e ainda monta eventos, deduplica JSONL e agrega interactions.
   - `mcp-email-server.py` tem 488 linhas e mistura protocolo MCP, config, dominio notification, telemetry, filesystem e SMTP.
   - `validate-framework.py` tem 733 linhas e mistura gate, subprocess orchestration, policy checks literais e fixtures.

2. Duplicacoes:
   - JSONL: `_common.iter_jsonl`, `apply-usage-rate-card.iter_jsonl`, validators, rollup, insights, email adapter.
   - State/Markdown fields: `_common.read_state_fields`, `mcp-email-server.state_field`, parsers locais de validators.
   - `now_iso`: varios entrypoints e infra.
   - Rate card wrappers: `attribute-usage-transcript.py` e `apply-usage-rate-card.py`.
   - Normalizacao de phase/lane: `_common.py`, `shared/observability/domain/services/normalizers.py`, regras inline.

3. Regras de negocio na borda:
   - CLI functions levantam `SystemExit` fora de `main` (`load_rate_card`, `make_request_event`, `update_state`, validators).
   - Renderers e use cases ainda retornam listas/dicts soltos em vez de resultados estruturados em pontos criticos.
   - Validadores imprimem direto dentro das funcoes de regra, dificultando testes unitarios.

4. Observability:
   - Custo de sessao e demanda ja sao separados no `CostForecastService`, mas a toolbar ainda vive em `shared/observability/presentation`.
   - `GenericJsonlAdapter` declara todas as capabilities como verdadeiras, embora `read_usage` so aceite `Mapping` e retorne vazio para outros sources.
   - Codex/Devin estao registrados no default registry delegando a `GenericJsonlAdapter`, sem fixture que prove formato real.
   - Valor zero observado esta corretamente diferenciado de missing por `ObservedTotal`.

5. Performance:
   - `attribute-usage-transcript.py` faz multiplas leituras integrais do mesmo output JSONL (`already_attributed_request_ids`, `existing_usage_events`, `load_anchor_events`).
   - `claude-code-usage-hook.py` usa leitura integral para `event_exists` a cada snapshot.
   - `render-toolbar.py` reler state e reconciliar observability log em cada render; aceitavel para logs pequenos, mas precisa repositorio incremental quando logs crescerem.
   - `validate-framework.py` executa varios subprocessos que importam novamente o projeto e repetem scans.
   - Scans recursivos (`rglob`) aparecem em boot, links, observability collection, email telemetry e framework validation.

## Classificacao por prioridade

| Prioridade | Arquivos | Problema | Principio afetado | Compatibilidade |
|---|---|---|---|---|
| P0 | `adapter_bootstrap.py`, `application/ports/adapters.py`, stubs Codex/Devin | registry registra adapters que nao respeitam o contrato ou capabilities reais | LSP, ISP | manter imports; tirar stubs do registry padrao ou marcar experimental |
| P0 | `claude-code-usage-hook.py` | hook non-blocking com subprocess e varias responsabilidades | SRP, DIP | manter arquivo e exit 0; mover para `shared/observability/.../use_cases` |
| P0 | `attribute-usage-transcript.py` | event assembly/dedup/cursor no CLI | SRP, DIP | wrapper fino preservando flags e JSONL |
| P1 | `render-toolbar.py`, `toolbar_presenter.py` | toolbar acoplada a observability e I/O | SRP, DIP | preservar fixtures byte a byte |
| P1 | `_common.py` | common generico raiz, usado por entrypoints | SRP | virar shim sobre `shared/common/*` |
| P1 | `validate-framework.py`, `validate-demand.py` | validators imprimem e chamam subprocess sem reports estruturados | SRP, DIP | manter CLI e exit codes; introduzir `ValidationReport` |
| P1 | `mcp-email-server.py` | MCP + dominio notification + SMTP + telemetry no mesmo arquivo | SRP, ISP | manter path MCP/CLI; mover implementacao a `shared/notification` ou `shared/connectors/email` |
| P2 | `generate-metrics-rollup.py`, `generate-metrics-insights.py`, `normalize-usage-cost.py` | log parsing/calculo/render no CLI | SRP | manter saidas atuais |
| P2 | `alfred-boot.py` | dynamic import por filename e apresentacao misturada com descoberta | DIP | importar renderer via modulo compartilhado |
| P2 | validators documentais pequenos | prints/SystemExit dentro de checks | SRP | migrar sob demanda para reports |

## Arquitetura-alvo incremental

Estrutura recomendada:

```text
scripts/
  workflow/      # wrappers CLI publicos
  validators/    # wrappers CLI publicos
  metrics/       # wrappers CLI publicos
  adapters/      # wrappers MCP/CLI publicos
  shared/
    common/      # markdown_fields, state_parser, jsonl, text_files, lifecycle, clock
    validation/  # models, report, runner, check composition
    observability/
      domain/
      application/
      infrastructure/
      composition/
    toolbar/     # state view model, renderers, active-demand runtime registration
    runtime/     # env, git, process runner, active demand
    notification/ # quando mcp-email-server for tocado
```

Regras:

- Entry points so fazem parse de argumentos, composition, chamada de caso de uso, renderizacao e exit code.
- `_common.py` e `metrics/observability.py` permanecem como shims ate zerar imports antigos.
- `AdapterRegistry` deve registrar contratos coerentes por source kind, ou retornar adapters experimentais com gaps explicitos.
- Toolbar consome `UsageSummary`, mas observability nao conhece sigla, lane visual, fase, checkpoint ou renderer.
- Validadores retornam `ValidationReport`; so CLI imprime.

## Riscos e itens preservados

Preservar obrigatoriamente:

- Paths publicos: `scripts/workflow/render-toolbar.py`, `scripts/workflow/alfred-boot.py`, `scripts/validators/validate-framework.py`, `scripts/metrics/import-ccusage.py`, `scripts/metrics/attribute-usage-transcript.py`, `scripts/metrics/claude-code-usage-hook.py`, `scripts/adapters/mcp-email-server.py`.
- Flags atuais, inclusive aliases PowerShell-style (`-StatePath`, `-InputPath`, etc.).
- Exit codes e comportamento non-blocking do hook Claude.
- Formato JSONL, fixtures de toolbar, generated registries/shims, manual fallback Markdown.
- Sem custo silencioso: session cost nao entra em demand forecast.

Nao alterar agora:

- Sem suporte real Codex/Devin sem fonte/fixture aprovada.
- Sem DI container ou plugin framework complexo.
- Sem tornar Python obrigatorio para usar Alfred.
- Sem remover shims antes de migrar consumidores.
