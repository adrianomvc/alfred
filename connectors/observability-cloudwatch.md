# Connector: observability — CloudWatch (D34/D14)

- **Type:** observability. **Status:** A DEFINIR (needs AWS account access).
- **Activation:** AWS credentials/role for the account; region.
- **Operations:** `get_logs(query, window)` · `get_alarms()`.
- **Use:** incident exploratory investigation → locate error/stack → map to repos.
- **Degradation (D3):** no access → human pastes logs; Alfred continues the analysis.
- **Note:** AWS-specific stays here (skill/connector), NOT in the core (A.3).
