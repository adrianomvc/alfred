# 003-spec - 006-simulado-adocao-v2 (sq9-app)

## Demand link
`examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/006-simulado-adocao-v2/001-state.md`

## Technical solution
Criar o espelho documental da adocao 2.0.0 no lado do app: index local, reverse-eng
carimbado por commit, audit/metrics locais e evento JSONL proprio. Nenhum codigo alterado.

## Out of scope
- Qualquer mudanca de codigo, pipeline ou infraestrutura do app.
- Migracao de demandas 0.x existentes.

## Files/components affected
- `.alfred-docs-app/iniciativa-001-piloto/006-simulado-adocao-v2/` (novos artefatos apenas)

## Dependencies
- unit-001 do HUB concluida (artefatos HUB carimbados 2.0.0).

## Impacts
- usuarios: nenhum; sistemas: nenhum; dados: nenhum (documental).

## Acceptance criteria
- index local aponta todos os artefatos e o state do HUB;
- reverse-eng registra o commit analisado;
- JSONL local parseia e carimba 2.0.0.

## Test plan
- `validate-demand --app-demand-path ... --strict` sem erros/avisos.
