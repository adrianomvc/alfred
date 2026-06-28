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
- `cost_usd`
- `retry_count`

Usage and cost may also arrive later as append-only `usage_attributed` events produced by a `usage-cost` connector. These events should reference the original session, interaction, trace, or parent event when the host exposes those identifiers.

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

`artifacts_used` records which artifacts were read, created, updated, or produced by the step. This is the field used to answer "what did Alfred use for this step?"

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

If cost or token usage arrives after the original interaction, append a `usage_attributed` event instead of editing the original line.

## Rollup
Roll demand -> initiative -> org. Insights suggest policy changes; humans ratify them in commits.
