---
name: common-token-budget-policy
description: Common rule - token budget preflight
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Token Budget Policy

## Trigger
Load this rule before assembling large multi-file context, scanning many files,
running a token-heavy phase, or opening long logs/diffs.

## Rule
Plan the token spend before loading context. The goal is to preserve quality by
spending tokens on the sources that matter, not on unfiltered bulk.

## Preflight
Before a large context load, record a short budget note:
- objective for this step;
- lane and phase;
- expected context classes: framework rules, state, spec, source files, tests,
  logs, diffs, external data;
- max scope to inspect now;
- what will be deferred, searched, summarized, or skipped.

## Selection Order
1. Load mandatory governance first: supreme law, active lane, phase, demand type,
   and the current sub-activity.
2. Load the demand `state`, current plan, and acceptance criteria.
3. Use `rg`, indexes, manifests, codebase-memory, or bounded tool search to find
   candidate sources.
4. Open original sources only for the current decision or unit.
5. Use compression only as a selector, following
   `rules/common/context-compression-policy.md`.

## Guardrails
- Do not reduce context by dropping acceptance criteria, constraints, rollback,
  security, data, privacy, incident, or SAFE approval requirements.
- Do not read entire repositories, generated folders, full logs, full diffs, or
  dependency trees unless the step explicitly requires it.
- Split large work into units when one context bundle would mix unrelated
  decisions or repos.
- If the model starts looping, stop, restate the remaining unit, and reload only
  the missing original sources.

## Degradation
If the host has token counting, use it. If not, use file counts, line counts,
`git diff --stat`, bounded reads, and human-readable budget notes. Never block
work only because exact token counting is unavailable.

## Audit
For material Standard/SAFE work, record the budget note or the chosen context
strategy in `audit` or observability metadata.
