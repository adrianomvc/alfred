# Common rule — session continuity

Inherited from AI-DLC `session-continuity`. The core of resilience: a demand can be paused and resumed later without starting over. Alfred **never** declares abandonment by inactivity.

## State persistence granularity
Resuming without restarting depends on saving the `state` often enough:
- **Save the `state`** (and what changed): on completing **each unit/step**, at **each phase transition**, at **each HITL checkpoint**, on **each decision**, and on **pause**. Never accumulate much work without persisting.
- **Commit on the demand branch** — HUB/app artifacts must be committed to survive across sessions/machines/people. Recommended: commit at the end of each significant step.
- **Loss granularity:** if the session drops, resume from the last saved `state` — at most the in-flight step is lost, never the demand.

## Minimum content to resume
The `state` always has phase, mode, progress, next step, and links — enough for boot to reconstruct context without re-reading everything.

## App-only persistence
If Alfred is running only inside an app repo, it cannot update the HUB `state` directly. Persist local progress under `.alfred-docs-app/<id-iniciativa>/<id-demanda>/`:
- update `001-index.md` with current local status and links;
- append app events to `05-operation/008-observability-log.jsonl`;
- update `05-operation/009-hub-sync.md` with the HUB changes that must be applied later;
- commit app artifacts on the demand branch.

The HUB is still the final source of truth. Until `05-operation/009-hub-sync.md` is imported into the HUB, the demand is **pending sync**.

## Observability write timing
Observability is append-only and must not wait for a final summary. Append one JSONL line immediately for each relevant interaction, step start, artifact write, step completion, error, checkpoint, and pause. Every event must include Alfred version metadata and explicit output artifact paths when files were created or updated.

## Demand states
`em andamento` (in progress) · `em espera` (on hold — first-class, resumable anytime) · `bloqueada` (blocked — depends on external) · `aguardando checkpoint` (awaiting checkpoint) · `concluída` (done) · `cancelada` (cancelled — only by explicit human decision).
- **Multi-demand:** several may be in progress/on hold at once; the `id` + `state` keep each isolated and resumable.
- **`última atividade`** (last-activity date) in the `state` helps notice long-stalled demands — but the human decides to cancel/resume. No auto-cancellation.
- **Cancel (explicit):** produces a mini-`summary` (why) + updates the `index` (leaves the active set), then archives. Pausing does not archive.

## Welcome back
On boot, list the sigla's open demands (in progress / on hold / blocked) with last activity and ask which to resume (`core/boot.md`).
