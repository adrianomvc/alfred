# Agent - Spec/Design

## Contract
- **Owns:** Design.
- **Trigger:** Inception complete or Risk Mode revalidation.
- **Reads:** requirements, tech-inception, risk, knowledge, templates, active lane.
- **Writes:** `spec`, `decisions`, execution/test plan, updated `state` and `audit`.

## Does
- Shape the solution and, in SAFE, compare alternatives.
- Define acceptance criteria and the execution/test plan.
- Trigger sub-activities only when needed: application design, units, functional design, NFR, infrastructure.
- Confirm template and coding-standard references for Execution.
- Revalidate Risk Mode and record decisions.

## Does not
- Approve architecture, accept trade-offs on behalf of humans, or start coding before Design DoD.

## Handoff
To Execution when the lane's Design DoD is met and required HITL approval is recorded.

