---
name: phase-execution
description: Lifecycle — Execution ("Do")
load: phase
triggers:
  phase: execution
  lane: all
  demand-type: all
  agent: all
---

# Lifecycle — Execution ("Do")

Execute aligned to the spec, in small, traceable changes. Owner agent: **Reviewer** — code generation itself is the `sub-activities/code-generation.md` sub-activity, not a separate agent (the roster is fixed in `core/squad.md`). Subject to the supreme law; escalation triggers watched.

## Steps
1. Load `spec` + template + active coding-standard (JIT).
2. **Planning** — numbered plan with checkboxes (single source) → approval (Standard/SAFE); load `../../common/token-budget-policy.md` if the unit needs broad context.
3. **Generation** — step by step / **loop per unit**; **brownfield in-place** (never `file_v2`); mirror the template + SOLID. Code automation-friendly (`data-testid`, etc.).
4. Commit on the **demand branch** at each step; update `state` + `audit`; watch the **escalation triggers**.
5. Technical review (Reviewer); satisfy **DoD Execution** → PR ready.

Each step has concise JIT guidance in `sub-activities/` (`workflow-planning` / `unit-loop` / `code-generation` / `technical-review`) — load only the rungs the demand triggers. These are sub-activities **inside Execution**, never new phases.

## Context compression
Execution may use compressed context only to select which spec excerpts, source
files, tests, and decisions to open. Before editing, open the original source and
the original spec/decision excerpts for the current unit. Compressed context is
not enough to implement code.

## Inherited from AI-DLC
- **Planning + Generation** — numbered plan with checkboxes (single source of truth) → step-by-step generation marking [x]; trace requirement→code.
- **Two-level checkbox** — checkbox in the plan (detail) + in the `state` (phase) → feeds the toolbar.
- **Brownfield in-place** — modify existing files; never create `arquivo_v2`.

## Escalation
Use `../../common/escalation-triggers.md` continuously. If a hard trigger fires, stop the unit, persist state/audit/observability, and ask the responsible human.

## Coding standard
Code per the active coding-standard (SOLID) — use the **language skill** if present (override: most specific wins), else the base (`../../../skills/coding-standard/SKILL.md`). Mirror the applicable **template** repo (load only relevant sections, JIT).

## Outputs
code/change · evidence · updated state · recorded deviations · technical review · PR.

## Human roles
Developer, Tech Lead (review).

## Checkpoint
PR technical review (Standard/SAFE); dependency approvals (SAFE). FAST: only if scope grows.

## Depth by mode
FAST = self-review + small PR · Standard = PR + technical review · SAFE = + dependency management + approvals + evidence.

## Special — emergency
Execution-first: stabilize with minimal authorization; Inception/Design become a post-mortem (`../../demand-types/operational.md`).
