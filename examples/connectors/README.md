# Connector Examples

These examples show how connector contracts can be used without making the framework depend on a specific host or vendor.

## Available
- `git-pr-handoff.md` - VCS/PR handoff shape.
- `notification-handoff.md` - notification/email degradation shape.
- `telemetry-batch.md` - local observability batch shape before sending to a future telemetry API.
- `vcs-git-dry-run-adapter.md` - example adapter shape for VCS in dry-run mode.
- `usage-export.jsonl` - example host usage export.
- `usage-attribution-events.jsonl` - example normalized `usage_attributed` event.

## Sandbox simulators (run a demand end-to-end without a host)
Test doubles that satisfy a connector contract with deterministic, clearly
labeled fake data, so the integrated demand flow can be rehearsed offline —
before any real host, credential, or recipient exists. All are `status: dry-run`
and never mutate external state.

| Connector | Simulator | Returns / does |
|---|---|---|
| vcs | `vcs-git-dry-run-adapter.md` | validates branch, plans commit/PR (no push) |
| tracker | `tracker-sim-adapter.md` | `get_demand` returns `tracker-sim-demand.md`; `open_issue` plans a handoff |
| notification | `notification-sim-adapter.md` | `send` renders the email to a sandbox outbox; never transmits |

Walkthrough: start from `tracker-sim` `get_demand`, run the five phases against an
example demand (see `examples/sq9-pilot/`), use `vcs-git-dry-run` for branch/PR
planning, and `notification-sim` at strategic-notification points. Swapping any
simulator for a real adapter is a connector change, not a rule change (Liskov).

## Rule
Examples are illustrative. Real adapters live outside the core framework or behind connector contracts.
