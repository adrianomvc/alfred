# Connector: notification — email

- **Type:** notification. **Status:** channel A DEFINIR (SMTP / Microsoft Graph / SES / MCP).
- **Operations:** `send(dest, subject, attachments)`.
- **Target:** from `knowledge/notification.md` (registered: adriano.vilela-costa@itau-unibanco.com.br).
- **Trigger points (not per interaction):** demand done · critical checkpoint · escalation · incident — configurable in knowledge.
- **Authorization:** durable (configured once) → sends transparently at configured points; records in `audit`. Asks only if it deviates from config .
- **Format:** subject `[Alfred-Framework][<SIGLA>][<id>] <event> — <title>`; body short; **files attached** (see templates/email.md).
- **Degradation:** no channel → remind human to send manually.
