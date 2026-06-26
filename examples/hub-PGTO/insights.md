# Insights — sigla PGTO (D43) [observabilidade do Alfred]
> Gerado pelo Metrics Agent a partir dos eventos contínuos (D45) + rollup. Dado markdown; dashboards = futuro.
> Janela: 3 demandas concluídas (PGTO-142, PGTO-150, PGTO-160).

## Custo
- Total estimado: ~US$ 14,50 · Tokens: ~950k · Interações: 41
- Por demanda: PGTO-142 ~5,20 · PGTO-150 ~1,40 · PGTO-160 ~7,90
- Por modo: SAFE ~9,30 (2 demandas) · Standard ~5,20 (1)
- Por stream: Produto ~5,20 · Operacional ~1,40 · Engineering ~7,90

## Mix de modelos (agregado)
- strong (opus) ~65% · medium (sonnet) ~20% · cheap (haiku) ~15%
- Por fase: Design/Execution -> strong · Inception -> medium · Operation -> cheap

## Eficiência
- Lead time medio: ~1,3 dia (excl. incidente) · MTTR incidente: ~25 min
- Aceite de 1a: 2/3 (PGTO-160 teve 1 ciclo de retrabalho)
- Reclassificacoes de modo: 0
- % aguardando humano: ~15%

## Checagem de baselines (D32) — sinais
- % SAFE = 67% (2/3)  -> ACIMA do baseline ~25% -> revisar criterios? (amostra pequena; observar)
- Aceite de 1a = 67%   -> ABAIXO de ~60%? no limite; observar PGTO-160 (serializacao)
- Custo vs teto: dentro

## Recomendacao (sugestao, humano decide — D7/D46)
- Avaliar usar 'medium' na Execution de demandas Standard (PGTO-142 aceitou de 1a com custo menor seria possivel).
- Amostra pequena: nao mudar model-policy ainda; reavaliar apos ~10 demandas.
