# Connector: telemetry — central API (future)

- **Type:** telemetry. **Status:** FUTURE (API to be provided).
- **Operations:** `send_events(batch) -> ack`.
- **Use:** ship continuous logs/events to a central observability backend.
- **Degradation (now):** events remain in `audit`/`metrics` (markdown) and/or go by email .
- **Pluggable:** when the API exists, only this adapter is filled — rules untouched (DIP).
