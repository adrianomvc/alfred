---
name: sub-activity-infrastructure-design
description: Design sub-activity — Infrastructure Design
load: sub-activity
triggers:
  phase: design
  lane: all
  demand-type: all
  agent: all
---

# Design sub-activity — Infrastructure Design

> Trigger: the demand needs **deploy or infrastructure change** (new resource,
> IaC, pipeline, environment). Optional, inside Design. Depth by mode.

## Purpose
Map the **logical components to actual infrastructure choices** for the target
environments — without inventing account/region/resource names (anti-overconfidence).

## Inputs
Functional Design (logical components), NFR Design (if any), tech-inception,
applicable IaC template/skill (D35/D36), `knowledge` infra policies (D42).

## Steps
1. Read the functional/NFR design; list the **logical components needing infrastructure**.
2. Choose infrastructure per component (compute, storage, network, orchestration)
   by **role**, not a fixed vendor — record the choice and why in `decisions`.
3. Define **environments** (dev/stage/prod), promotion, and **rollout/rollback** (SAFE).
4. Mark every **external parameter** (account, region, endpoint, bucket, secret,
   role) as `a confirmar` if not verified — use `templates/hub/environment-parameters.md`;
   never run real infra commands with assumed values.
5. Feed the infra plan into the execution plan; map units to IaC changes.

## Output
Infrastructure mapping + environments + rollout/rollback in the `spec`;
environment-parameters checklist for anything unconfirmed.

## Depth by mode
FAST = rare (usually no infra) · Standard = mapping + environments ·
SAFE = + phased rollout, rollback plan, and environment-parameters gate before deploy.
