# Playbooks

A playbook is the **operational step-by-step** for one demand type. The
demand-type files (`rules/demand-types/*.md`) declare *what* a type is
(emphasis, mode tendency, sub-activities); a playbook says *how to run it* —
the ordered actions, artifacts, and HITL checkpoints per phase.

Playbooks are optional and loaded just in time: the Orchestrator loads the
playbook for the active type only when it applies. They do not replace the
lane (governance) or the lifecycle (phases) — they sequence them for a type.

## When to write one
Distill a playbook from **real, closed demands**, not from theory. A new type
runs from the demand-type contract + lifecycle until enough real runs justify a
reusable roteiro (anti-overconfidence: do not invent steps that were not proven).

## Structure (each playbook)
- **Applies to** — type(s) and the trigger that selects this playbook.
- **Mode tendency** — default lane and the hard overrides that raise it.
- **Per phase** (Inception → Design → Execution → Validate → Operation) — key
  actions, artifacts produced, and the HITL checkpoint that gates the phase.
- **Typical units** — the usual decomposition (units stay inside one demand state).
- **Rollback & risks** — what makes it irreversible and how to back out.
- **Done when** — the acceptance condition for the type.

## Rules
- English file, pt-BR generated content (same as the rest of the framework).
- Reference connectors/skills by **role**, never a concrete tool name.
- Keep ~1 screen; split when it grows; reference from the demand-type file.

## Available
| Playbook | Type | Link |
|---|---|---|
| Migration | Engineering / migration | `rules/demand-types/playbooks/migration.md` |
