# Connector - Usage Cost

## type
`usage-cost`

## activation
Optional adapter for hosts that expose model usage, tokens, ACUs, credits, or
cost by session, interaction, trace, or request.

This connector is not required for Alfred to run. If the host does not expose
usage, the metrics schema keeps `tokens_input`, `tokens_output`, `total_acus`,
and `cost_usd` empty and records the gap.

Primary corporate path: Devin API consumption + Session Insights, because most
usage may run through Devin and Devin meters work in ACUs. Secondary path: local
CLI importers such as `ccusage` when the CLI is supported and logs are durable. See
`docs/usage-cost-adoption.md`.

## operations
- `read_usage(window, filters)` reads usage records from the host or an exported file.
- `map_usage(record)` maps one host usage record to Alfred observability fields.
- `append_usage_event(event)` appends a `usage_attributed` event to the demand JSONL log.

## input fields
- `ts`
- `started_at`
- `ended_at`
- `alfred_run_id`
- `session_id`
- `interaction_id`
- `trace_id`
- `initiative_id`
- `demand_id`
- `host`
- `workspace_id`
- `repo`
- `branch`
- `commit_start`
- `commit_end`
- `phase`
- `lane`
- `model`
- `tokens_input`
- `tokens_output`
- `tokens_cache_creation`
- `tokens_cache_read`
- `total_acus`
- `acus_by_product`
- `acu_confidence`
- `cost_usd`
- `cost_confidence`
- `source`
- `source_record_id`

## source kinds
- `devin_api`: preferred for DEVIN CLI/Devin-hosted executions, using Session
  Insights and Consumption endpoints.
- `devin_export`: saved Devin API/admin export file.
- `enterprise_billing`: approved billing export or admin report.
- `ccusage`: local CLI usage parsed from a supported tool's durable logs.
- `manual_allocation`: human/FinOps-approved allocation from aggregate cost.

## degradation
When host usage cannot be read:
- keep original events append-only;
- do not estimate cost unless the human provides an approved rate table;
- record the missing source in metrics gaps or validation evidence.

## audit fields
source, source kind, usage window, records read, records attributed, records
skipped, missing identifiers, confidence, output JSONL path.

## confidence
Use explicit confidence labels:
- `exact`: source provides exact tokens, ACUs, credits, or cost for the
  correlated session.
- `estimated`: source provides tokens/ACUs and Alfred applies an approved rate
  table.
- `allocated`: source provides aggregate usage/cost and an approved allocation
  rule.
- `unavailable`: source did not provide the field.
