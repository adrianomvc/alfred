# Notification Defaults

## destination
Configured by the adopting sigla/HUB. Do not hardcode personal addresses in framework logic.

Where to register it, in precedence order:
1. sigla/HUB `knowledge` (the organizational record of destination + triggers);
2. machine level for the MCP e-mail adapter: `~/.alfred-email.json` (`default_to`, `allowlist`, `mode`, `smtp{}`) or `ALFRED_EMAIL_CONFIG`;
3. environment variables (`ALFRED_EMAIL_DEFAULT_TO`, `ALFRED_EMAIL_ALLOWLIST`, ...) override the file per session.

## default triggers
- demand completed
- critical checkpoint requiring action
- escalation or Risk Mode change
- incident stabilized
- optional periodic status

## guardrails
Notify only configured destinations and triggers automatically. New destination, unusual content, or sensitive data requires human confirmation and an `audit` entry.

