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

### DEVIN CLI token-economy pass (2026-07-16)
This pass corrected host-integration defects and added deterministic, opt-in
savings for the DEVIN CLI (the predominant host). Effect on the fixed baselines:
- **Session start / per-demand fixed cost: unchanged.** The new rules
  (`context-compaction-policy`, MCP JIT, `/btw`) are `load: event`/opt-in and do
  not enter boot; knowledge frontmatter replaced a hand-written registry with a
  generated one of the same size.
- **Per-command and per-log cost: expected to drop, not yet measured on a real
  host.** The RTK `PreToolUse` hook (once installed with an `exec` matcher) and
  the permission allowlist remove per-command approval turns; moving observability
  writes out-of-band (Wave 5) removes model-generated JSONL. These require a real
  DEVIN CLI session to measure (`/context`, `/usage`, `rtk gain`) — that is the
  first real host measurement the 2026-07 roadmap asked for.

A first **budget gate** now guards regressions per scenario:
`metrics/context-budgets.json` + `scripts/validators/validate-context-budget.py`
(run inside `validate-framework`). Estimates are chars/4 (planning proxy, not a
host tokenizer); tighten the caps with real host measurement when available.
Measure ad hoc with `python scripts/metrics/measure-context-budget.py`.

## Pilot baselines
These values are conversation triggers, not gates. They require real samples
before ratification.

```json
[
  {"metric":"cache_reuse_ratio","threshold":0.30,"status":"pilot","minimum_sample_size":5,"approved_by":null},
  {"metric":"tool_failure_rate","threshold":0.10,"status":"planning","minimum_sample_size":5,"approved_by":null},
  {"metric":"repeated_unchanged_artifact_reads","threshold":5,"status":"pilot","minimum_sample_size":5,"approved_by":null},
  {"metric":"events_with_exact_usage","threshold":0.80,"status":"planning","minimum_sample_size":5,"approved_by":null}
]
```
