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
- Usage/cost records are append-only observability events.
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
4. ccusage JSON for supported local CLIs.
5. Host-native interactive cost command manually recorded by the human.
6. Manual allocation approved by the human/FinOps owner.

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
- output: `usage_attributed` JSONL events using `connectors/usage-cost.md`.

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

If only aggregate ACU or cost is available, attribute by approved allocation rule
(for example by session id, time window, user, service user, or workspace) and
mark `acu_confidence` or `cost_confidence` as `allocated`.

## ccusage Secondary Design
Use `ccusage` only when the host is supported and local logs are available.

Requirements:
- pin or approve the `ccusage` version through the corporate package path;
- preserve local CLI logs long enough to import them;
- in containers, mount the CLI usage/log directory to a durable volume or export
  ccusage JSON during teardown;
- import JSON into Alfred instead of treating the terminal report as evidence.

Active helper:
- `scripts/python/metrics/import-ccusage.py`;
- input: `ccusage session --json` output or a saved JSON file;
- output: normalized `usage_attributed` JSONL events and optional
  `001-state.md` cost fields.

Claude Code automatic path:

```bash
python scripts/python/metrics/import-ccusage.py -StatePath <hub-demand>/001-state.md -Host claude-code
```

Set `usage session id:` in `001-state.md` when the host exposes it. If it is
missing, the helper uses the latest `claude` session and records
`selection_method: latest_agent_session` in the event so the attribution remains
auditable instead of silent.

For Claude Code in AWS containers, ccusage is useful only if the usage logs
survive the container. Without a durable volume, it is not a reliable source.

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
3. Render the toolbar from `state`; the renderer reads `cost usd` and can show
   the linear `Previsao`/`est. total` when progress is between 0 and 100.
4. If the value is not provided, keep `custo: nao coletado`; never invent a
   dollar amount.

## Pilot Checklist
Run one corporate pilot before implementing automatic policy suggestions:

1. Pick one Standard or SAFE brownfield demand, preferably multi-repo.
2. Record `ALFRED_RUN_ID`, repo, branch, start commit, and host at start.
3. Run the demand normally with Alfred token-economy policies enabled.
4. Capture the Devin session id (`devin-...`) and collect Session Insights plus
   session daily consumption after the run.
5. Normalize usage into `usage_attributed` events.
6. Close Operation with ACU, optional tokens, and optional USD cost in metrics.
7. Compare:
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
