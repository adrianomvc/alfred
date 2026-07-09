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
2. Aggregate: **elapsed time, time per phase, interactions, retries, defects,
   blockers**, and the acceptance result.
3. Add **model/tokens/cost** when a host usage source provided them; otherwise
   mark as not collected (do not invent).
4. In **App-only** mode, gather local metrics and leave HUB rollup changes for
   `hub-sync`.
5. Write the aggregated metrics into `metrics` for the summary.

## Output
A metrics record (time, interactions, defects, blockers, optional cost) tied to
the demand, ready for `baseline-drift-check` and `closure-summary`.

## Depth by mode
FAST = lean metrics (time + result) · Standard = full phase metrics · SAFE = +
cost attribution where available and per-phase breakdown.
