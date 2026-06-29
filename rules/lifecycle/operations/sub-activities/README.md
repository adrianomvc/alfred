# Operation sub-activities

Optional steps **inside Operation** (never new phases). They run **by trigger**
and their depth scales with the active lane. Loaded just in time. Operation
closes the demand after release/merge with traceability, metrics, and a
resumable summary. Owner: **Metrics** agent.

## The ladder (run only the rungs the demand triggers)
| Sub-activity | Trigger | Gives |
|---|---|---|
| `metrics-collection` | always | elapsed/phase time, interactions, model/tokens/cost, defects, blockers from JSONL |
| `baseline-drift-check` | Standard/SAFE | flags: too much SAFE, excessive cost, repeated rework, missing post-mortem |
| `closure-summary` | always | `summary` + refreshed `index` + resume note for the next session |
| `hub-sync` | App-only mode | push local metrics/changes back to the HUB |
| `strategic-notification` | a notification channel is configured | send/remind the strategic update + record in `audit` |
| `followup-conversion` | open follow-ups / debts exist | convert them into new demands |

## Order (when several fire)
`metrics-collection` → `baseline-drift-check` → `closure-summary` →
(`hub-sync` if App-only) → `strategic-notification` → `followup-conversion` → close `state`.

## Where the output lands
Into `metrics`, the `summary`, the HUB/App `index`, the notification record in
`audit`, and any new demands spun from follow-ups. Then `state` is closed.

## Depth by mode
FAST = short close note + lean metrics. Standard = summary + baseline check.
SAFE = complete evidence, post-release watch, and explicit follow-ups.
