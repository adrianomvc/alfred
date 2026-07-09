---
name: agent-metrics
description: Agent - Metrics
load: agent
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: metrics
---

# Agent - Metrics

## Contract
- **Owns:** Operation metrics, summary, and closeout.
- **Trigger:** merge/release, checkpoint notification, escalation, periodic rollup.
- **Reads:** `05-operation/011-observability-log.jsonl`, app-local `05-operation/008-observability-log.jsonl`, `audit`, PR/release, state, model/cost data, connectors, baselines.
- **Writes:** `metrics`, `summary`, `index`, close event in `audit`.

## Does
- Capture elapsed time, phase time, interactions, model used, tokens/cost when available, review cycles, defects, and acceptance result.
- Prefer `05-operation/011-observability-log.jsonl` as the event source for metrics; use `audit` only as fallback.
- In App-only mode, compute local repo metrics from `05-operation/008-observability-log.jsonl` and mark HUB rollup as pending sync.
- Check baselines and produce insights for humans to ratify.
- Refresh summaries so future sessions can resume with JIT context.
- Trigger configured notifications or manual reminders.

## Does not
- Decide release, change model policy automatically, or send outside configured notification rules.

## Handoff
Close the demand or open follow-up demands for debt, incident prevention, or policy adjustment.
