# Metrics definition (D10/D43/D45)

What Alfred measures about its own operation (Alfred measuring Alfred). Captured **continuously** (D45) into `audit`/`metrics`, not only at close.

## Per demand (-> agent/phase)
- **Models used:** model id per agent/phase (host, D14) · interactions.
- **Cost (D10):** tokens in/out · estimated $ · cost per model/phase/agent/mode.
- **Efficiency:** lead time · rework (cycles to accept) · first-time acceptance · mode reclassifications · % waiting on human.
- **Quality:** post-release defects · % of AI output kept per agent.

## Aggregation (rollup)
demand → iniciativa → sigla → org (`metrics-rollup.md` at sigla level).

## Agnostic (D3)
Data is markdown; automatic capture (tokens/$/model) is optional via host/connector; without it, essentials are manual/approx. Dashboards = future; data captured now.
