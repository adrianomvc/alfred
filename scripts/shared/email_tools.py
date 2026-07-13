TOOLS = [
    {
        "name": "send_email",
        "description": ("Send an Alfred strategic notification e-mail (demand closed, critical "
                        "checkpoint, escalation, incident). Only to allowlisted destinations; "
                        "subject is prefixed [Alfred-Framework]; every attempt is audited. "
                        "In dry-run mode the message is written to an outbox instead of sent."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "short subject (prefix added automatically)"},
                "body": {"type": "string", "description": "short summary body; attach files instead of pasting them"},
                "to": {"type": "string", "description": "destination; defaults to ALFRED_EMAIL_DEFAULT_TO"},
                "trigger": {"type": "string", "description": "which configured trigger fired (e.g. demand_completed)"},
                "attachments": {"type": "array", "items": {"type": "string"},
                                 "description": "file paths (metrics.md, audit.md, summary.md)"},
            },
            "required": ["subject", "body"],
        },
    },
    {
        "name": "send_demand_report",
        "description": ("Send the demand report e-mail: reads 001-state.md for context and attaches "
                        "the demand's metrics, audit, summary, and observability JSONL automatically. "
                        "Same guardrails as send_email (allowlist, prefix, audit, dry-run by default)."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "demand_path": {"type": "string",
                                 "description": "HUB demand folder (contains 001-state.md)"},
                "to": {"type": "string", "description": "destination; defaults to the registered one"},
                "trigger": {"type": "string", "description": "default: demand_report"},
            },
            "required": ["demand_path"],
        },
    },
    {
        "name": "send_telemetry",
        "description": ("Batch every local observability JSONL under root_path and e-mail it to the "
                        "org telemetry destination (telemetry_to) — provisional transport until the "
                        "telemetry API exists. Each batch line carries {sender, collected_at, source, "
                        "event} so logs from many people can be aggregated into org metrics. "
                        "Same guardrails: allowlist, audit, dry-run by default."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "root_path": {"type": "string",
                               "description": "root to scan for *observability-log.jsonl (HUB/app root or a demand folder); default: current dir"},
                "trigger": {"type": "string", "description": "default: telemetry_batch"},
            },
        },
    },
    {
        "name": "email_status",
        "description": "Report the adapter state: mode (dry-run/active/disabled), destinations (default/telemetry), allowlist, SMTP readiness, outbox/audit paths, and which config file is in use.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]
