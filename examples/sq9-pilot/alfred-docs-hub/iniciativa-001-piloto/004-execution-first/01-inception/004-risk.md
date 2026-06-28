# Risk - 004-execution-first

## Classificacao
- score de risco: 8/10
- score de complexidade: 5/10
- modo proposto: SAFE
- modo confirmado: SAFE
- tempo: Emergency / Execution-first

## Overrides
- Incidente operacional com impacto direto na capacidade de retomada: SAFE.
- Urgencia alta: Execution-first.

## Racional
O incidente simulado afeta rastreabilidade e retomada. A ordem normal das fases e comprimida: estabiliza primeiro, depois completa os artefatos obrigatorios.

## Elevacao por app
- `sq9-app`: SAFE durante o incidente.

