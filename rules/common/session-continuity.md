# Session continuity — operational prompt (D16/D28/D37)

The `state` (HUB) is the live source of truth — always resume from it.

## Persist (D37)
Write `state` (and commit on the demand branch) at EACH: step/unit, phase transition, checkpoint, decision, and pause. Never accumulate much work without persisting. Worst case on crash = lose the in-flight step, never the demand.

## Resume (D16/D28)
On boot, list OPEN demands (in-progress / on-hold / blocked) with last activity; ask which to resume. Pausing is normal — never auto-abandon. Only humans cancel (write a mini-`summary` with the reason).

## What `state` must always carry
phase · mode · progress checklist · next step · current model · cost · links · last activity — enough to rebuild context without re-reading everything.
