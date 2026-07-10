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

The installer can best-effort install `ccusage` from the configured npm registry
(`ALFRED_NPM_REGISTRY` / `-NpmRegistry`), with package override
`ALFRED_CCUSAGE_PACKAGE` / `-CcusagePackage`.

When `ccusage` is installed and local logs are durable, Alfred can import the
current host session with `scripts/python/metrics/import-ccusage.py`. The helper
maps `ccusage session --json` into a `usage_attributed` event, updates
`001-state.md` with `cost source: ccusage`, and keeps `cost confidence:
estimated` unless an approved billing source confirms the USD value.

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
- `host_cost_command`: host-native cost summary such as Claude Code `/cost`,
  recorded by the human or by a supported host export. It is valid only as a
  session/window total, with source and timestamp.
- `manual_allocation`: human/FinOps-approved allocation from aggregate cost.

## degradation
When host usage cannot be read:
- keep original events append-only;
- do not estimate cost unless the human provides an approved rate table;
- record the missing source in metrics gaps or validation evidence.

For Claude Code/Codex-like local CLIs, prefer `ccusage` before asking for a
manual `/cost` value:

```bash
python scripts/python/metrics/import-ccusage.py -StatePath <hub-demand>/001-state.md -Host claude-code
```

If the state contains `usage session id`, the helper imports that exact session.
Otherwise it selects the latest session for the configured agent and records the
selection method in the event validation metadata. Humans may still provide
`/cost` when `ccusage` is unavailable or the session correlation is ambiguous.

When a host exposes cost only through an interactive command (for example
Claude Code `/cost`), Alfred may ask the human to run it at start/end or before
closing the demand, then record the exact displayed value in `001-state.md` as
`cost source: host_cost_command`, `cost usd: <value>`, and
`cost confidence: exact` if the command reports the current session total. Do
not scrape prompts or infer missing token details.

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
