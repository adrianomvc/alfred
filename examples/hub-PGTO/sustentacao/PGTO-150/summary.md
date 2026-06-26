# Summary — PGTO-150 (fechamento, D11)
- Incidente: split duplicava lançamento (idempotência ausente no publish).
- Resolução: hotfix de idempotência + reprocesso de conciliação.
- Causa raiz: regressão introduzida em PGTO-142 (publish sem chave idempotente).
- Ação preventiva (débito -> nova demanda): teste de contrato de idempotência no pipeline.
- Lição: incluir idempotência no DoD de eventos.
