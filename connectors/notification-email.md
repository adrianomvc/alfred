# Connector - Notification Email

## type
`notification`

## activation
Destination and triggers are configured in `knowledge/notification.md`. Transport may be SMTP, Graph, SES, MCP, or manual.

## operations
- `send(destination, subject, attachments)` sends strategic notifications only.

## adapter — MCP server (Python, owner decision 2.0.0)
The concrete channel is an MCP server: `scripts/python/adapters/mcp-email-server.py` (stdlib only, stdio JSON-RPC). Tools: `send_email(subject, body, to?, trigger?, attachments?)`, `send_demand_report(demand_path, to?, trigger?)` — reads `001-state.md` and auto-attaches the demand's metrics, audit, summary, and observability JSONL — `send_telemetry(root_path?, trigger?)` — batches every local observability JSONL to the org `telemetry_to` destination (each line = `{sender, collected_at, source, event}` so many runners' logs aggregate into org metrics; **provisional transport until the telemetry API exists, D45**) — and `email_status()`.
- **Where the destination is registered:** JSON config at `~/.alfred-email.json` (or the path in `ALFRED_EMAIL_CONFIG`) holding `default_to`, `allowlist`, `mode`, `smtp{}`; env vars override it. This is the machine-level mirror of the sigla's `knowledge` notification config — the durable authorization (D44) lives in configuration, never in a prompt.
- **States:** `dry-run` (default — composes the RFC-822 message into an outbox folder, never sends) · `active` (SMTP/STARTTLS via `SMTP_*` env vars) · `disabled`.
- **Register (Claude Code):** `claude mcp add alfred-email -- python <framework>/scripts/python/adapters/mcp-email-server.py` — any MCP host works. The **installer does this for you** (`install/`): it prompts for the destination, writes `~/.alfred-email.json` (dry-run), and registers the MCP when the Claude Code CLI is available.
- **Config (env):** `ALFRED_EMAIL_MODE`, `ALFRED_EMAIL_DEFAULT_TO`, `ALFRED_EMAIL_ALLOWLIST`, `ALFRED_EMAIL_OUTBOX`, `ALFRED_EMAIL_AUDIT`, `SMTP_HOST/PORT/USER/PASS/FROM`. Destination values come from the sigla's `knowledge` configuration — never hardcoded.
- **Guardrails:** recipients outside the allowlist are refused (a new destination requires a human editing config — durable authorization, D44); subject always prefixed `[Alfred-Framework]`; every attempt (sent/dry-run/refused/failed) appends the audit fields below to an audit JSONL.
- **Response format / error guidance:** replies are one concise text line; errors state the exact next step (which env var to set, who must approve) instead of an opaque code.

## degradation
Without a sender, Alfred prepares the subject, body, and attachment list, then reminds the human to send manually. The MCP adapter in `dry-run` produces exactly that prepared message (an `.eml` in the outbox).

## guardrail
Auto-send is allowed only for configured destination + trigger + standard content. Anything outside config requires human confirmation and an audit entry.

## audit fields
destination, trigger, subject, attachment list, send mode, approval reference, result, failure reason.
