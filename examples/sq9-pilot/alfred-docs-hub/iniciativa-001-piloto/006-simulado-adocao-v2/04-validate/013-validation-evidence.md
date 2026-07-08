# 013-validation-evidence - 006-simulado-adocao-v2

## Contexto
- demand id: `006-simulado-adocao-v2`
- lane: Standard
- framework version: 2.0.0

## Criterios de aceite
| Criterio | Verificacao | Resultado |
|---|---|---|
| Novas demandas carimbam 2.0.0 | `001-state.md` desta demanda | passed |
| Registro de skills segue o template 2.0.0 | template `skills.md` de `templates/hub/` | passed |
| Demandas ativas congeladas | nenhuma demanda 0.x alterada | passed |
| Ciclo validado | validate-sdd-gate + validate-demand estrito | passed |
| Index local do app aponta artefatos e state do HUB | `001-index.md` do app | passed |
| Reverse-eng do app registra o commit analisado | `002-reverse-eng.md` do app (commit gravado) | passed |
| JSONL de observabilidade local do app parseia e carimba 2.0.0 | `008-observability-log.jsonl` do app | passed |

## Regressao
- Demandas 001-005 do exemplo permanecem intactas e validas (suite de regressao).

## Aceite
- Aceite humano registrado em `05-operation/007-audit.md` (merge = aceite).
