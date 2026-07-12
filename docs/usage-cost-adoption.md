# Usage Cost Adoption Plan

This plan defines how Alfred moves from planned token/cost governance to real
usage attribution. `ccusage` import is active for supported local CLIs; Devin
API import remains the primary corporate target and still depends on approved
API/export access.

## Goal
Attribute AI usage to Alfred demands without making the framework depend on one
vendor, one CLI, or one billing source.

Primary path:
- **Devin API consumption + Session Insights** because most corporate usage is
  expected to run through Devin and Devin meters work in Agent Compute Units
  (ACUs).

Secondary path:
- **ccusage** for local CLIs it supports, such as Claude Code, Codex, Copilot
  CLI, Gemini CLI, or similar tools with readable local usage logs.

Fallback:
- manual allocation from approved billing reports or invoices, explicitly
  marked as manual.
- host-native interactive cost command (for example Claude Code `/cost`) when
  the human records the displayed total into the demand state.

## Principles
- Usage import is optional; Alfred runs without it.
- Interaction/request usage records are append-only observability events.
  Session totals are state fields for toolbar display unless the source provides
  interaction-level records; they must not drive demand forecasts.
- Interaction cost records are separate append-only `usage_cost_attributed`
  events when exact usage is priced by an approved rate card.
- Do not estimate USD cost unless the human provides an approved rate table or
  the source export already includes cost.
- Devin ACU counts may be exact while USD cost may be estimated or allocated;
  record that distinction. Token counts remain optional for hosts that expose
  them.
- Every attributed record needs correlation evidence: demand, repo, time window,
  host, and source.
- Never send secrets, prompts, source code, or billing exports to an unapproved
  external service for attribution.

## Correlation Model
At demand start or resume, Alfred should create or reuse:

| Field | Purpose |
|---|---|
| `alfred_run_id` | unique id for one Alfred execution window |
| `initiative_id` | HUB initiative id |
| `demand_id` | demand id |
| `host` | `devin`, `claude-code`, `codex`, `copilot`, etc. |
| `workspace_id` | host workspace/project/container id when available |
| `repo` | repository name or local path |
| `branch` | current branch |
| `commit_start` | commit before execution |
| `commit_end` | commit after execution or validation |
| `started_at` / `ended_at` | usage attribution window |

`ALFRED_RUN_ID` is the preferred environment variable when the host allows it.
If the host cannot receive environment variables, record the run id in
`001-state.md` and in the first observability event for the session.

## Source Priority
Use the most authoritative source available:

1. Devin Consumption API by session, plus Session Insights for correlation.
2. Devin organization/user/service-user consumption API.
3. Enterprise billing export that includes user, workspace, repo, or time
   windows.
4. ccusage JSON for supported local CLIs (session total only).
5. Approved usage rate card applied to exact interaction usage.
6. Host-native interactive cost command manually recorded by the human.
7. Manual allocation approved by the human/FinOps owner.

If sources conflict, keep both records with their source and mark the conflict
in metrics; do not silently reconcile.

## Devin-First Design
The first active implementation should use Devin's ACU sources:

- Session Insights identifies the session, title, tags, PRs, user,
  parent/child sessions, messages, category, and `acus_consumed` when available.
- Consumption by session is the preferred authoritative ACU source:
  `/v3/organizations/{org_id}/consumption/daily/sessions/{session_id}`.
- Organization, user, and service-user consumption endpoints support rollups and
  reconciliation.
- USD cost is derived only from the enterprise contract/order form or an
  approved FinOps allocation table.

Implementation target:
- Python metric helper named `import-devin-usage`;
- input: saved Devin API JSON or approved local metadata;
- output: `usage_attributed` JSONL events only when the Devin source is
  interaction/session-window granular enough for the event being written;
  otherwise update demand state with session summary fields for toolbar display.

