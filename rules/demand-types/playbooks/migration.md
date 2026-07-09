---
name: playbook-migration
description: Playbook — Migration
load: playbook
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Playbook — Migration

> Operational roteiro for Engineering / **migration** (tech, platform, provider,
> or data migration). Loaded JIT when the demand type is migration.

## Applies to
Moving a system or dataset from a source to a target while the source stays
authoritative until acceptance. Trigger: demand type = migration, or a provider
change/upgrade large enough to be treated as one.

## Mode tendency
**SAFE** (hard override): irreversibility + multi-component + data movement.
Does not drop below SAFE even for a small slice. Often splits into **units** by
component/repo.

## Per phase

### Inception
- Heavy **reverse-eng** of every affected repo (staleness-checked); map
  **source → target** and the integration points.
- List **what data moves**, expected volume, incremental window, and
  delete/update (CDC) rules. Mark anything unknown as `a confirmar` — never invent
  schemas, endpoints, or volumes.
- Identify **irreversibilities** and the sensitive-data surface (raise to the
  security skill if present).
- Artifacts: `problem`, `tech-inception`, `risk`. HITL: confirm scope + SAFE mode.

### Design
- Choose the **rollout strategy**: strangler or **parallel-run** (source and
  target live together; source stays as reference).
- Define an **explicit rollback** (default: keep the source active; do not
  decommission until acceptance).
- Spec the **reconciliation** contract: count, schema, and sample/hash between
  source and target.
- Decompose into **units** per component (ingestion, landing, processing,
  catalog/governance, orchestration). Record decisions/ADR.
- Artifacts: `spec`, `decisions`, `execution-plan`. HITL: architecture + rollback
  approval (Tech Lead).

### Execution
- Build each unit **in-place** (never `file_v2`); follow template + active
  language/platform skills.
- Keep the source untouched and authoritative. Commit per step/unit on the
  demand branch; watch escalation triggers (destructive/irreversible actions stop
  and ask).
- Park real infrastructure commands until **environment parameters** are
  confirmed (account, region, endpoints, buckets, secrets) — record blockers in
  `environment-parameters`, do not run with assumed values.

### Validate
- Run **reconciliation** source × target (count/schema/sample-hash) and
  **regression**.
- Formal evidence (SAFE). HITL: acceptance. The PR merge into the protected
  branch is the acceptance.

### Operation
- **Phased cutover**; monitor target; keep rollback active.
- Decommission the source **only after acceptance**.
- `summary` + `index`; record follow-ups/tech-debt as new demands.

## Typical units
ingestion · landing (separate from final) · processing · catalog/governance ·
orchestration · reconciliation.

## Rollback & risks
Irreversible once the source is decommissioned → that step is the gate. Until
then, parallel-run makes rollback = route back to source. Watch data loss on
incremental/CDC, idempotency, and sensitive-data exposure.

## Done when
Target reconciles with source, evidence is signed off, cutover is accepted, and
the source is decommissioned (or an explicit decision keeps it as fallback).
