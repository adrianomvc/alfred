# Host Adapter Readiness

Use this checklist before turning a connector contract into a working host adapter.

Use `connectors/adapter-template.md` for the concrete adapter file and `docs/adapter-implementation.md` for adapter state rules.

## Required Inputs
- host name and product/version;
- environment: local, enterprise SaaS, internal platform, or CI runner;
- authentication method and secret owner;
- allowed operations;
- rate limits and audit requirements;
- target repositories, projects, queues, channels, or endpoints;
- failure handling expectation;
- rollback or disable procedure.

## Required Decisions
- which connector type is being implemented;
- whether the adapter is read-only, write-capable, or send-capable;
- where credentials live;
- whether output is written back to Alfred JSONL, markdown artifacts, or the external host;
- whether the adapter can run automatically or requires explicit human approval.

## Adapter Acceptance
- reads required input without exposing secrets;
- writes only to approved destinations;
- records every host action in audit/observability;
- degrades to markdown handoff when host is unavailable;
- declares adapter state: contract, handoff, dry-run, active, or disabled;
- has a dry-run mode when the operation can mutate external state;
- has a minimal example fixture;
- is referenced from `connectors/` without changing lifecycle rules.

## Connector-Specific Notes
- `vcs`: branch, commit, PR creation, and PR status need repository permissions.
- `tracker`: issue creation/update needs project and workflow mapping.
- `notification`: send operations need destination allowlist and approval policy.
- `telemetry`: event sending needs destination schema and retry policy.
- `usage-cost`: usage collection needs a host export/API, local usage log, or approved billing export that exposes model, tokens, cost or allocation inputs, and correlation identifiers. For DEVIN-first adoption, confirm the available Devin usage source before implementing an adapter; use `docs/usage-cost-adoption.md`.

## Degradation Rule
If any required input is missing, keep the connector as a contract or handoff example. Do not create a partial adapter that silently skips audit, approval, or error handling.
