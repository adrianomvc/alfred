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
maps `ccusage session --json` into session-level state fields for toolbar
display (`cost source: ccusage`, `cost usd`, `cost granularity: session`) and
keeps `cost confidence: estimated` unless an approved billing source confirms
the USD value. A ccusage session total is not an interaction-level
observability event and must not be appended to the demand JSONL log as
`usage_attributed`.

## operations
- `read_usage(window, filters)` reads usage records from the host or an exported file.
- `map_usage(record)` maps one host usage record to Alfred observability fields.
- `append_usage_event(event)` appends a `usage_attributed` event to the demand JSONL log.
- `append_cost_event(event)` appends a separate `usage_cost_attributed` event
  only when an interaction/request source already has cost or exact usage is
  priced through `connectors/usage-rate-card.md`.

## input fields
- `ts`
- `started_at`
- `ended_at`
- `alfred_run_id`
- `session_id`
- `interaction_id`
- `request_id`
- `event_scope`
- `interaction_confidence`
- `correlation_method`
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
- `token_confidence`
- `source`
- `source_record_id`

## source kinds
- `devin_api`: preferred for DEVIN CLI/Devin-hosted executions, using Session
  Insights and Consumption endpoints.
- `devin_export`: saved Devin API/admin export file.
- `enterprise_billing`: approved billing export or admin report.
- `ccusage`: local CLI session total parsed from a supported tool's durable logs;
  valid for toolbar/state session display, not for interaction JSONL events.
- `host_transcript`: exact per-request token usage parsed from a host transcript
  (for example the Claude Code session JSONL), attributed to Alfred event windows
  or turns. Tokens are exact; cost is `null` unless an approved interaction cost
  source or rate card is applied. See the layered attribution below.
- `host_raw_log`: sanitized technical JSONL written by a runtime hook outside
  the demand; it may include request/tool/artifact metadata, never prompt/file
  contents by default.
- `usage_rate_card`: approved per-model/per-unit table applied to exact
  interaction usage; confidence `rated` or `estimated` depending on approval.
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
selection method in the state/session snapshot metadata. Humans may still provide
`/cost` when `ccusage` is unavailable or the session correlation is ambiguous.

Run the import at each checkpoint, not only at demand close, so the session cost
stays current in the toolbar. Each run refreshes the `001-state.md` cost fields;
it does not append to `05-operation/011-observability-log.jsonl`. On Windows the
helper resolves the `ccusage` npm shim via `PATHEXT`; if it is unreachable, dump
`ccusage session --json` to a file and pass `-InputPath`.

### Layered transcript attribution (finer than the session total)
When the host keeps a durable transcript with per-request usage (Claude Code),
`scripts/python/metrics/attribute-usage-transcript.py` recovers finer
granularity from the `host_transcript` source. Usage is de-duplicated by
`requestId` (a request spans several transcript lines that repeat the same
usage), so tokens are exact. Cost is not in the transcript: it stays `null`
unless an approved interaction-level cost source or `usage-rate-card` is
provided. Do not allocate a ccusage session total into interaction events.

- `--granularity request`: one event per host model request. Legacy
  `--granularity turn` remains an alias for compatibility.
- `--granularity window`: sum requests into windows bounded by consecutive Alfred
  event timestamps (needs real, distinct event `ts`). One-shot, run at close.
- `--emit-interactions`: append `interaction_completed` aggregates from
  request-level usage when `promptId` or a user boundary supports correlation.
- `--rate-card-path`: optional approved `usage-rate-card` JSON. When supplied,
  transcript attribution can compute interaction cost from exact tokens. Without
  it, cost stays `null`.

Interaction correlation priority:
1. host-provided `promptId` or equivalent span id (`interaction_confidence:
   exact`);
2. transcript user boundary (`derived`);
3. request-only, with `interaction_id: null` and the limitation recorded.

The Claude Code Stop hook (`core/hooks/usage-attribution.md`) runs the turn mode
automatically and out-of-band, since the host — not the in-band agent — owns the
usage object. Hooks do not receive usage inline; they receive `transcript_path`.

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
- `rated`: exact interaction usage priced by an approved rate card.
- `estimated`: source provides tokens/ACUs and Alfred applies an approved but
  approximate/public rate table.
- `allocated`: source provides aggregate usage/cost and an approved allocation
  rule.
- `unavailable`: source did not provide the field.
