# Tracker Simulator Fixture — canned demand

Deterministic record returned by `tracker-sim` `get_demand(id)`. It mimics what a
real tracker would return, so a sandbox demand can start from a realistic input
without a live fetch. Values are illustrative.

## Demand
- id: `SIM-001`
- title: Reconciliar split de pagamento no fechamento diário
- stream: Operacional
- type: bug
- reporter: on-call (simulado)
- created: 2026-06-29
- priority: alta
- summary: lançamentos de split divergem do extrato no D+1 para um subconjunto de contas.

## Acceptance hints (as a real tracker would carry)
- divergência some após o reprocessamento;
- nenhuma conta fora do subconjunto afetada;
- evidência anexada no fechamento.

## Notes
- This is simulated data. A real run must use a concrete tracker adapter.
