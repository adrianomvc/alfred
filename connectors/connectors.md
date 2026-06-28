# Connectors Registry

Connectors are optional adapters. Alfred rules depend on the **role contract**, not a concrete tool. Without a connector, Alfred degrades to markdown and asks the human for the missing input/action.

## Required sections per connector
- `type`
- `activation`
- `operations`
- `degradation`
- `audit fields`

Concrete host adapters must also follow `connectors/adapter-template.md` and `docs/adapter-implementation.md`.

## Types
| Type | Contract |
|---|---|
| observability | `get_logs(query, window)`, `get_alarms()` |
| vcs | `create_branch(id)`, `commit(message)`, `open_pr(base, head)` |
| tracker | `get_demand(id)`, `open_issue(data)` |
| notification | `send(destination, subject, attachments)` |
| telemetry | `send_events(batch)` |
| usage-cost | `read_usage(window, filters)`, `map_usage(record)`, `append_usage_event(event)` |

## Adapter states
| State | Meaning |
|---|---|
| contract | role contract only; no host call |
| handoff | Alfred prepares a manual action |
| dry-run | adapter can validate/simulate without external mutation |
| active | adapter may execute approved operations |
| disabled | adapter exists but must not run |

## Golden rule
Rules reference the type. Swapping CloudWatch for Datadog or GitHub for GitLab is a connector change, not a lifecycle change.
