---
name: sub-activity-memory-distillation
description: Operation sub-activity — Memory Distillation
load: sub-activity
triggers:
  phase: operations
  lane: all
  demand-type: all
  agent: all
---

# Operation sub-activity — Memory Distillation

> Trigger: at demand close, after `summary`. Optional, inside Operation. Turns
> this demand's lessons into cross-demand memory (`rules/common/memory-policy.md`).

## Purpose
Capture the **decisions and gotchas** a future demand should not have to re-learn,
as compact observations indexed for JIT retrieval — without re-dumping context.

## Steps
1. Scan this demand's `decisions`, `audit`, `summary`, and post-mortem for lessons
   that will help a **future** demand (not already an `insight`, `knowledge`, or
   plain `summary`).
2. **Propose** 0..N observations to the human (do not write yet): for each, a
   `type` (`decision`｜`gotcha`), an 8–12 word `title`, a `trigger`/tags, and the
   source artifact path. Few, high-signal — keep the index compact.
3. On human confirmation, write each as `alfred-docs-hub/memory/<slug>.md` from
   `templates/hub/memory-observation.md` (pointer to the original artifact, never
   a copy of the decision).
4. Regenerate the index: `python ~/.alfred/scripts/workflow/generate-memory-index.py -Root <hub>`.
5. Record in `audit` which observations were added and that the human confirmed.

## Guardrails
Additive and non-authoritative: an observation never rewrites or replaces the
source of truth. Nothing is written without human confirmation. If there is no
lesson worth carrying forward, write nothing — memory stays high-signal.

## Output
0..N confirmed observation files and a regenerated `005-memory.md`.

## Depth by mode
FAST = usually skipped, or one observation if a real gotcha appeared · Standard =
propose the demand's key decisions/gotchas · SAFE = + traceability of each
observation to its decision/audit source.
