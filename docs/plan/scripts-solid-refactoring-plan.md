# Plano de refatoracao SOLID dos scripts Python

Este plano implementa a analise em `docs/plan/scripts-solid-analysis.md` sem big bang. O baseline inicial esta verde: `python scripts/validators/validate-framework.py`.

## Estrategia

- Refatorar por ondas pequenas, cada uma com wrappers de compatibilidade.
- Primeiro estabilizar contratos e testes; depois mover logica.
- Manter saidas e fixtures. Quando uma saida mudar, registrar decisao e migracao.
- Validar apos cada onda: `python scripts/validators/validate-framework.py`; quando houver testes, tambem `pytest`.

## Wave 0 - Baseline e harness

Arquivos:

- `docs/plan/scripts-solid-analysis.md`
- `docs/plan/scripts-solid-refactoring-plan.md`
- futura estrutura `tests/scripts/{unit,contract,integration,architecture,fixtures}`

Trabalho:

- Registrar baseline atual e lacunas.
- Criar testes de compatibilidade para wrappers publicos mais criticos.
- Capturar fixtures de toolbar, transcript, ccusage, rate card, hook e validators.

Rollback:

- Remover apenas novos testes/docs se bloquearem; nenhum comportamento runtime muda.

Aceite:

- `validate-framework` verde.
- Fixtures atuais identificadas.

## Wave 1 - Contracts de adapters

Arquivos:

- `scripts/shared/observability/application/ports/adapters.py`
- `scripts/shared/observability/composition/adapter_bootstrap.py`
- `scripts/shared/observability/infrastructure/adapters/{generic,codex,devin,claude,ccusage}/`
- `scripts/validators/validate-scripts-architecture.py`

Trabalho:

- Separar registries por contrato ou tornar `AdapterRegistry` generico por capability.
- Nao registrar Codex/Devin stubs como completos no registry padrao.
- Fazer stubs retornarem gaps explicitos ou ficarem em registry experimental.
- Provar contrato com testes/validator.

Rollback:

- Reverter composition/registry mantendo adapters fisicos intocados.

Aceite:

- Nenhum adapter registrado viola o protocolo resolvido.
- `ccusage` segue session-scoped.
- `validate-scripts-architecture` cobre anti-stub.

## Wave 2 - `shared/common`

Arquivos:

- novo `scripts/shared/common/{markdown_fields.py,state_parser.py,jsonl.py,text_files.py,lifecycle.py,clock.py}`
- `scripts/_common.py`
- entrypoints que importam `_common`

Trabalho:

- Mover funcoes puras/compartilhadas.
- `_common.py` vira shim de reexport.
- Consolidar parsing JSONL e state fields.

Rollback:

- `_common.py` continua publicando os mesmos nomes; voltar imports e simples.

Aceite:

- Sem duplicacao critica de JSONL/state nos entrypoints tocados.
- Validadores e toolbar continuam com mesma saida.

## Wave 3 - Observability application

Arquivos:

- `scripts/shared/observability/application/use_cases/`
- `scripts/shared/observability/infrastructure/repositories/`
- `scripts/shared/observability/domain/services/legacy_usage.py`
- `scripts/metrics/generate-metrics-rollup.py`
- `scripts/metrics/generate-metrics-insights.py`

Trabalho:

- Tirar legacy dict parsing do dominio quando houver repositorio/modelo adequado.
- Criar assemblers de eventos tipados para request, interaction, cost e session snapshot.
- Reduzir leituras repetidas de JSONL com repository que retorna visoes em uma passada.

Rollback:

- Manter shims e wrappers; nao mudar JSONL.

Aceite:

- Zero observado continua diferente de missing.
- Session cost nao alimenta forecast de demanda.
- Benchmark simples mostra leituras reduzidas para attribution/hook em fixtures.

## Wave 4 - Ingestion CLIs

Arquivos:

- `scripts/metrics/attribute-usage-transcript.py`
- `scripts/metrics/claude-code-usage-hook.py`
- `scripts/metrics/import-ccusage.py`
- `scripts/metrics/apply-usage-rate-card.py`
- novos use cases em `shared/observability/application/use_cases/`
- infra `runtime` para env/git/processo quando necessario

