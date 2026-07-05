---
name: platform-aws-data
description: AWS data-platform standard for Glue, DMS, S3, Catalog, Lake Formation, Step Functions, EventBridge, CloudWatch, and IAM; complements language skills.
---

# Skill - AWS Data Platform Standard

## name
`platform-aws-data`

## purpose
AWS data-platform engineering standard for Glue, DMS, S3, Glue Catalog, Lake Formation, Step Functions, EventBridge, CloudWatch, and IAM boundaries. It complements language skills such as Python, SQL, and Terraform.

## trigger
Load when the active unit changes AWS data migration, ingestion, orchestration, catalog, permission, storage, observability, or reconciliation components.

## inputs
- active demand `state`
- risk artifact
- technical `spec`
- execution plan when present
- app reverse-engineering and current AWS architecture
- changed Python, SQL, Terraform, or workflow files
- base `skills/coding-standard.md`
- active language skills such as `lang-python`, `lang-sql`, or `lang-terraform`

## expected output
- AWS data-platform implementation guidance
- integration and validation plan
- review findings for cloud/data operational risk

## link
`skills/platform-aws-data.md`

## sections to load
- `rules`
- `validation`
- `review checklist`

## rules
- Keep source, landing, curated, catalog, orchestration, and permission concerns explicit.
- Treat IAM, Lake Formation, bucket policy, KMS, and network access as first-class design artifacts.
- Make data classification visible for sensitive fields such as CPF, account identifiers, customer identifiers, and operational keys.
- Prefer idempotent ingestion and transformation steps; document replay behavior and duplicate handling.
- Make partition strategy, file format, compression, schema evolution, and small-file handling explicit for S3/Parquet flows.
- For DMS or CDC flows, document full-load behavior, incremental window, delete/update handling, latency target, and rollback/coexistence path.
- For Step Functions or orchestration, document retry policy, timeout, failure path, and operator recovery action.
- For Glue Catalog and Lake Formation, document database/table ownership, grant scope, cross-account assumptions, and consumer visibility.
- For CloudWatch or observability, define metrics, logs, alarms, and correlation identifiers before closing Validate.

## validation
- Validate infrastructure syntax and plans per `lang-terraform` when Terraform is touched.
- Validate Glue or transformation logic per `lang-python` and `lang-sql` when code/query artifacts are touched.
- Validate source-to-target reconciliation using counts, hashes, key uniqueness, and business-critical measures when data access exists.
- Validate orchestration failure behavior with dry-run, local simulation, or documented skipped evidence when AWS access is unavailable.
- Validate IAM/Lake Formation permissions with least-privilege review and, when possible, a real access check.
- If AWS credentials or environment parameters are missing, record each skipped check, missing input, and exact command or console/API action expected.

## review checklist
- source, landing, curated, catalog, and orchestration responsibilities are separated;
- sensitive data handling is explicit and evidence avoids raw sensitive values;
- IAM/Lake Formation permissions are least-privilege and traceable;
- DMS/CDC assumptions are documented, including deletes, updates, latency, and coexistence;
- S3 layout, partitions, Parquet format, compression, and schema evolution are intentional;
- Step Functions retries, timeouts, and failure paths are operationally clear;
- observability covers job status, lag, failures, validation results, and cost-relevant signals;
- validation evidence distinguishes local checks from real AWS checks.
