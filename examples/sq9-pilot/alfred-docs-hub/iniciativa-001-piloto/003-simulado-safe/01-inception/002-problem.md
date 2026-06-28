# Problema - 003-simulado-safe

## Contexto
Depois dos simulados Standard e FAST, o Alfred precisa provar o modo SAFE: maior rigor, mais evidencias e checkpoints humanos explicitos.

## Problema
Uma mudanca critica de convencao operacional pode afetar a forma como demandas futuras localizam `state`, `audit`, `metrics` e artefatos tecnicos. Mesmo sendo documental, a consequencia de erro e alta para retomada e rastreabilidade.

## Objetivo
Validar que o Alfred aplica SAFE quando ha risco de governanca: decisions completas, audit completo, criterios de aceite formais, plano de rollback e evidencias.

## Escopo
- Criar demanda `003-simulado-safe` em modo SAFE.
- Registrar risco alto e justificativa.
- Produzir spec tecnica formal.
- Validar retomada, links e evidencias.

## Fora de escopo
- Alterar integracoes reais.
- Enviar notificacao externa.
- Fazer merge em branch protegida.

## Riscos / duvidas
- Risco de over-process se SAFE for usado em demandas simples.
- Risco de drift entre indices e `state` se a demanda SAFE nao registrar evidencias.

