# Usage Cost Adoption Plan

This plan defines how Alfred should move from planned token/cost governance to
real usage attribution. It is a design for the next implementation wave, not an
active adapter yet.

## Goal
Attribute AI usage to Alfred demands without making the framework depend on one
vendor, one CLI, or one billing source.

Primary path:
- **DEVIN CLI / Devin usage export** because most corporate usage is expected to
  run through Devin.

Secondary path:
- **ccusage** for local CLIs it supports, such as Claude Code, Codex, Copilot
  CLI, Gemini CLI, or similar tools with readable local usage logs.

Fallback:
- manual allocation from approved billing reports or invoices, explicitly
  marked as manual.

## Principles
- Usage import is optional; Alfred runs without it.
- Token/cost records are append-only observability events.
- Do not estimate USD cost unless the human provides an approved rate table or
  the source export already includes cost.
- Token counts may be exact while USD cost may be estimated; record that
  distinction.
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

1. Devin official export/API/admin report with session or task ids.
2. Enterprise billing export that includes user, workspace, repo, or time
   windows.
3. ccusage JSON for supported local CLIs.
4. Manual allocation approved by the human/FinOps owner.

If sources conflict, keep both records with their source and mark the conflict
in metrics; do not silently reconcile.

## Devin-First Design
The first active implementation should discover what Devin exposes:

- Does Devin provide API/export for usage by session, task, repo, user, or
  workspace?
- Does it expose input/output/cache tokens, credits, or only USD/billing units?
- Can a Devin task/session be tagged with `ALFRED_RUN_ID`?
- Does the CLI expose start/end/session metadata locally?
- What is the enterprise-approved way to retrieve that data?

Implementation target:
- future Python metric helper named `import-devin-usage`;
- input: export/API file or approved local metadata;
- output: `usage_attributed` JSONL events using `connectors/usage-cost.md`.

If Devin only exposes aggregate cost, attribute by approved allocation rule
(for example by task id, time window, user, or workspace) and mark
`cost_confidence = allocated`.

## ccusage Secondary Design
Use `ccusage` only when the host is supported and local logs are available.

Requirements:
- pin or approve the `ccusage` version through the corporate package path;
- preserve local CLI logs long enough to import them;
- in containers, mount the CLI usage/log directory to a durable volume or export
  ccusage JSON during teardown;
- import JSON into Alfred instead of treating the terminal report as evidence.

Implementation target:
- future Python metric helper named `import-ccusage`;
- input: `ccusage ... --json` output saved to a file;
- output: normalized `usage_attributed` JSONL events.

For Claude Code in AWS containers, ccusage is useful only if the usage logs
survive the container. Without a durable volume, it is not a reliable source.

## Pilot Checklist
Run one corporate pilot before implementing automatic policy suggestions:

1. Pick one Standard or SAFE brownfield demand, preferably multi-repo.
2. Record `ALFRED_RUN_ID`, repo, branch, start commit, and host at start.
3. Run the demand normally with Alfred token-economy policies enabled.
4. Export or collect usage from Devin after the run.
5. Normalize usage into `usage_attributed` events.
6. Close Operation with cost/tokens in metrics.
7. Compare:
   - actual spend vs baseline;
   - cache/token savings when available;
   - rework/interactions;
   - acceptance on first review;
   - time blocked waiting for human.

Acceptance for the pilot:
- at least one real usage source imported;
- no invented cost;
- demand can still validate without the cost source;
- metrics clearly mark exact, estimated, allocated, or unavailable fields.

## Implementation Order
1. Extend `connectors/usage-cost.md` with the correlation and confidence fields.
2. Add example input fixtures for Devin-like export and ccusage-like export.
3. Add import scripts for one source at a time.
4. Add validation for normalized usage events.
5. Add docs for corporate setup and privacy boundaries.
6. After 5+ real demands, evaluate model-policy suggestions from metrics.

## Open Decisions
- Which Devin usage source is available in the corporate environment?
- Can Devin sessions/tasks be tagged with `ALFRED_RUN_ID`?
- Is ccusage approved for corporate use, or must it be mirrored through
  Artifactory?
- Where should billing exports be stored while being normalized?
- Who ratifies USD rate tables and allocation rules?