Minimum mapped fields:
- `source_kind = devin_api`;
- `session_id = devin-...`;
- `total_acus`;
- `acus_by_product.devin`;
- `acus_by_product.terminal`;
- `acus_by_product.review`;
- `acus_by_product.cascade`;
- `acu_confidence = exact`;
- `cost_usd = null` until a contract/rate table is approved;
- `cost_confidence = unavailable`, `estimated`, or `allocated`.

If only aggregate ACU or cost is available, keep it as session/window summary in
state or a separate approved rollup artifact. Do not append it as an interaction
JSONL event unless an approved allocation rule and target granularity are
explicitly recorded.

## ccusage Secondary Design
Use `ccusage` only when the host is supported and local logs are available.

Requirements:
- pin or approve the `ccusage` version through the corporate package path;
- preserve local CLI logs long enough to import them;
- in containers, mount the CLI usage/log directory to a durable volume or export
  ccusage JSON during teardown;
- import JSON into Alfred instead of treating the terminal report as evidence.

Active helper:
- `scripts/metrics/import-ccusage.py`;
- input: `ccusage session --json` output or a saved JSON file;
- output: `001-state.md` session cost fields for toolbar display. Optional
  debug snapshots may be written outside the observability log with
  `-WriteSnapshot`.

Claude Code automatic path:

```bash
python scripts/metrics/import-ccusage.py -StatePath <hub-demand>/001-state.md -Host claude-code
```

Set `usage session id:` in `001-state.md` when the host exposes it. If it is
missing, the helper uses the latest `claude` session and records
`selection_method: latest_agent_session` in the state/session snapshot metadata
so the attribution remains auditable instead of silent.

For Claude Code in AWS containers, ccusage is useful only if the usage logs
survive the container. Without a durable volume, it is not a reliable source.

## Claude Code Transcript and Hook Path
Claude Code durable transcripts can provide request-level tokens and cache
fields without asking the agent to estimate them:

- request tokens: supported when assistant transcript records include
  `requestId`, `message.model`, and `message.usage`;
- interaction id: exact when the host exposes `promptId`, derived from user
  boundaries when safe, otherwise `interaction_confidence: unavailable`;
- cost: not in the transcript, so JSONL cost requires an approved rate card or
  another granular host/billing export;
- artifacts/tools: captured only when the transcript or hook event exposes
  enough metadata; raw content is not recorded.

The optional hook (`scripts/metrics/claude-code-usage-hook.py`) can write
sanitized raw telemetry outside the demand and normalized Alfred events inside
the demand:

| Variable | Meaning |
|---|---|
| `AI_OBS_RAW_LOG` | external JSONL path for technical raw events |
| `AI_OBS_CURSOR_DIR` | per-transcript cursor directory |
| `AI_OBS_MODE` | `raw`, `alfred`, or `both` |
| `AI_OBS_PROVIDER` | provider label, default `claude-code` |
| `AI_OBS_PROJECT` / `AI_OBS_TEAM` / `AI_OBS_ENVIRONMENT` | optional dimensions |
| `ALFRED_OBS_LOG` | explicit demand observability JSONL |
| `ALFRED_STATE_PATH` | demand `001-state.md`; log is derived from it |
| `ALFRED_RUN_ID` | run correlation id |

The hook is non-blocking, append-only, idempotent by `requestId`, and uses an
incremental cursor. The installed path currently uses the confirmed Claude Code
`Stop` hook; `SessionEnd` is documented as a future addition until the host
configuration is confirmed. Manual close/flush remains:

```bash
python scripts/metrics/attribute-usage-transcript.py --transcript-path <transcript.jsonl> --observability-log <hub-demand>/05-operation/011-observability-log.jsonl --granularity request --emit-interactions
```

## Devin Source Boundary
Devin remains API/export first. ACU/session API continues to be the preferred
corporate source. Alfred must not infer request tokens or interaction cost from
Devin wall time, terminal output, or conversation text. If the API only exposes
session-level ACU/USD, keep it in state/rollup with confidence metadata; append
JSONL interaction events only when the Devin export itself provides suitable
granularity or an approved rate card prices exact granular usage.

