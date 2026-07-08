---
name: sub-activity-contract-testing
description: Validate sub-activity — Contract Testing
load: sub-activity
triggers:
  phase: validation
  lane: all
  demand-type: all
  agent: all
---

# Validate sub-activity — Contract Testing

> Trigger: an **external or internal API contract** is produced or consumed by the
> change. Optional, inside Validate.

## Purpose
Prove provider and consumer stay compatible — that the interface honors its
agreed shape and semantics, so neither side breaks silently.

## Inputs
The API/interface definition, `application-design` (interfaces), consumer
expectations, integration points from `tech-inception`.

## Steps
1. Capture the **contract**: request/response shape, status/error semantics,
   versioning expectations.
2. Test the **provider** against the contract (it produces what is promised).
3. Test the **consumer** against the contract (it tolerates the promised shape).
4. Check **backward compatibility** for existing consumers when changing a shape.
5. Record breaking changes; route any to `decisions` and possibly a stronger lane.

## Output
Contract test results, compatibility verdict, and any breaking-change decisions
in the validation evidence.

## Depth by mode
FAST = rarely applies · Standard = provider-side contract check · SAFE = +
consumer-side and explicit backward-compatibility evidence.
