# Adapter Implementation

Use this guide when turning a connector contract into a concrete host adapter.

## Adapter States
| State | Meaning | Allowed use |
|---|---|---|
| contract | only the role contract exists | lifecycle may reference the connector type, but no host call is made |
| handoff | Alfred prepares a manual action | human or external process performs the action |
| dry-run | adapter can read/validate and simulate writes | useful before enabling external mutation |
| active | adapter can perform approved operations | must satisfy readiness, audit, and observability rules |
| disabled | adapter exists but must not run | degrade to handoff |

## Activation Rule
An adapter may be marked `active` only when:
- `docs/host-adapter-readiness.md` is complete for that host;
- the adapter file follows `connectors/adapter-template.md`;
- allowed operations and destinations are explicit;
- secret ownership is recorded without exposing the secret;
- every operation has audit fields;
- mutating operations have dry-run or a documented reason why dry-run is impossible;
- degradation path is documented.

## Runtime Rule
Before using an adapter, Alfred checks the demand `001-state.md` Host Adapters section.

If the state says `contract`, `handoff`, `disabled`, `not configured`, or the adapter readiness is missing, Alfred must not call the host. It writes a handoff note and records the missing input.

## No Silent Partial Adapter
A partial adapter must not skip:
- audit;
- JSONL observability;
- approval requirements;
- destination allowlists;
- error recording;
- degradation notes.

If any of these is unavailable, the adapter remains `handoff` or `dry-run`, not `active`.

## Implementation Checklist
1. Choose connector type and host.
2. Create an adapter file from `connectors/adapter-template.md`.
3. Fill readiness using `docs/host-adapter-readiness.md`.
4. Add a minimal fixture or dry-run example.
5. Run `scripts/powershell/validate-connectors.ps1` and add deterministic checks when the adapter has local behavior.
6. Record active status in the HUB/App `state`.
7. Run `scripts/powershell/validate-framework.ps1` for framework changes.

## Human Decisions
Humans decide:
- whether a host adapter is allowed to mutate external state;
- credential owner and rotation policy;
- destination allowlist;
- approval policy;
- when to switch from handoff/dry-run to active.
