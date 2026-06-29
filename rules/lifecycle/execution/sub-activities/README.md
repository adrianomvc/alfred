# Execution sub-activities

Optional steps **inside Execution** (never new phases). They run **by trigger**
and their depth scales with the Risk Mode. Loaded just in time. Distilled from
AI-DLC (Planning + Generation), kept stack-agnostic; reference connectors/skills
by role and use the active coding-standard/language skill.

## The ladder (run only the rungs the demand triggers)
| Sub-activity | Trigger | Gives |
|---|---|---|
| `workflow-planning` | Standard/SAFE (any non-trivial change) | numbered plan with checkboxes (single source), sequence, parallelization |
| `unit-loop` | demand decomposed into >1 unit (D24) | per-unit generate→commit→review loop, two-level checkbox |
| `code-generation` | always | in-place brownfield change, SOLID, template mirror, automation-friendly |
| `technical-review` | Standard/SAFE | Reviewer pass against spec/standard → PR ready |

## Order (when several fire)
`workflow-planning` → (`unit-loop` wrapping) `code-generation` → `technical-review`.
Each is optional; skip with justification in the execution plan.

## Where the output lands
Into code on the **demand branch**, plus updated `state`/`audit` at each step and
the two-level checkbox that feeds the toolbar. No `arquivo_v2` — brownfield in place.

## Depth by mode
FAST = self-review + small PR, plan optional. Standard = plan + step-by-step
generation + technical review. SAFE = + dependency management, approvals, and
evidence per step.
