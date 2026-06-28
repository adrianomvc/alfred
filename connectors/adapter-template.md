# Connector Adapter Template

Use this template when implementing a concrete adapter for one connector type.

## identity
- connector type:
- adapter name:
- host/product:
- host version:
- owner:
- status: contract | handoff | dry-run | active | disabled

## activation
- configured by:
- credential location:
- secret owner:
- environment:
- allowed scopes:
- disabled by:

## operations
| Operation | Mode | Mutates external state | Requires approval | Dry-run support | Audit event |
|---|---|---|---|---|---|
|  | read | no | no | not applicable |  |

## inputs
| Input | Required | Source | Secret | Validation |
|---|---|---|---|---|
|  | yes |  | no |  |

## outputs
| Output | Destination | Format | Retention | Notes |
|---|---|---|---|---|
|  |  |  |  |  |

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
Every adapter operation must append or request an Alfred JSONL event with:
- `event_type`: connector operation name;
- `tool`: adapter name;
- `action`: operation performed;
- `status`: started | completed | failed | skipped;
- `artifacts_used`: read/created/updated/output artifacts;
- `error`: populated on failure;
- `metadata.connector`: connector type and host.

## degradation
Describe the exact manual handoff when the adapter is unavailable.

The degradation must preserve traceability: what Alfred needed, who must perform it, where the result must be recorded, and which audit/JSONL event marks completion.

## safety checks
- no secret is printed to markdown, JSONL, console, or logs;
- write/send operations have explicit destination allowlist;
- destructive or irreversible operations require human approval;
- dry-run is available for mutating operations where the host supports it;
- failures are recorded before stopping.

## fixture
- minimal fixture path:
- validation command:
- expected result:
