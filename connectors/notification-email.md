# Connector - Notification Email

## type
`notification`

## activation
Destination and triggers are configured in `knowledge/notification.md`. Transport may be SMTP, Graph, SES, MCP, or manual.

## operations
- `send(destination, subject, attachments)` sends strategic notifications only.

## adapter — MCP server (Python, owner decision 2.0.0)
The concrete channel is an MCP server: `scripts/adapters/mcp-email-server.py` (stdlib only, stdio JSON-RPC). Tools: `send_email(subject, body, to?, trigger?, attachments?)`, `send_demand_report(demand_path, to?, trigger?)` — reads `001-state.md` and auto-attaches the demand's metrics, audit, summary, and observability JSONL — `send_telemetry(root_path?, trigger?)` — batches every local observability JSONL to the org `telemetry_to` destination (each line = `{sender, collected_at, source, event}` so many runners' logs aggregate into org metrics; **provisional transport until the telemetry API exists, D45**) — and `email_status()`.
- **Where the destination is registered:** JSON config at `~/.alfred-email.json` (or the path in `ALFRED_EMAIL_CONFIG`) holds non-secret destination, allowlist, mode, and SMTP endpoint metadata. Passwords are accepted only through `SMTP_PASS` supplied by the Devin Secrets UI, environment, or an approved secret store. A legacy `smtp.password` value is refused.
- **States:** `dry-run` (default — composes the RFC-822 message into an outbox folder, never sends) · `active` (SMTP/STARTTLS via `SMTP_*` env vars) · `disabled`.
- **Register (Claude Code):** `claude mcp add alfred-email -- python <framework>/scripts/adapters/mcp-email-server.py` — any MCP host works. The **installer does this for you** (`install/`): it prompts for the destination, writes `~/.alfred-email.json` (dry-run), and registers the MCP when the Claude Code CLI is available.
- **Register (DEVIN CLI):** add to the project's `.devin/config.local.json` (gitignored):
  `{"mcpServers": {"alfred-email": {"command": "python", "args": ["<home>/.alfred/scripts/adapters/mcp-email-server.py"]}}}` — tools appear as `mcp__alfred-email__send_telemetry` etc.
- **CLI mode (no MCP needed):** the same file doubles as a command for any host or scheduler: `python mcp-email-server.py status | send-telemetry --root <path> | send-report --demand-path <path>`.
- **Config (env):** `ALFRED_EMAIL_MODE`, `ALFRED_EMAIL_DEFAULT_TO`, `ALFRED_EMAIL_ALLOWLIST`, `ALFRED_EMAIL_OUTBOX`, `ALFRED_EMAIL_AUDIT`, `SMTP_HOST/PORT/USER/PASS/FROM`. Destination values come from the sigla's `knowledge` configuration — never hardcoded.
- **Guardrails:** recipients outside the allowlist are refused (a new destination requires a human editing config — durable authorization, D44); subject always prefixed `[Alfred-Framework]`; every attempt (sent/dry-run/refused/failed) appends the audit fields below to an audit JSONL.
- **Response format / error guidance:** replies are one concise text line; errors state the exact next step (which env var to set, who must approve) instead of an opaque code.

## degradation
Without a sender, Alfred prepares the subject, body, and attachment list, then reminds the human to send manually. The MCP adapter in `dry-run` produces exactly that prepared message (an `.eml` in the outbox).

## guardrail
Auto-send is allowed only for configured destination + trigger + standard content. Anything outside config requires human confirmation and an audit entry.

## audit fields
destination, trigger, subject, attachment list, send mode, approval reference, result, failure reason.
