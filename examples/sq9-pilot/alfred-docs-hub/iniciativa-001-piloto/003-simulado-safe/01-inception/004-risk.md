# Risk - 003-simulado-safe

## Classificacao
- score de risco: 8/10
- score de complexidade: 6/10
- modo proposto: SAFE
- modo confirmado: SAFE

## Overrides
- Governanca critica de artefatos e retomada: minimo SAFE.

## Racional
O erro na convencao de rastreio afeta todas as demandas futuras da sigla. A mudanca e documental, mas o impacto operacional sobre retomada, auditoria e correlacao HUB/App justifica SAFE.

## Elevacao por app
- `sq9-app`: SAFE por depender da correlacao `examples/sq9-pilot/.alfred-docs-app/iniciativa-001-piloto/003-simulado-safe/` com o HUB.

