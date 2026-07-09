# Generated Metrics Insights

Derived from `examples/generated/metrics-rollup.md`.

## Insight 1 - Observability Coverage
- observation: maintained demand events now cover the strict 2.0.0 regression and the onboarding fixture.
- evidence: rollup has 8 events, 2 demands, and all maintained demand events are Standard.
- likely cause: stale historical lane snapshots were removed; lane-specific rendering now lives in `examples/toolbar-states/`.
- proposed adjustment: add future FAST/SAFE demand coverage only as strict fixtures, not partial snapshots.
- expected effect: examples remain smaller and every maintained demand can be validated intentionally.
- human decision: pending.

## Insight 2 - Cost And Token Gap
- observation: cost and token metrics exist in the schema but are not populated in current examples.
- evidence: rollup reports `tokens input: 0`, `tokens output: 0`, `cost usd: 0`.
- likely cause: Alfred does not yet have a host adapter that can read model usage.
- proposed adjustment: keep D10/D43 open until a host-specific usage source is available.
- expected effect: avoids false precision while keeping the schema ready for automation.
- human decision: pending.

## Insight 3 - Model Attribution Gap
- observation: most maintained events now identify the model used.
- evidence: rollup reports `events without model: 1`.
- likely cause: the 2.0.0 regression fixture records model attribution; the onboarding fixture remains minimal.
- proposed adjustment: future sample and real events should include `model` whenever the host exposes it.
- expected effect: investigation can correlate output quality and cost with Alfred version/model.
- human decision: pending.

## Insight 4 - Lane Coverage Gap
- observation: maintained end-to-end demand examples currently cover Standard only.
- evidence: FAST, SAFE, and Execution-first are covered by toolbar fixtures and Risk Mode helper probes, not strict demands.
- likely cause: partial historical snapshots were removed instead of being treated as closure evidence.
- proposed adjustment: when a FAST/SAFE/Execution-first scenario is needed, add a complete strict fixture with HUB+App artifacts.
- expected effect: lane evidence stays trustworthy without reintroducing partial demand snapshots.
- human decision: pending.
