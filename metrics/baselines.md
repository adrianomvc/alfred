# Metrics Baselines

Baselines are conversation triggers, not gates.

## Defaults
- SAFE share above ~25% over a window: review whether fear is replacing risk classification.
- Repeated FAST escalations: check whether the checklist is under-scoring risk.
- Repeated validation failure: tighten Design DoD or test plan.
- High cost without quality gain: review model policy.
- Long blocked time: inspect HITL and dependency handoffs.

## Evidence
Every baseline alert links to the metrics rows and the affected demands.

## Context optimization baseline (2026-07)
These numbers are planning baselines for framework context overhead, not exact
host tokenizer output. Use them to compare architecture changes; when a host
exports exact token usage, record that as demand metrics instead.

| Load | Before | After target | Evidence |
|---|---:|---:|---|
| Session start | ~8,230 tk | ~3,300 tk (-60%) | `docs/plan/context-optimization-progress.md` |
| Additional per demand | ~2,630 tk | ~2,100 tk | `risk-mode.md` deferred to Inception; `model-policy.md` deferred to model selection |
| 5-session demand framework overhead | ~43,800 tk | ~20,500 tk (-53%) | JIT registries/manifests + generated host shims |

Tracking rule: new framework context work must update this section or explain
why the baseline is unchanged. Keep stable kernel context first and volatile
state/artifacts last so hosts with caching can reuse the largest stable prefix.
