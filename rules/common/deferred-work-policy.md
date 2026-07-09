---
name: common-deferred-work-policy
description: Common rule - deferred and low-priority token work
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Deferred Work Policy

## Trigger
Load this rule before using host features that trade latency for lower cost, such
as batch, flex, background, queued, or low-priority execution.

## Rule
Use deferred execution only for work that is not on the human's critical path
and does not make final decisions by itself.

Good candidates:
- metrics rollups, usage normalization, and report generation;
- large read-only scans that produce candidate pointers;
- stale reverse-engineering refreshes that will be reviewed later;
- non-urgent summaries, notifications, and follow-up grouping;
- broad test-log clustering after the original failing evidence is preserved.

Bad candidates:
- interactive incident stabilization;
- Design approval, SAFE architecture decisions, or risk classification;
- code edits, merge decisions, or final validation judgment;
- anything waiting on human clarification right now.

## Cost Routing
When the host supports cheaper deferred modes, prefer them for good candidates
after recording:
- objective and expected output artifact;
- source refs or query window;
- max runtime or scope;
- model tier/effort if configurable;
- fallback if the deferred job fails or returns late.

Deferred outputs are drafts or inputs. Before they affect code, decisions, or
validation, Alfred must load the relevant original sources and apply the normal
lane/phase rules.

## Degradation
If the host has no deferred/batch/flex mode, run the task normally with bounded
context and the cheapest tier allowed by `core/model-policy.md`, or leave it as
a follow-up if it is not needed now.

## Audit
Record deferred jobs in `audit` or observability metadata with source, mode,
status, and the artifact produced.
