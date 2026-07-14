# Resultado parcial da refatoracao SOLID dos scripts

Data: 2026-07-12.

## Escopo concluido

- Relatorio inicial criado em `docs/plan/scripts-solid-analysis.md`.
- Plano incremental criado em `docs/plan/scripts-solid-refactoring-plan.md`.
- `docs/README.md` atualizado com os novos documentos.
- Wave 1 iniciada e concluida para o ponto critico de contracts:
  - `AdapterRegistry` deixou de prometer sempre `ObservabilityAdapter`; agora resolve `object` e permite marcar registros experimentais.
  - Protocolos de adapter viraram `runtime_checkable`, permitindo validacao de contrato em runtime.
  - Codex/Devin passthrough adapters sairam do default registry.
  - `build_experimental_registry()` mantem acesso aos passthrough adapters como experimentais.
  - `validate-scripts-architecture.py` agora impede stubs Codex/Devin no registry padrao e verifica contratos de transcript/session.
- Wave 2 iniciada e concluida para common:
  - criado `scripts/shared/common/` com `markdown_fields.py`, `state_parser.py`, `jsonl.py`, `text_files.py`, `lifecycle.py`.
  - `scripts/_common.py` foi reduzido a shim de compatibilidade, preservando os nomes antigos.
- Testes iniciais criados em `tests/scripts/`:
  - `unit/test_shared_common.py`
  - `unit/test_apply_usage_rate_card.py`
  - `unit/test_import_ccusage_session.py`
  - `unit/test_process_claude_hook.py`
  - `unit/test_attribute_transcript_usage.py`
  - `unit/test_metrics_jsonl_readers.py`
  - `contract/test_observability_adapter_registry.py`
  - `architecture/test_shared_boundaries.py`
- Wave 4 iniciada para ingestion CLIs:
  - criado `scripts/shared/observability/application/use_cases/apply_usage_rate_card.py`.
  - `scripts/metrics/apply-usage-rate-card.py` agora delega assembly/custo/dedup sem reintroduzir `event_tokens`, `rate_for` ou `make_cost_event`.
  - criado `scripts/shared/observability/application/use_cases/import_ccusage_session.py`.
  - `scripts/metrics/import-ccusage.py` agora delega montagem do snapshot e dos updates de state, mantendo aquisicao via arquivo/subprocess e escrita na borda CLI.
  - criado `scripts/shared/observability/application/use_cases/process_claude_hook.py`.
  - `scripts/metrics/claude-code-usage-hook.py` agora delega a coordenacao raw/alfred para `ProcessClaudeHook`, mantendo env vars, filesystem, subprocess e exit 0 na borda CLI.
  - criado `scripts/shared/observability/application/use_cases/attribute_transcript_usage.py`.
  - `scripts/metrics/attribute-usage-transcript.py` agora delega montagem de `usage_attributed` e `interaction_completed`, mantendo parsing do transcript, cursor, leitura JSONL e append na borda CLI.
  - `validate-scripts-architecture.py` trava esses helpers fora do CLI, incluindo `make_snapshot`, `make_request_event` e `make_interaction_events`.
- Consolidacao pontual de JSONL:
  - `scripts/metrics/apply-usage-rate-card.py`, `scripts/metrics/attribute-usage-transcript.py` e `scripts/metrics/claude-code-usage-hook.py` passaram a usar `shared.common.iter_jsonl` para leitura JSONL.
  - `scripts/metrics/collect-observability.py`, `scripts/metrics/generate-metrics-rollup.py` e `scripts/metrics/generate-metrics-insights.py` tambem passaram a usar `shared.common.iter_jsonl`.
  - O parse de stdin do hook permanece local porque nao e JSONL.
- `docs/scripts-architecture.md` atualizado com `shared/common` e registry experimental.
- Wave 5 iniciada para toolbar:
  - criado `scripts/shared/toolbar/` com `presenter.py` e `__init__.py`.
  - `scripts/workflow/render-toolbar.py` agora importa `ToolbarViewModelBuilder` de `shared.toolbar.presenter`.
  - `scripts/shared/observability/presentation/toolbar_presenter.py` virou shim de compatibilidade.
  - criado `scripts/shared/toolbar/renderers.py` com renderers `text`, `rich` e `web`.
  - `scripts/workflow/render-toolbar.py` agora delega renderizacao visual para `shared.toolbar.renderers`.
  - criado `scripts/shared/toolbar/state.py` com parsing de state, fases, markers e progresso.
  - `scripts/workflow/render-toolbar.py` agora delega parsing da toolbar para `shared.toolbar.state`.
  - criado `scripts/shared/toolbar/runtime.py` com resolucao de framework/app commit e paths auxiliares.
  - `scripts/workflow/render-toolbar.py` agora delega a resolucao de framework/app revision para `shared.toolbar.runtime`.
  - criado `scripts/shared/toolbar/active_demand.py` com registro runtime da demanda ativa.
  - criado `scripts/shared/toolbar/summary.py` com ajustes de campos de custo/uso e composition do `UsageSummary`.
  - criado `scripts/shared/toolbar/service.py` com orquestracao de renderizacao da toolbar.
  - `scripts/workflow/render-toolbar.py` agora funciona como wrapper/entrypoint fino: argparse, registro opcional, chamada do servico e impressao.
  - fixtures da toolbar foram preservadas sem drift.