Trabalho:

- Transformar CLIs em wrappers finos.
- Hook Claude: `stdin -> context -> ProcessClaudeHook -> always exit 0`.
- Attribute transcript: dedup, anchors, interaction aggregation e cursor em use case.
- Import ccusage: separar aquisicao subprocess/file, selecao, snapshot, state update.
- Apply rate card: separar repository, calculator, assembler e renderer CLI.

Rollback:

- Arquivos publicos permanecem; trocar import para implementacao antiga se necessario.

Aceite:

- Mesmas flags e formatos.
- Hook continua non-blocking.
- Fixtures de observability passam.

## Wave 5 - Toolbar

Arquivos:

- novo pacote compartilhado de toolbar
- `scripts/workflow/render-toolbar.py`
- `scripts/shared/observability/presentation/toolbar_presenter.py`
- `scripts/workflow/alfred-boot.py`
- `scripts/validators/validate-toolbar-fixtures.py`

Trabalho:

- Criar `ToolbarViewModel`, `UsageCostViewModel`, `TextToolbarRenderer`, `RichToolbarRenderer`, `SvgToolbarRenderer`.
- Mover active-demand runtime registration para `shared/runtime`.
- Boot deixa de importar `render-toolbar.py` por filename.

Rollback:

- Wrapper publico preserva `render()` e `main()`.

Aceite:

- Fixtures de toolbar byte a byte.
- Observability nao conhece sigla/progresso/lane visual/fase.

## Wave 6 - Validators estruturados

Arquivos:

- novo `scripts/shared/validation/{models.py,reverse_eng_staleness.py}`; `runner.py`/`renderers.py` ficam condicionais a novos usos reais
- `scripts/validators/validate-framework.py`
- `scripts/validators/validate-demand.py`
- `scripts/validators/validate-reverse-eng-staleness.py`
- validators documentais

Trabalho:

- Introduzir `ValidationIssue` e `ValidationReport`.
- Substituir subprocess por chamada Python quando o objetivo for regra, nao CLI behavior.
- Manter subprocess para smoke real de comandos publicos, MCP e hook.
- Remover listas manuais quando metadata/registry puder gerar catalogo.

Rollback:

- CLI imprime os mesmos textos principais e exit codes.

Aceite:

- `validate-framework` continua gate unico.
- Reports testaveis sem capturar stdout.

## Wave 7 - Qualidade, CI e documentacao

Arquivos:

- `pyproject.toml`
- `.github/workflows/ci.yml`
- `tests/scripts/**`
- `docs/scripts-architecture.md`
- `scripts/README.md`

Trabalho:

- Adotar `pytest` e `ruff` se mantiver instalacao simples.
- Type checking incremental (`mypy` ou `pyright`) somente se nao travar contribuicao.
- CI: `python scripts/validators/validate-framework.py`, `pytest`, `ruff check`.
- Atualizar docs para refletir estrutura real.

Rollback:

- Ferramentas novas podem ser removidas sem mexer nos scripts.

Aceite:

- Testes unitarios, contrato, integracao e arquitetura cobrindo fronteiras criticas.
- Sem referencias obsoletas a paths removidos.

## Medicao de performance

Medir antes/depois apenas em pontos com suspeita real:

- `attribute-usage-transcript`: leituras de output JSONL e tempo em fixture crescente.
- `claude-code-usage-hook`: custo de cursor + snapshot idempotente.
- `render-toolbar`: tempo com log pequeno e log sintetico maior.
- `validate-framework`: tempo total e quantidade de subprocessos.

Formato minimo:

```text
command, fixture, before_ms, after_ms, notes
```

Sem cache global oculto. Qualquer cache deve ter chave, escopo e invalidaçao clara.

## Criterios finais

- `validate-framework.py` retorna sucesso.
- Wrappers publicos e aliases de flags preservados.
- Hooks non-blocking.
- MCP e CLI de email preservados.
- JSONL e fixtures compativeis.
- Registry padrao sem stubs completos.
- `shared` sem dependencia de entrypoints.
- `_common.py` reduzido a shim ou removido somente apos migracao total.
- Relatorio final em `docs/plan/scripts-solid-refactoring-result.md`.
