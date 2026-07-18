---
id: devin-usage-quota
type: gotcha
title: Devin /usage shows cycle quota not per-session cost
trigger: cost, ACU, usage, budget
source-demand: 002-custo
date: 2026-07-18
scope: sigla
---

## What
`/usage` reports cumulative cycle ACU; session/demand cost is a delta.

## Source (the truth)
`connectors/usage-cost.md`
