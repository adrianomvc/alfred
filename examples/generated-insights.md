# Generated Metrics Insights

Derived from `examples/generated-metrics-rollup.md`.

## Insight 1 - Observability Coverage
- observation: example events cover six demands across FAST, Standard, SAFE, and Execution-first flows.
- evidence: rollup has 16 events, 6 demands, 3 FAST events, 6 Standard events, and 7 SAFE events.
- likely cause: examples now exercise lane differences and phase-folder lifecycle consistently.
- proposed adjustment: keep new examples tied to observability JSONL instead of static-only Markdown.
- expected effect: future framework changes can be checked against realistic telemetry shape.
- human decision: pending.

## Insight 2 - Cost And Token Gap
- observation: cost and token metrics exist in the schema but are not populated in current examples.
- evidence: rollup reports `tokens input: 0`, `tokens output: 0`, `cost usd: 0`.
- likely cause: Alfred does not yet have a host adapter that can read model usage.
- proposed adjustment: keep D10/D43 open until a host-specific usage source is available.
- expected effect: avoids false precision while keeping the schema ready for automation.
- human decision: pending.

## Insight 3 - Model Attribution Gap
- observation: most events do not identify the model used.
- evidence: rollup reports `events without model: 14`.
- likely cause: examples were written before model attribution became mandatory operational context.
- proposed adjustment: future sample and real events should include `model` whenever the host exposes it.
- expected effect: investigation can correlate output quality and cost with Alfred version/model.
- human decision: pending.

## Insight 4 - Parallel Unit Validation
- observation: the parallel-units example stops at Design.
- evidence: demand `005-parallel-units` has last phase `design` and status `completed`.
- likely cause: the example currently demonstrates decomposition but not full unit validation.
- proposed adjustment: add a follow-up example that completes Execution and Validate for multiple units.
- expected effect: stronger evidence for D13/D24 parallel execution behavior.
- human decision: pending.
