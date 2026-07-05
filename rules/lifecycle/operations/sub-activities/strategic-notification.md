# Operation sub-activity — Strategic Notification

> Trigger: a **notification channel is configured** in `knowledge/notification.md`.
> Optional, inside Operation.

## Purpose
Send (or remind to send) the strategic close update so stakeholders learn the
outcome through the agreed channel — and the action is auditable.

## Inputs
`knowledge/notification.md` (configured channel/recipients/template), the
`summary`, the notification connector contract (`../../../../connectors/`).

## Steps
1. Read the configured **channel, recipients, and template** from
   `knowledge/notification.md`.
2. Compose the update from the `summary` (outcome + link + follow-ups).
3. If a working channel exists, **send**; otherwise **remind** the human with the
   ready-to-send content (notification is a contract/template, not yet a live
   channel).
4. **Telemetry batch (automatic when configured):** if `knowledge/notification.md`
   defines a `telemetry_to` destination, send the demand's observability JSONL as a
   telemetry batch (`send_telemetry` on the MCP e-mail adapter, or remind the human)
   at every generation that appended events — closure, hub-sync, rollup. This is the
   **provisional transport until the telemetry API exists (D45)**: destination +
   trigger live in config (durable authorization), so no per-send prompt; the send
   is audited like any notification.
5. **Record** the action (sent / reminded) in `audit`.
6. Never send sensitive content to an external channel without the configured
   policy allowing it.

## Output
A sent or drafted strategic notification, with the action recorded in `audit`.

## Depth by mode
FAST = optional / skipped · Standard = notify or remind + audit · SAFE = +
sponsor-level recipients and explicit confirmation.
