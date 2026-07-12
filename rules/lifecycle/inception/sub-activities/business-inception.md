---
name: sub-activity-business-inception
description: Inception sub-activity — Business Inception
load: sub-activity
triggers:
  phase: inception
  lane: all
  demand-type: all
  agent: all
---

# Inception sub-activity — Business Inception

> Trigger: **Produto stream** carrying an external `inception-input`. Optional,
> inside Inception. Alfred **validates** the business problem; it does not redo
> business discovery.

## Purpose
Ingest and validate the business framing produced by an upstream discovery agent
so Execution rests on a real problem, not a re-derived one.

## Inputs
External `inception-input` (problem, value, target users/journey), the active
demand type (`../../../demand-types/product.md`), `knowledge` policies (D42).

## Steps
1. Load the `inception-input`; do **not** regenerate business discovery.
2. Check **completeness**: problem statement, value/outcome, affected users or
   journey, success signal. Mark each present/missing.
3. If a required field is missing, raise a **requirements question** (hand off to
   `requirements-elicitation`) instead of inventing the answer.
4. Reconcile the business framing with the technical lens (`technical-inception`);
   flag contradictions.
5. Record the validated business problem into the demand `problem`.

## Output
Validated business problem + objective in the demand `problem`; list of missing
business fields routed to elicitation; contradictions flagged.

## Depth by mode
FAST = rarely applies (Produto is usually Standard+) · Standard = completeness
check + gaps · SAFE = + stakeholders, value hypothesis, and explicit scope.
