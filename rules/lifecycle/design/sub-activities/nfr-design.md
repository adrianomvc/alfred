# Design sub-activity — NFR Design

> Trigger: **performance, scale, availability, or security** matters for the demand
> (hot path, sensitive data, SLAs). Optional, inside Design. Depth by mode.

## Purpose
Weave **non-functional requirements** into the design so SAFE demands do not
"forget" them — turning quality attributes into concrete design choices.

## Inputs
`requirements` (NFR signals), Functional Design, risk (`risk.md`), security skill
if active (D12/D36), `knowledge` policies (D42).

## Steps
1. List the relevant **NFRs**: performance/latency, scalability, availability,
   security/privacy, cost (FinOps).
2. For each, pick a **design pattern or component** that addresses it (e.g.,
   idempotency, retry/backoff, partitioning, caching, least-privilege) — by role, not vendor.
3. Define **measurable targets** and how they will be validated (ties to Validate
   test strategy; performance needs a before/after baseline).
4. Raise the lane / add `decisions` when an NFR forces a stronger mode (override).
5. Mark unknown targets as `a confirmar` — never invent numbers.

## Output
NFR design choices + measurable targets in the `spec`; validation hooks for the
test strategy; any mode override recorded.

## Depth by mode
FAST = usually skipped · Standard = key NFRs + targets ·
SAFE = full NFR analysis with patterns, targets, and validation evidence.
