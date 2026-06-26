# Session continuity (D16/D28/D37)

- The `state` (HUB) is the live source of truth — resume from it.
- Persist the `state` (and commit on the demand branch) at each step/phase/checkpoint/decision/pause (D37).
- On boot, list **open demands** (in-progress/on-hold/blocked) with last activity; ask which to resume (D28).
- Pausing is normal; never auto-abandon. Only humans cancel (with a mini-summary).
