# Inception sub-activities

Optional steps **inside Inception** (never new phases). They run **by trigger**
and their depth scales with the Risk Mode. Loaded just in time — only the ones
the demand needs. Distilled from AI-DLC, kept stack-agnostic; reference
connectors/skills by role.

## The ladder (run only the rungs the demand triggers)
| Sub-activity | Trigger | Gives |
|---|---|---|
| `business-inception` | Produto stream with external `inception-input` | validated business problem (imported, not redone) |
| `technical-inception` | always (Alfred) | affected systems via reverse-eng, integration points, technical risks, feasibility |
| `requirements-elicitation` | clarity is vague/incomplete | structured multiple-choice questions + gate + contradiction detection |
| `risk-mode-proposal` | Standard/SAFE (human confirms the lane) | intent → pre-filled Risk Mode checklist + proposed lane |

## Order (when several fire)
`business-inception` → `technical-inception` → `requirements-elicitation` → `risk-mode-proposal`.
Each is optional; skip with justification recorded in the state/audit.

## Where the output lands
Into the demand `problem`/`requirements` and `tech-inception`, plus the proposed
Risk Mode that pre-fills the lane. No separate per-unit folders.

## Depth by mode
FAST usually collapses these into a one-paragraph intent in the state. Standard
runs the rungs the demand triggers, briefly. SAFE runs them with stakeholders,
risk analysis, and explicit scope confirmation.
