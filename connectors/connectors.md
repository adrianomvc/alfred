# Connectors registry + contracts

Connector = ACCESS to an external system. Rules depend on the **type/contract**, never the concrete (DIP). Optional: no connector → degrade to manual.

| Type | Contract (operations) | Degradation |
|---|---|---|
| observability | `get_logs(query, window) -> entries` · `get_alarms` | human provides logs |
| vcs | `create_branch(id)` · `commit(msg)` · `open_pr(base,head)` — never merge protected | human commits/opens PR |
| tracker | `get_demand(id) -> {title,desc,type}` · `open_issue` | human informs id / opens issue |
| notification | `send(dest, subject, attachments)` | remind human to send manually |
| telemetry (future) | `send_events(batch) -> ack` | events stay in audit/metrics (markdown) |

Each concrete connector file declares: type · activation (config/credential) · operations · degradation · status.
Golden rule: swap CloudWatch→Datadog = new `observability` connector, rules untouched.
