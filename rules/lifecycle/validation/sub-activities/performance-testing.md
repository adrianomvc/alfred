# Validate sub-activity — Performance Testing

> Trigger: an **NFR perf/scale target exists** (from `nfr-design`) or the change
> touches a hot path. Optional, inside Validate.

## Purpose
Prove the change meets its measurable performance/scale targets — with a real
before/after baseline, never a guessed number.

## Inputs
`nfr-design` targets (latency, throughput, resource), a representative dataset/
load, the affected hot path, the prior baseline if one exists.

## Steps
1. Restate the **measurable target** from `nfr-design` (e.g., p95 latency, TPS).
2. Capture a **before baseline** on the unchanged path when feasible.
3. Run the load against the change with a **representative** dataset/profile.
4. Compare **after vs before**; confirm the target is met or record the gap.
5. Never invent numbers — mark missing targets as `a confirmar` and escalate.

## Output
Before/after performance numbers against the target, pass/gap verdict, and
residual risks in the validation evidence.

## Depth by mode
FAST = skipped · Standard = targeted measurement on the hot path · SAFE = full
load profile with before/after baseline and documented method.
