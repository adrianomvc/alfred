# 006-decisions - 005-parallel-units

| Data | Decisao | Responsavel | Motivo | Impacto |
|---|---|---|---|---|
| 2026-06-27 | Usar units dentro da mesma demanda | Alfred | Escopo e aceite sao unicos | Evita multiplicar demandas |
| 2026-06-27 | Permitir paralelismo entre unit-001 e unit-002 | Alfred | Write scopes independentes | Execucao pode ser concorrente |
| 2026-06-27 | Serializar consolidacao no HUB | Alfred | `001-state.md` e fonte unica | Evita conflito de merge de estado |

