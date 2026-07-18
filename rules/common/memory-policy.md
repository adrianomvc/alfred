---
name: common-memory-policy
description: Common rule - cross-demand observation memory (progressive disclosure)
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Memory Policy

Cross-demand memory of **decisions and gotchas**, so a new demand does not
re-learn what a past one already discovered. Progressive disclosure, markdown-first
(D3): a compact index is scanned first, an observation's detail loads JIT.

## Shape (3 layers, in the HUB)
- **Index (compact):** `alfred-docs-hub/005-memory.md`, generated from frontmatter
  by `scripts/workflow/generate-memory-index.py` (deterministic, drift-checked).
- **Detail:** `alfred-docs-hub/memory/<slug>.md`, one observation per file (~1
  screen), loaded by id only when relevant (`templates/hub/memory-observation.md`).
- Types are **narrow: `decision` and `gotcha` only** (high signal). Extend later.

## Inject (always, at session start)
On boot, load the memory **index** (compact) if it exists — via a SessionStart
hook where available, otherwise the boot sequence reads the file
(`core/boot.md`). The agent always sees what memory exists.

## Retrieve (JIT)
When classifying the new demand, scan the index by `trigger`/`tags` and open
**only** the observations that match — never the whole set. An observation is a
**pointer, not authority**: to decide or edit, open the original artifact it
points to (`rules/common/context-compression-policy.md`).

Use `scripts/workflow/memory-query.py`: `startup --budget <tokens>` injects a
bounded gotcha-first/recent-first index, `search` narrows candidates, `timeline`
shows bounded neighbors, and `get` opens only selected detail. The index exposes
an estimated token cost and marks a pointer stale when its recorded source hash
no longer matches. Missing helpers degrade to the same index-first manual flow.

## Distil (at demand close, human-confirmed)
In Operation (`rules/lifecycle/operations/sub-activities/memory-distillation.md`),
Alfred **proposes** 0..N observations from the demand's `decisions`, `audit`, and
`summary`; the human **confirms** before they are written (additive,
non-authoritative — the same "propose → human ratifies" discipline as `insights`).
Then regenerate the index. This keeps the memory reproducible: the index is
generated from frontmatter; only the observation content is distilled and reviewed
(so it respects the boundary that rejected LLM-summarizing *framework rules*).

## Boundary (do not duplicate)
- **observation** = a tactical decision/gotcha carried **across demands**;
- `insights` = ratified metric trends; `knowledge` = org policy (a mandate);
- `summary` = one demand's recap. Write an observation only when it helps a
  **future** demand and is not already an insight/knowledge/summary.

## Token economy
The startup slice is **budgeted by contract**; the complete index may grow on
disk without being injected whole. Archive stale/low-value observations by
recency and relevance, and measure retrieval with
`scripts/metrics/evaluate-context-benchmark.py` rather than assuming fewer
tokens preserved recall.

## Degradation (D3)
No SessionStart hook / no MCP → the boot reads the index file and JIT-opens
details as plain markdown. Memory is optional: with no HUB memory, nothing loads
and work proceeds normally.
