# Investigação de incidente — PGTO-150 @ pgto-api (D34)
- Incidente: INC-9921 · descrição: split gerando lançamento em duplicidade na conciliação.
- Fonte (observability/connector): CloudWatch (logs do pgto-api) — via connector observability.
- Erro/stack encontrado: retry sem idempotência no publish do evento de split.
- Repos/arquivos mapeados: pgto-api src/payments/split/SplitEventPublisher.
- Causa provável: chave de idempotência ausente no publish (regressão do PGTO-142).
- Ação de estabilização proposta: hotfix idempotência + reprocesso de conciliação.