## Interaction Cost from Rate Cards
For Claude Code and similar transcript-based hosts, the transcript can provide
exact request tokens but not USD cost. To populate interaction cost in JSONL,
Alfred needs an approved rate card:

```bash
python scripts/metrics/apply-usage-rate-card.py -InputPath <hub-demand>/05-operation/011-observability-log.jsonl -RateCardPath <approved-rate-card.json>
```

This appends `usage_cost_attributed` events that reference the original
`usage_attributed` event by `parent_event_id`. It does not edit old lines and
does not allocate `ccusage` session totals. Confidence is `rated` when the rate
card is approved by the human/FinOps owner, `estimated` when the table is
approved only as a public/approximate rate, and `exact` only when the source
itself provides per-interaction billed cost.

## Claude Code Manual Cost Capture
Claude Code may expose session cost through `/cost` in the interactive UI.
Alfred cannot assume that value or call it as a normal shell command. Use this
only when `ccusage` is unavailable, logs are not durable, or session correlation
is ambiguous. When a demand runs in Claude Code and no durable usage export is
configured:

1. Ask the human to run `/cost` at a natural checkpoint (resume, before Design
   approval, before close, or when the toolbar still says `nao coletado`).
2. Record the displayed value in `001-state.md`:
   - `usage-cost: host cost command (/cost)`
   - `cost source: host_cost_command`
   - `cost usd: <numeric USD value>`
   - `cost confidence: exact` when `/cost` reports the current session total.
3. Render the toolbar from `state`; the renderer reads `cost usd` as
   session-scoped unless demand-scoped cost evidence exists. It must not show a
   demand forecast from `/cost`.
4. If the value is not provided, keep `custo: nao coletado`; never invent a
   dollar amount.

## Pilot Checklist
Run one corporate pilot before implementing automatic policy suggestions:

1. Pick one Standard or SAFE brownfield demand, preferably multi-repo.
2. Record `ALFRED_RUN_ID`, repo, branch, start commit, and host at start.
3. Run the demand normally with Alfred token-economy policies enabled.
4. Capture the Devin session id (`devin-...`) and collect Session Insights plus
   session daily consumption after the run.
5. Normalize interaction/request usage into `usage_attributed` events; keep
   session totals in state for toolbar display.
6. If an approved rate card exists, append `usage_cost_attributed` events from
   the exact usage events.
7. Close Operation with ACU, optional tokens, and optional USD cost in metrics.
8. Compare:
   - actual spend vs baseline;
   - ACU consumption and product breakdown;
   - cache/token savings when a non-Devin source exposes them;
   - rework/interactions;
   - acceptance on first review;
   - time blocked waiting for human.

Acceptance for the pilot:
- at least one real Devin usage source imported;
- no invented cost;
- demand can still validate without the cost source;
- metrics clearly mark exact, estimated, allocated, or unavailable fields.

## Implementation Order
1. Extend `connectors/usage-cost.md` with the correlation and confidence fields.
2. Add example input fixtures for Devin Session Insights, Devin session
   consumption, and ccusage-like export.
3. Add import scripts for one source at a time. `import-ccusage.py` is active;
   Devin API import is next.
4. Add validation for normalized usage events.
5. Add docs for corporate setup and privacy boundaries.
6. After 5+ real demands, evaluate model-policy suggestions from metrics.

## Open Decisions
- Which Devin API scope/permission is available in the corporate environment?
- Can Devin sessions/tasks be tagged with `ALFRED_RUN_ID`?
- How do we reliably capture the Devin `session_id` from CLI/cloud sessions?
- Is ccusage approved for corporate use, or must it be mirrored through
  Artifactory?
- Where should billing exports be stored while being normalized?
- Who ratifies ACU-to-USD contract rates and allocation rules?
