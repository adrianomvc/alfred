---
name: sub-activity-risk-mode-proposal
description: Inception sub-activity — Risk Mode Proposal
load: sub-activity
triggers:
  phase: inception
  lane: all
  demand-type: all
  agent: all
---

# Inception sub-activity — Risk Mode Proposal

> Trigger: **Standard/SAFE** demands (FAST is self-evident). Optional, inside
> Inception. Alfred proposes; a human confirms the lane.

## Purpose
Map the analyzed intent to a **Risk Mode** so the right lane (FAST/Standard/SAFE)
governs depth, DoD, and checkpoints — without the human filling a blank form.

## Inputs
Intent analysis (clarity/type/scope/complexity), `tech-inception` risks, the lane
contracts (`../../../lanes/*`), `knowledge` policies that can force a floor.

## Steps
1. Pre-fill the **Risk Mode checklist** from intent: scope size, blast radius,
   data sensitivity, reversibility, external dependencies.
2. Derive a **proposed lane** from the checklist (FAST / Standard / SAFE).
   Optional helper: `classify-risk` (`scripts/powershell/` · `scripts/python/`)
   computes the axes, fires the hard overrides, and prints the pt-BR block for
   `004-risk.md`. `core/risk-mode.md` stays the source of truth; without the
   helper, apply the same tables manually (D3).
3. State **why** — the one or two factors that set the lane (transparency, D46).
4. Present for **human confirmation** in Standard/SAFE; record the decision.
5. If a later signal (e.g., an NFR) forces a stronger lane, record the override
   in `decisions` and re-propose.

## Output
A pre-filled Risk Mode checklist, a proposed lane with justification, and the
confirmed lane recorded in `state`/`decisions`.

## Depth by mode
FAST = implicit (small, reversible) · Standard = checklist + proposed lane +
confirmation · SAFE = + documented risk factors and sponsor awareness.
