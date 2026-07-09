# Tracker Simulator Adapter Example

A **test double** for the `tracker` contract (`connectors/tracker.md`). It
returns deterministic canned data instead of calling a real tracker, so a whole
demand can be walked end-to-end in a sandbox without credentials or a host.
It never mutates external state.

## identity
- connector type: tracker
- adapter name: tracker-sim
- host/product: none (in-repo simulator)
- host version: not applicable
- owner: framework example
- status: dry-run

## activation
- configured by: sandbox/example runs only
- credential location: not required
- secret owner: not applicable
- environment: local, offline
- allowed scopes: read canned fixture; plan issues as handoff
- disabled by: any real/integrated run (use a concrete tracker adapter instead)

## operations
| Operation | Mode | Mutates external state | Requires approval | Dry-run support | Audit event |
|---|---|---|---|---|---|
| get_demand | read | no | no | canned fixture | `tracker_get_demand` |
| open_issue | dry-run | no | yes before active | planned only | `tracker_plan_issue` |

## simulated responses (deterministic)
- `get_demand(id)` → returns the fixture `examples/connectors/tracker-sim-demand.md` verbatim, regardless of `id`; the `id` echoes into the audit event.
- `open_issue(data)` → does not create anything; writes a planned-issue handoff block (title, body, labels) and returns a fake reference `SIM-ISSUE-0001`.

## inputs
| Input | Required | Source | Secret | Validation |
|---|---|---|---|---|
| demand id | yes | human or `001-state.md` | no | non-empty |
| issue data | for open_issue | execution plan or human | no | title non-empty |

## outputs
| Output | Destination | Format | Retention | Notes |
|---|---|---|---|---|
| canned demand | demand context | markdown | sandbox run | from fixture; never a live fetch |
| planned issue | `05-operation/007-audit.md` | markdown | sandbox run | fake reference `SIM-ISSUE-0001` |

## audit fields
- demand id:
- initiative id:
- actor:
- operation:
- target:
- result:
- external reference:
- failure reason:

## observability event
Every simulated operation records:
- `event_type`: simulated tracker operation;
- `tool`: tracker-sim;
- `action`: `get_demand` or `open_issue`;
- `status`: completed or skipped;
- `artifacts_used`: fixture, state, audit output;
- `error`: populated on validation failure;
- `metadata.connector`: `tracker`.

## degradation
This is already the degraded path: with no real tracker, Alfred reads the fixture
and records planned issues as handoffs in `05-operation/007-audit.md` for a human
to act on. Swapping in a real tracker adapter is a connector change, not a rule change.

## safety checks
- no secret is printed to markdown, JSONL, console, or logs;
- no external state is mutated (read-only + planned handoffs);
- responses are deterministic and clearly labeled as simulated;
- a real/integrated run must not use this adapter;
- failures are recorded before stopping.

## fixture
- minimal fixture path: `examples/connectors/tracker-sim-demand.md`
- validation command: `python scripts/python/validators/validate-connectors.py`
- expected result: connector and adapter validation completes