- Wave 5 / Boot preview:
  - `scripts/workflow/alfred-boot.py` deixou de importar `render-toolbar.py` via `importlib`.
  - criado `render_resume_preview()` em `alfred-boot.py`, delegando diretamente para `shared.toolbar.service.render_toolbar`.
  - `validate-scripts-architecture.py` agora impede regressao desse acoplamento por filename.
- Wave 6 iniciada para validators:
  - criado `scripts/shared/validation/` com `Severity`, `ValidationIssue` e `ValidationReport`.
  - `scripts/validators/validate-model-policy.py` agora possui `validate_model_policy(root) -> ValidationReport`.
  - `scripts/validators/validate-observability-hygiene.py` agora possui `validate_observability_hygiene(root) -> tuple[ValidationReport, int]`.
  - `scripts/validators/validate-toolbar-fixtures.py` agora possui `validate_toolbar_fixtures(root) -> ValidationReport`.
  - `validate-toolbar-fixtures.py` deixou de importar `render-toolbar.py` por filename e passou a usar `shared.toolbar.service.render_toolbar`.
  - criado `scripts/shared/context_manifest.py` com a regra de montagem do context manifest.
  - `scripts/workflow/context-manifest.py` virou CLI fino sobre `shared.context_manifest.build_manifest`.
  - `scripts/validators/validate-context-manifest-fixtures.py` agora possui `validate_context_manifest_fixtures(root) -> ValidationReport`.
  - `validate-context-manifest-fixtures.py` deixou de importar `context-manifest.py` por filename e passou a usar `shared.context_manifest`.
  - criado `scripts/shared/email_tools.py` com o catalogo MCP do adapter de e-mail.
  - `scripts/adapters/mcp-email-server.py` passou a importar `TOOLS` de `shared.email_tools`.
  - `scripts/validators/validate-tool-discovery-policy.py` agora possui `validate_tool_discovery_policy(root) -> ValidationReport`.
  - `validate-tool-discovery-policy.py` deixou de importar `mcp-email-server.py` por filename e passou a usar `shared.email_tools`.
  - criado `scripts/shared/sdd_gate.py` com a regra do SDD gate.
  - `scripts/validators/validate-sdd-gate.py` virou CLI fino sobre `shared.sdd_gate.run`.
  - `scripts/validators/validate-demand.py` deixou de importar `validate-sdd-gate.py` por filename e passou a usar `shared.sdd_gate`.
  - `scripts/validators/validate-demand.py` agora possui `validate_demand(args) -> DemandValidationResult` com `ValidationReport`; o entrypoint ficou responsavel por imprimir e retornar exit code.
  - criado `scripts/shared/validation/reverse_eng_staleness.py` com parsing de commit e avaliacao de staleness.
  - `scripts/validators/validate-reverse-eng-staleness.py` virou CLI fino sobre o modulo compartilhado.
  - `validate-demand.py` deixou de chamar o staleness por subprocess e passou a compor `shared.validation.reverse_eng_staleness` diretamente.
  - O entrypoint de `validate-model-policy.py` ficou responsavel por argparse, renderizacao da saida e exit code.
  - Os entrypoints migrados ficaram responsaveis por argparse, renderizacao da saida e exit code.
  - As saidas de sucesso dos validators migrados foram preservadas.

## Estrutura antes/depois

Antes:

```text
scripts/_common.py
scripts/shared/observability/application/ports/adapters.py
scripts/shared/observability/composition/adapter_bootstrap.py
```

Depois:

