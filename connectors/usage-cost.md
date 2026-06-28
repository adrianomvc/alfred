# Connector - Usage Cost

## type
`usage-cost`

## activation
Optional adapter for hosts that expose model usage, tokens, or cost by session, interaction, trace, or request.

This connector is not required for Alfred to run. If the host does not expose usage, the metrics schema keeps `tokens_input`, `tokens_output`, and `cost_usd` empty and records the gap.

## operations
- `read_usage(window, filters)` reads usage records from the host or an exported file.
- `map_usage(record)` maps one host usage record to Alfred observability fields.
- `append_usage_event(event)` appends a `usage_attributed` event to the demand JSONL log.

## input fields
- `ts`
- `session_id`
- `interaction_id`
- `trace_id`
- `initiative_id`
- `demand_id`
- `phase`
- `lane`
- `model`
- `tokens_input`
- `tokens_output`
- `cost_usd`
- `source`

## degradation
When host usage cannot be read:
- keep original events append-only;
- do not estimate cost unless the human provides an approved rate table;
- record the missing source in metrics gaps or validation evidence.

## audit fields
source, usage window, records read, records attributed, records skipped, missing identifiers, output JSONL path.
