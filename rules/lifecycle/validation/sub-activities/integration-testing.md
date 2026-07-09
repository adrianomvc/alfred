---
name: sub-activity-integration-testing
description: Validate sub-activity — Integration Testing
load: sub-activity
triggers:
  phase: validation
  lane: all
  demand-type: all
  agent: all
---

# Validate sub-activity — Integration Testing

> Trigger: the change **crosses a component or service boundary** (DB, queue,
> job, internal module seam). Optional, inside Validate.

## Purpose
Prove that the parts touched by the change interact correctly when wired together.

## Inputs
`application-design` (component boundaries), integration points from
`tech-inception`, test environment / fixtures, connectors by role.

## Steps
1. Identify the **boundaries** the change crosses (component ↔ component, service
   ↔ datastore/queue).
2. Set up the **integration fixtures** or test environment (by role, not vendor).
3. Exercise the wired path; assert data and control flow across the boundary.
4. Record command, environment, and result; note flakiness or external coupling.
5. Flag boundaries that could not be exercised as a **residual risk**.

## Output
Integration test results with environment notes, and residual risks in the
validation evidence.

## Depth by mode
FAST = usually skipped · Standard = key boundaries · SAFE = all crossed
boundaries with reproducible environment and evidence.
