# 012-execution-plan - 005-parallel-units

## Contexto
- demand id: `005-parallel-units`
- initiative id: `iniciativa-001-piloto`
- lane: Standard
- phase: Execution
- branch: `alfred/005-parallel-units`
- framework version: 0.1.0-dev

## Plano
| Unit | Repo | Escopo | Write scope | Dependencias | Validacao | Status |
|---|---|---|---|---|---|---|
| unit-001 | `sq9-app-a` | contrato A | app A only | nenhuma | lint textual | completed |
| unit-002 | `sq9-app-b` | contrato B | app B only | nenhuma | lint textual | completed |
| unit-003 | HUB | consolidacao | HUB state/evidence | unit-001, unit-002 | evidencia completa | pending |

## Sequencia
1. Executar unit-001 e unit-002 em paralelo.
2. Registrar eventos locais por repo.
3. Serializar unit-003 no HUB.
4. Atualizar `001-state.md`.
5. Gerar evidencia de validacao.

## Paralelismo
- unidades paralelizaveis: `unit-001`, `unit-002`
- restricoes: nao tocar `001-state.md` em paralelo
- merge serializado no `001-state.md`: `unit-003`

## Branch / Commit
- branch esperada: `alfred/005-parallel-units`
- politica: commit pequeno ao fim de cada unit
- PR alvo: `develop`
- merge: somente humano

## Gatilhos de escalonamento
- conflito de write scope
- falha repetida na mesma unit
- inclusao de novo repo fora do plano

## Evidencias esperadas
- logs locais das units
- validacao textual por unit
- consolidacao no HUB

