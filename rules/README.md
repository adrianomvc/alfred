# Rules — the customized AI-DLC engine

This is the JIT entry point for `rules/`. Load this index first, then only the
file for the active phase, lane, demand type, or agent — never the whole folder.
For a generated metadata view, use [`rules-index.md`](rules-index.md).

A demand always combines **one demand type × one lane**, runs through the
**lifecycle**, is carried out by **agents**, and obeys the **common** rules.

## Two orthogonal axes
| Axis | Folder | Question it answers | Members |
|---|---|---|---|
| Path (per stream) | `demand-types/` | *what kind of work is this?* | `product.md` · `operational.md` · `engineering.md` (+ `playbooks/`) |
| Governance (per mode) | `lanes/` | *how much process does its risk require?* | `fast.md` · `standard.md` · `safe.md` |

## Process and actors
| Folder | Purpose | Entry |
|---|---|---|
| `lifecycle/` | the 5 phases (Inception → Design → Execution → Validate → Operation); each phase folder has a `sub-activities/` ladder loaded JIT | `lifecycle/lifecycle.md` |
| `agents/` | specialty roles materialized as artifacts; communicate through `state`, not with each other | `orchestrator` · `discovery` · `spec-design` · `reviewer` · `metrics` |
| `common/` | cross-cutting rules, loaded by event (only the supreme law is always in force) | overconfidence · question-format · escalation-triggers · units · session-continuity · content-validation · terminology · workflow-changes · verification-loop · budget-policy · memory-policy · terminal-token-policy · prompt-caching-policy · tool-discovery-policy · context-compression-policy · context-compaction-policy · context-retrieval-policy · token-budget-policy · deferred-work-policy |

## When to load what
- Helper path: `scripts/workflow/context-manifest.py --phase --lane --demand-type --agent [--sub-activity]` prints the minimal ordered rule files; if it cannot run, use the table below plus `rules-index.md`.
- Start of a demand → `demand-types/<stream>.md` + `lanes/<mode>.md`.
- Each phase → `lifecycle/<phase>/` (and only the needed `sub-activities/` file).
- Always in force → the supreme law (`core/principles.md`, enforced by `common/overconfidence.md`) and the active lane's DoD.
- The other `common/` rules load **on their event, not upfront**: `question-format` when asking the human · `escalation-triggers` when a trigger may fire or an error occurs · `session-continuity` on pause/resume/compaction · `content-validation` when ingesting external content · `units` when planning/running units · `workflow-changes` when the flow itself changes · `verification-loop` when implementing/correcting against tests · `budget-policy` when a demand carries a cost/usage budget · `memory-policy` when reading or distilling memory · `terminal-token-policy` before shell commands or large terminal output · `prompt-caching-policy` when a host exposes prompt caching or Alfred assembles multi-file context · `tool-discovery-policy` before using optional tools, MCP servers, connector adapters, external catalogs, or specialty skills · `context-compression-policy` when RAG/compressed summaries/codebase-memory select context · `context-compaction-policy` before/after host context compaction · `context-retrieval-policy` when choosing what to read into context · `token-budget-policy` before large context loads or token-heavy steps · `deferred-work-policy` before batch/flex/background work · `terminology` when naming artifacts/ids.

## Invariant
Extend by **adding** a demand type, lane, agent, or sub-activity — never by
adding a phase. Rules reference the contract/role (lane, connector, agent),
never the concrete.
