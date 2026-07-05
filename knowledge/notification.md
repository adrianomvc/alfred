# Notification Defaults

## destination
Configured by the adopting sigla/HUB. Do not hardcode personal addresses in framework logic.

Where to register it, in precedence order:
1. sigla/HUB `knowledge` (the organizational record of destination + triggers);
2. machine level for the MCP e-mail adapter: `~/.alfred-email.json` (`default_to`, `allowlist`, `mode`, `smtp{}`) or `ALFRED_EMAIL_CONFIG`;
3. environment variables (`ALFRED_EMAIL_DEFAULT_TO`, `ALFRED_EMAIL_ALLOWLIST`, ...) override the file per session.

## telemetry destination (org)
- telemetry_to: `adriano.vilela-costa@itau-unibanco.com`
- purpose: aggregate observability logs from **every person running Alfred** into org metrics.
- transport: e-mail batches via the MCP adapter (`send_telemetry`) — **provisional until the telemetry API exists (D45)**; when the API arrives, only this transport changes, not the rules.
- trigger: automatic at each generation that appends observability events (demand closure, hub-sync, rollup) — durable authorization: destination + trigger live here, so no per-send prompt; every send is audited.
- the installer copies this value into each runner's `~/.alfred-email.json` (`telemetry_to`).

## default triggers
- demand completed
- critical checkpoint requiring action
- escalation or Risk Mode change
- incident stabilized
- optional periodic status
- telemetry batch (observability logs → telemetry destination above)

## guardrails
Notify only configured destinations and triggers automatically. New destination, unusual content, or sensitive data requires human confirmation and an `audit` entry.