```text
scripts/_common.py                         # shim
scripts/shared/common/                     # helpers comuns
scripts/shared/context_manifest.py         # regra de selecao JIT de contexto
scripts/shared/email_tools.py              # catalogo MCP do adapter de e-mail
scripts/shared/sdd_gate.py                 # regra do SDD gate
scripts/shared/toolbar/                    # state, runtime, presenter, renderers e service da toolbar
scripts/shared/validation/                 # modelos estruturados de validacao
scripts/shared/observability/application/ports/adapters.py
scripts/shared/observability/application/use_cases/attribute_transcript_usage.py
scripts/shared/observability/application/use_cases/apply_usage_rate_card.py
scripts/shared/observability/application/use_cases/import_ccusage_session.py
scripts/shared/observability/application/use_cases/process_claude_hook.py
scripts/shared/observability/composition/adapter_bootstrap.py
tests/scripts/{unit,contract,architecture}/
```

## Arquivos movidos ou preservados

Nenhum path publico foi movido. Foram adicionados modulos novos e mantidos os wrappers/shims existentes.

Wrappers e shims preservados:

- `scripts/_common.py`
- `scripts/metrics/observability.py`
- `scripts/shared/observability/presentation/toolbar_presenter.py`
- todos os entrypoints em `scripts/workflow`, `scripts/metrics`, `scripts/validators`, `scripts/adapters`

## Compatibilidade preservada

- Comandos publicos e flags nao mudaram.
- `validate-framework.py` continua gate unico.
- JSONL e fixtures nao foram alterados.
- Hook Claude preserva comportamento non-blocking e continua retornando 0 em todos os caminhos validados.
- MCP email nao foi modificado nesta onda.
- Toolbar fixtures `examples/toolbar-fixtures/*.txt` continuam sem drift.

## Duplicacoes removidas ou preparadas

- Logica comum de `_common.py` saiu do arquivo raiz e passou a ter home em `shared/common`.
- O registry padrao deixou de misturar adapters reais com passthroughs experimentais.
- Assembly e pricing de `apply-usage-rate-card.py` sairam do CLI para um use case compartilhado.
- Assembly de snapshot e updates de state de `import-ccusage.py` saiu do CLI para um use case compartilhado.
- Coordenacao raw/alfred do `claude-code-usage-hook.py` saiu do CLI para um use case compartilhado, com falhas convertidas em mensagens em vez de excecoes.
- Assembly de request/interaction events de `attribute-usage-transcript.py` saiu do CLI para um use case compartilhado, preservando dedup por `requestId` no wrapper e formato JSONL.
- Leitura JSONL duplicada nos seis CLIs metricos migrados foi consolidada em `shared.common.iter_jsonl`.
- Presenter/view model da toolbar saiu de `shared.observability.presentation` para `shared.toolbar`, deixando o modulo antigo como shim.
- Renderers `text`, `rich` e `web` sairam de `render-toolbar.py` para `shared.toolbar.renderers`.
- Parsing de campos, fases e progresso da toolbar saiu de `render-toolbar.py` para `shared.toolbar.state`.
- Resolucao de framework/app commit da toolbar saiu de `render-toolbar.py` para `shared.toolbar.runtime`.
- Registro de demanda ativa saiu de `render-toolbar.py` para `shared.toolbar.active_demand`.
- Ajustes de custo/uso e composition do `UsageSummary` sairam de `render-toolbar.py` para `shared.toolbar.summary`.
- Orquestracao da renderizacao saiu de `render-toolbar.py` para `shared.toolbar.service`.
- Boot deixou de importar `render-toolbar.py` por path e passou a reutilizar o mesmo servico compartilhado.
- Validators migrados para report estruturado: `validate-model-policy.py`, `validate-observability-hygiene.py` e `validate-toolbar-fixtures.py`.
- `context-manifest.py` deixou de carregar regra no entrypoint; a montagem passou para `shared.context_manifest`.
- `validate-context-manifest-fixtures.py` foi migrado para report estruturado e deixou de importar o script por path.
- Catalogo MCP do e-mail saiu do entrypoint `mcp-email-server.py` para `shared.email_tools`.
- `validate-tool-discovery-policy.py` foi migrado para report estruturado e deixou de importar o MCP server por path.
- Regra do SDD gate saiu do entrypoint `validate-sdd-gate.py` para `shared.sdd_gate`.
- `validate-demand.py` deixou de importar `validate-sdd-gate.py` por path.
- Staleness de reverse-eng saiu do entrypoint `validate-reverse-eng-staleness.py` para `shared.validation.reverse_eng_staleness`.
- `validate-demand.py` deixou de executar staleness por subprocess interno.
- `validate-toolbar-fixtures.py` deixou de importar `render-toolbar.py` por path; `validate-framework.py` ainda executa smoke real do comando publico.

Ainda restam duplicacoes conhecidas:

- JSONL em validators, email adapter e alguns repositories de infraestrutura.
- `now_iso` em varios entrypoints.
- assembly de eventos em CLIs metricos.
- parsers Markdown locais no MCP email e em validators.

## Performance

