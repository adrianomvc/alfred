---
name: lang-sql
description: SQL engineering standard; overrides coding-standard where more specific. Load for SQL files, DDL, validation queries, reconciliation, or embedded SQL.
trigger: Load when the active unit changes SQL files, migration queries, DDL, data validation queries, warehouse views, stored procedures, reconciliation scripts, or embedded SQL in code.
sections_to_load:
  - rules
  - validation
  - review checklist
---

# Skill - SQL Standard

## purpose
SQL-specific engineering standard. It overrides `skills/coding-standard.md` only where it is more specific.

## inputs
- active demand `state`
- app `reverse-eng`
- technical `spec`
- existing SQL files, DDL, views, procedures, and data contracts
- source/target schema documentation when available
- base `skills/coding-standard.md`

## expected output
- SQL implementation plan
- data validation and reconciliation plan
- SQL review findings

## rules
- Keep SQL explicit: name selected columns instead of relying on `select *` in durable artifacts.
- Separate extraction, transformation, and validation queries when the lifecycle needs evidence.
- Make join keys, filters, partitions, and incremental watermarks visible in the artifact.
- Preserve source-system semantics when migrating data types, nullability, timezone handling, precision, and scale.
- Treat CPF, account numbers, customer identifiers, and operational keys as sensitive unless a policy says otherwise.
- Avoid logging or exporting raw sensitive values in validation evidence; prefer counts, hashes, masked samples, and aggregates.
- Record assumptions about late-arriving data, duplicate keys, deletes, and update strategy.
- Keep environment-specific schema/database names configurable when queries run in more than one environment.

## validation
- Validate row counts, key uniqueness, nullability expectations, and reconciliation totals when data is available.
- Compare source and target using stable business keys or approved hashes.
- For incremental flows, validate the watermark window and at least one replay/idempotency scenario.
- For schema migration, validate type mapping and partition/catalog visibility.
- If source or target access is unavailable, record the skipped query, missing access, and expected validation command.

## review checklist
- query intent is clear and tied to a requirement or validation goal;
- selected columns, filters, joins, and watermarks are explicit;
- sensitive fields are masked, hashed, or excluded from evidence;
- source-to-target type mapping is documented where relevant;
- reconciliation covers count and business-critical measures;
- failure/empty-result behavior is understood;
- skipped validations are recorded with missing inputs and next action.
