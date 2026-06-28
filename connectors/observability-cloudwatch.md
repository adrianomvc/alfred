# Connector - Observability Example

## type
`observability`

## activation
Optional adapter for log/alarm systems. This file is an example contract, not a core dependency.

## operations
- `get_logs(query, window)` returns relevant log entries.
- `get_alarms()` returns active/recent alarms.

## degradation
If unavailable, Alfred asks the human for logs/alarms and records the evidence source.

## audit fields
query, time window, source, evidence link or pasted excerpt reference.

