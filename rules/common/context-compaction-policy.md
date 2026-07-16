---
name: common-context-compaction-policy
description: Common rule - when to compact conversation context safely
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Context Compaction Policy

## Trigger
Load this rule when the host compacts/summarizes the conversation (automatically
or via a command such as the DEVIN CLI `/compact`), or when the context window is
filling and compaction is being considered.

## Rule
Compaction is a **conversation** operation owned by the host. It never rewrites a
framework rule or a demand artifact, and its summary is never the source of
truth. After any compaction, re-read `001-state.md` before acting — the state
file, not the summary, is authoritative.

The safety of compaction follows an invariant Alfred already guarantees: the
`state` is saved at defined points and, by `core/boot.md`, the `state` alone
reconstructs context. **So compaction is safe exactly where the `state` was just
saved and committed, and unsafe anywhere else.** Compaction safety = state
freshness. This adds no new save discipline; it reuses `session-continuity.md`.

## Safe points (compact here)
Right after the `state` is persisted and committed (see the save-points in
`rules/common/session-continuity.md`):
- end of a unit/step;
- a phase transition;
- a recorded decision;
- a HITL checkpoint that has already been decided;
- a pause.

On the DEVIN CLI, this is where to run `/compact`.

## Forbidden points (never compact here)
- mid-step with uncommitted edits;
- a pending HITL/SAFE approval — the human's words in the conversation are the
  evidence and must not be summarized away before the decision is recorded;
- an incident/escalation not yet written to `audit`;
- an artifact write in flight.

## Preflight
Before compacting, persist the `state` and commit. If you cannot save now, do not
compact — finish the step first. Compaction after a save is lossless; compaction
before a save can drop the in-flight step.

## Minimum content to preserve
When the host compacts, the summary must preserve at least: the demand id and the
`001-state.md` path, the files modified in the current step, the next step, the
pending checkpoint and its owner, and any open escalation. If the host lets a
hook re-inject context after compaction, re-inject the `001-state.md` path;
otherwise re-read it on the next turn.

## Degradation
If the host has no compaction command or hook, nothing changes: the same
save-point discipline is what already makes resume work. Never block work because
a host lacks compaction controls.

## Audit
For material Standard/SAFE work, record in `audit` or observability metadata when
a compaction happened relative to the last save-point, whether the state was
fresh, and that the state was re-read afterwards.