Nao houve otimizacao mensurada nesta entrega. A unica mudanca de performance esperada e neutra: `_common.py` agora reexporta funcoes de modulos menores. Benchmarks ficam para as ondas que reduzirem leituras repetidas de JSONL.

`import-ccusage.py` nao recebeu alegacao de ganho de performance nesta onda: a execucao de `ccusage`, leitura de arquivo e escrita de state continuam iguais. A melhoria foi de separacao arquitetural e testabilidade.

`claude-code-usage-hook.py` tambem nao recebeu alegacao de ganho de performance. A leitura incremental por cursor foi preservada; a mudanca foi mover a orquestracao para um caso de uso testavel sem alterar o numero de leituras ou subprocessos.

`attribute-usage-transcript.py` nao recebeu alegacao de ganho de performance. A leitura do transcript, cursor, dedup do output existente e append continuam iguais; a mudanca foi separar montagem de eventos para teste.

A consolidacao JSONL tambem nao recebeu alegacao de ganho de performance: ela remove duplicacao de parsing, preserva erro em JSONL invalido nos comandos estritos e tolerancia nos logs auxiliares do transcript, mas nao muda o numero de leituras de arquivo.

Baseline executado:

```text
python scripts/validators/validate-framework.py
```

Resultado: sucesso.

## Testes executados

- `python scripts/validators/validate-scripts-architecture.py`: sucesso.
- `python scripts/validators/validate-observability-intelligence.py`: sucesso.
- `python scripts/validators/validate-toolbar-fixtures.py`: sucesso.
- `python scripts/validators/validate-reverse-eng-staleness.py -ReverseEngPath examples/staleness-fixtures/reverse-eng-fresh.md -CurrentCommit aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --strict`: sucesso.
- `python scripts/validators/validate-demand.py -HubDemandPath examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/006-simulado-adocao-v2 -AppDemandPath examples/sq9-pilot/.alfred-docs-app/iniciativa-001-piloto/006-simulado-adocao-v2 -AppCurrentCommit bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb --strict`: sucesso.
- `python -m unittest discover -s tests -p test_*.py`: 66 testes, sucesso.
- `python scripts/validators/validate-framework.py`: sucesso.

`pytest` nao foi adotado nesta entrega porque nao esta instalado no ambiente
atual (`python -m pytest --version` falhou com `No module named pytest`). A
suite inicial usa `unittest` da stdlib para manter dependencias zero. `ruff`,
`mypy` ou `pyright` ficam para Wave 7, apos decisao sobre dependencia local/CI.

## Riscos restantes

- Entry points principais ainda grossos: `mcp-email-server`, `validate-framework` e parte dos validators.
- `apply-usage-rate-card.py` ainda faz I/O JSONL e append no wrapper; a regra de negocio principal saiu.
- `import-ccusage.py` ainda faz subprocess, leitura de input e escrita de state no wrapper por serem responsabilidades de borda; selecao da sessao ainda usa o adapter diretamente no CLI.
- `claude-code-usage-hook.py` ainda resolve ambiente, demanda ativa, paths, policy snapshot e subprocess no wrapper; a orquestracao principal saiu, mas ainda ha responsabilidades de runtime a extrair em ondas posteriores.
- `attribute-usage-transcript.py` ainda faz leitura JSONL de anchors/eventos existentes, cursor e append no wrapper; assembler principal saiu.
- `validate-framework.py` ainda depende de listas manuais e subprocess extensivo.
- A maioria dos validators ainda usa `SystemExit` inline; `validate-model-policy.py`, `validate-observability-hygiene.py`, `validate-toolbar-fixtures.py`, `validate-context-manifest-fixtures.py`, `validate-tool-discovery-policy.py`, `validate-demand.py` e `validate-reverse-eng-staleness.py` iniciaram o padrao `ValidationReport`.
- `render-toolbar.py` ainda preserva um wrapper `render()` por compatibilidade com validators/fixtures que importam o arquivo por path.
- Codex/Devin continuam sem adapters reais; apenas foram retirados do default registry.
- O novo `shared/common` ainda nao foi adotado diretamente pelos entrypoints; `_common.py` preserva compatibilidade ate a migracao gradual.

## Proximos passos

1. Criar harness `tests/scripts/` antes de refatorar CLIs maiores.
2. Migrar leitores JSONL duplicados para `shared/common/jsonl.py`.
3. Migrar leitores JSONL restantes de validators/email adapter para repositories/shared common.
4. Separar runtime/config do `claude-code-usage-hook.py` mantendo exit 0.
5. Migrar o proximo validator pequeno para `ValidationReport` antes de tocar `validate-framework.py`.
