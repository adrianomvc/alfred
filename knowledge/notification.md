# Policy: notification target (D44)

- **Email target:** adriano.vilela-costa@itau-unibanco.com.br
- **Channel:** A DEFINIR (SMTP / Microsoft Graph / SES / MCP) — fill `connectors/notification-email.md` when known.
- **Trigger points (strategic, NOT per interaction):**
  - Demand done (final report)
  - Critical checkpoint (spec/architecture approval, acceptance)
  - Escalation / risk (D27, mode change, blocked)
  - Incident declared & stabilized (D34)
- **Authorization:** durable (configured here) → transparent auto-send at these points; recorded in `audit`. Ask only if it deviates from this config.
- **Content:** body short; files (`metrics`, `audit` logs, `summary`) **attached**; subject `[Alfred-Framework][<SIGLA>][<id>] <event> — <title>`.
