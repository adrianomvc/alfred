# VCS Git Dry-Run Adapter Example

This example follows `connectors/adapter-template.md` without enabling real host mutation.

## identity
- connector type: vcs
- adapter name: git-local-dry-run
- host/product: local git CLI
- host version: not pinned
- owner: framework example
- status: dry-run

## activation
- configured by: local workspace
- credential location: not required for dry-run
- secret owner: not applicable
- environment: local CLI
- allowed scopes: current repository only
- disabled by: missing git executable or non-git workspace

## operations
| Operation | Mode | Mutates external state | Requires approval | Dry-run support | Audit event |
|---|---|---|---|---|---|
| validate_branch_name | read | no | no | native | `vcs_validate_branch_name` |
| inspect_status | read | no | no | native | `vcs_inspect_status` |
| plan_commit | dry-run | no | no | native | `vcs_plan_commit` |
| plan_pr | dry-run | no | yes before active | native | `vcs_plan_pr` |

## inputs
| Input | Required | Source | Secret | Validation |
|---|---|---|---|---|
| demand id | yes | `001-state.md` | no | non-empty |
| branch | yes | `001-state.md` | no | starts with `alfred/` or configured branch pattern |
| base branch | yes | execution plan or human input | no | non-empty |
| changed files | yes | git status | no | scoped to demand |

## outputs
| Output | Destination | Format | Retention | Notes |
|---|---|---|---|---|
| planned branch | audit/JSONL | text/json | demand lifetime | no checkout performed |
| planned commit message | audit/JSONL | text/json | demand lifetime | no commit performed |
| planned PR handoff | `05-operation/007-audit.md` | markdown | demand lifetime | human opens PR |

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
Every dry-run operation records:
- `event_type`: planned VCS operation;
- `tool`: git-local-dry-run;
- `action`: planned operation;
- `status`: completed or skipped;
- `artifacts_used`: state, execution plan, audit output;
- `error`: populated on validation failure;
- `metadata.connector`: `vcs`.

## degradation
If git is unavailable, Alfred writes a VCS handoff entry in `05-operation/007-audit.md` and asks the human to provide branch/status/PR information manually.

The handoff must include demand id, branch, base branch, files expected to change, and where the human should record the result.

## safety checks
- no secret is printed to markdown, JSONL, console, or logs;
- write/send operations have explicit destination allowlist;
- destructive or irreversible operations require human approval;
- dry-run is available for mutating operations where the host supports it;
- failures are recorded before stopping.

## fixture
- minimal fixture path: `examples/connectors/git-pr-handoff.md`
- validation command: `python scripts/validators/validate-connectors.py`
- expected result: connector and adapter validation completes
