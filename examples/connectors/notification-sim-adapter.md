# Notification Simulator Adapter Example

A **test double** for the `notification` contract (`connectors/notification-email.md`).
It renders the email and writes it to a sandbox outbox file instead of sending,
so strategic-notification points can be exercised end-to-end without a real
channel, credentials, or recipient. It never sends anything externally.

## identity
- connector type: notification
- adapter name: notification-sim
- host/product: none (in-repo simulator)
- host version: not applicable
- owner: framework example
- status: dry-run

## activation
- configured by: sandbox/example runs only
- credential location: not required
- secret owner: not applicable
- environment: local, offline
- allowed scopes: render subject/body, write to a sandbox outbox
- disabled by: any real/integrated run (use a concrete notification adapter instead)

## operations
| Operation | Mode | Mutates external state | Requires approval | Dry-run support | Audit event |
|---|---|---|---|---|---|
| send | dry-run | no | no (already simulated) | render to outbox | `notification_send` |

## simulated responses (deterministic)
- `send(destination, subject, attachments)` → does not transmit; writes the rendered email (subject + short body + attachment pointers) as a handoff block following `examples/connectors/notification-handoff.md`, and returns a fake reference `SIM-MAIL-0001`.
- destination is taken from `knowledge/notification.md`; in sandbox it is echoed, never contacted.

## inputs
| Input | Required | Source | Secret | Validation |
|---|---|---|---|---|
| destination | yes | `knowledge/notification.md` | no | non-empty |
| subject | yes | template `templates/email.md` | no | starts with `[Alfred-Framework]` |
| attachments | yes | demand artifacts | no | pointers only, not pasted content |

## outputs
| Output | Destination | Format | Retention | Notes |
|---|---|---|---|---|
| rendered email | sandbox outbox / `05-operation/007-audit.md` | markdown | sandbox run | never transmitted |
| send result | audit/JSONL | text/json | sandbox run | fake reference `SIM-MAIL-0001` |

## audit fields
- demand id:
- initiative id:
- actor:
- operation:
- target:
- result:
- external reference:
- failure reason:

## observability event
Every simulated send records:
- `event_type`: simulated notification;
- `tool`: notification-sim;
- `action`: `send`;
- `status`: completed;
- `artifacts_used`: template, knowledge destination, demand artifacts;
- `error`: populated on validation failure;
- `metadata.connector`: `notification`.

## degradation
This is already the degraded path: with no real channel, Alfred renders the email
and records it as a handoff/reminder. Swapping in a real notification adapter
(SMTP, Graph, SES, MCP) is a connector change, not a rule change.

## safety checks
- no secret is printed to markdown, JSONL, console, or logs;
- nothing is transmitted externally (render-only);
- subject must carry the `[Alfred-Framework]` prefix;
- a real/integrated run must not use this adapter;
- failures are recorded before stopping.

## fixture
- minimal fixture path: `examples/connectors/notification-handoff.md`
- validation command: `powershell -ExecutionPolicy Bypass -File scripts/powershell/validate-connectors.ps1`
- expected result: connector and adapter validation completes
