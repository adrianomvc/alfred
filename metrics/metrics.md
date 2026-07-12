# Metrics Contract

Metrics measure Alfred usage and delivery quality. They inform humans; they do not change policy automatically.

## Demand metrics
- demand id, initiative id, stream/type, lane.
- phase start/end, elapsed time, pauses, blockers.
- interactions, model used, token/cost estimate when available.
- units planned/completed, review cycles, test result, defects.
- acceptance result, merge/release link, follow-ups.

## Source artifact
`05-operation/011-observability-log.jsonl` is the preferred HUB event source for metrics. If it is missing, metrics may be reconstructed from `05-operation/007-audit.md`, but that is a fallback: audit is for responsibility, observability log is for measurement.

In App-only sessions, `.alfred-docs-app/<id-iniciativa>/<id-demanda>/05-operation/008-observability-log.jsonl` is the local event source. It is synchronized into the HUB `05-operation/011-observability-log.jsonl` when the HUB becomes writable.

## Event format
Append-only JSON Lines. Each line is one valid JSON object and should use `schema_version: "alfred.observability.v1"`.

Required fields:
- `schema_version`
- `alfred`
- `ts`
- `event_id`
- `trace_id`
- `session_id`
- `interaction_id`
- `sequence`
- `initiative_id`
- `demand_id`
- `event_type`
- `phase`
- `lane`
- `actor_type`
- `actor_id`
- `action`
- `status`
- `step`
- `artifacts_used`

Metric fields:
- `duration_ms`
- `tokens_input`
- `tokens_output`
- `tokens_cache_creation`
- `tokens_cache_read`
- `cost_usd`
- `retry_count`

Usage may also arrive later as append-only `usage_attributed` events produced by
a `usage-cost` connector when the source has interaction/request granularity.
Interaction cost may be appended later as separate `usage_cost_attributed`
events when exact usage is combined with an approved `usage-rate-card`
connector. These events should reference the original session, interaction,
trace, or parent event when the host exposes those identifiers. Session totals
such as `ccusage session --json` belong in `001-state.md` for toolbar display;
they are not interaction events and must not be appended to the observability
JSONL log or allocated into interaction cost.

Scopes are explicit:
- `event_scope: request` = one real model request/call, with `request_id`.
- `event_scope: interaction` = one human prompt/span and all resulting requests
  and tools.
- `event_scope: step` = Alfred lifecycle step.
- session-level totals stay in `001-state.md`.

`--granularity turn` in legacy helpers is an alias for request-level attribution,
not proof of one human interaction.

Detail fields:
- `input`
- `derivation`
- `output`
- `model`
- `tool`
- `parent_event_id`
- `artifacts`
- `files_changed`
- `validation`
- `risk`
- `blocker`
- `error`
- `state_transition`
- `actions`
- `questions_open`
- `assumptions`
- `metric_impact`
- `next`
- `metadata`

`step` identifies what Alfred is doing now: `id`, `name`, `sequence`, and `goal`.

`alfred` records the framework version used to produce the event: `version`, `framework_ref`, `framework_commit`, and `schema_version`. This makes it possible to analyze old logs after Alfred evolves.

`artifacts_used` records which artifacts were read, created, updated, or produced by the step. The canonical shape is a list of objects:

```json
{"artifacts_used":[{"path":"rules/common/token-budget-policy.md","artifact_type":"framework_policy","operation":"read","selection_reason":"token_heavy_step","observed_by":"claude_hook","size_bytes":4280,"lines_read":60,"content_hash":"sha256:...","first_seen_at":"2026-07-12T15:00:00Z","last_seen_at":"2026-07-12T15:00:03Z","read_count":1}]}
```

Readers must accept the legacy object form (`read`/`created`/`updated`/`output`)
and normalize it into this list. Sensitive paths are redacted by category/hash;
contents are never recorded by default.

`actions` records the concrete step-by-step operations performed by Alfred: filesystem changes, command checks, validations, handoffs, or human checkpoints.

`input` records what entered the step: human message, command result, artifact content, connector result, or previous event. For human input, store both a short `raw_excerpt` and a normalized `intent` when useful. Avoid storing secrets or large transcripts.

`derivation` records the audit-friendly path from input to output: rules applied, artifacts consulted, assumptions, constraints, decision references, and validation checks. It must explain the result without exposing hidden chain-of-thought.

`output` records what Alfred produced: artifact paths, status changes, decisions, questions, or next-step recommendations.

## Append discipline
Do not batch observability in memory. Alfred appends events as soon as they happen:
- append `interaction_received` immediately after a human message that changes the demand;
- append `step_started` before a non-trivial action;
- append `artifact_written` after each artifact create/update;
- append `step_completed` after the step output is persisted;
- append `error` before stopping on a failure.

If a later schema adds fields, do not rewrite old JSONL lines. Append a new event that records the schema/version change or backfill summary.

If interaction/request token usage arrives after the original interaction,
append a `usage_attributed` event instead of editing the original line. If
interaction cost is computed later from an approved rate card, append a
`usage_cost_attributed` event that references the usage event. If only a session
total cost arrives, refresh the state fields used by the toolbar instead of
appending a JSONL event.

Unknown is not zero. Use `null` when duration, retry count, usage, cost, outcome,
or file-change status was not observed. Use `0` only when the runtime/export
observed a real zero. Use `[]` only when an empty list was actually observed.

## Event hygiene (enables attribution)
Per-event `tokens_input`, `tokens_output`, and `cost_usd` stay `null` on hosts
that do not expose per-interaction usage/cost (for example Claude Code). Exact
tokens may be recovered later from a host transcript as `usage_attributed`;
session total cost from ccusage remains in state for toolbar display. That is
expected, not a gap. Even so, these fields make later fine-grained attribution
possible only if the event metadata is real:
- **Real `ts`.** Stamp a real ISO-8601 timestamp from the system clock at write
  time. Never a placeholder, rounded, or duplicated value — the `ts` sequence is
  the window boundary any later usage attribution relies on.
- **Real `session_id`.** Use the host's session id when the host exposes one, so
  `usage_attributed` events correlate to the same session. Keep `trace_id` /
  `ALFRED_RUN_ID` stable across the whole demand, and record the git commit at
  Execution step boundaries so a window maps to a diff.
- **Refresh session totals at checkpoints.** Run the session-total source
  (`import-ccusage.py`, Devin session/consumption summary) at each checkpoint so
  the toolbar stays current. Do not append those session totals to JSONL. Append
  JSONL only from interaction/request-granular sources. Append interaction cost
  only from a source that already has interaction cost or from exact usage plus
  an approved rate card.
- **Cache reuse ratio.** Rollups calculate
  `cache_reuse_ratio = tokens_cache_read / (tokens_input + tokens_cache_creation + tokens_cache_read)`.
  If the denominator is zero or not observed, the ratio is `n/a`.
- **No double counting.** Rollups sum tokens only from `usage_attributed` events
  and cost only from `usage_cost_attributed` events. Tokens copied into cost
  events are evidence, not additional usage.

## Rollup
Roll demand -> initiative -> org. Insights suggest policy changes; humans ratify them in commits.
