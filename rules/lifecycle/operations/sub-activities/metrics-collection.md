---
name: sub-activity-metrics-collection
description: Operation sub-activity — Metrics Collection
load: sub-activity
triggers:
  phase: operations
  lane: all
  demand-type: all
  agent: all
---

# Operation sub-activity — Metrics Collection

> Trigger: **always**. Optional only in depth. Owner: **Metrics** agent.

## Purpose
Collect the demand's actual metrics from the append-only observability log so the
close is evidence-based, not estimated.

## Inputs
`05-operation/011-observability-log.jsonl` (HUB) or `008-observability-log.jsonl`
(App-only), the demand `state`, the metrics agent contract
(`../../../agents/metrics.md`).

If the host supports batch/flex/background execution and the close is not
waiting on this result, load `../../../common/deferred-work-policy.md` and run
the rollup as deferred work.

## Steps
1. Read the **observability JSONL** for this demand (append-only, never edited).
2. Aggregate: **elapsed time, time per phase, requests, interactions, retries,
   defects, blockers, artifacts/rules/skills loaded**, and the acceptance
   result.
3. Add **model/tokens/cost** from separate sources: count tokens only from
   `usage_attributed`, count cost only from `usage_cost_attributed`, and keep
   `null` when a metric was not observed. Include `tokens_cache_creation`,
   `tokens_cache_read`, output, and `cache_reuse_ratio`.
4. Refresh session totals for display separately: run the `usage-cost` import
   (ccusage / Devin Insights) so `001-state.md` and the toolbar are current —
   at each checkpoint, not only at close. Do not append ccusage/session totals
   into interaction JSONL. Use rate-card pricing only after exact request or
   interaction usage exists. Keep `cost_confidence` honest (`rated`/`estimated`
   for table pricing, `exact` only from an approved billing source or the host
   cost command). If no usage source is available, mark as not collected (do not
   invent). See `../../../../connectors/usage-cost.md`.
5. In **App-only** mode, gather local metrics and leave HUB rollup changes for
   `hub-sync`.
6. Write the aggregated metrics into `metrics` for the summary.

## Output
A metrics record (time, interactions, defects, blockers, optional cost) tied to
the demand, ready for `baseline-drift-check` and `closure-summary`.

## Depth by mode
FAST = lean metrics (time + result) · Standard = full phase metrics · SAFE = +
cost attribution where available and per-phase breakdown.
