# Validate sub-activities

Optional **test strategies inside Validate** (never new phases). They run **by
trigger** and their depth scales with the active lane and the actual risk.
Loaded just in time — only the strategies the change needs. Stack-agnostic;
reference the active language/platform skill and connectors by role.

## The ladder (run only the rungs the demand triggers)
| Sub-activity | Trigger | Gives |
|---|---|---|
| `unit-testing` | logic changed | per-unit correctness |
| `regression-testing` | existing behavior touched | no regression in the affected area |
| `integration-testing` | crosses a component/service boundary | parts interact correctly |
| `contract-testing` | an external/internal API contract is involved | provider/consumer compatibility |
| `e2e-testing` | a user-facing journey is affected | the full journey works |
| `performance-testing` | an NFR perf/scale target exists | before/after baseline meets target |
| `security-testing` | sensitive data or attack surface | security checks pass |

## Order (when several fire)
Cheap and local first: `unit-testing` → `regression-testing` → `integration-testing`
→ `contract-testing` → `e2e-testing` → `performance-testing` → `security-testing`.
Each is optional; record which were run and which were skipped with justification.

## Where the output lands
Into the validation evidence (`../../../../templates/hub/validation-evidence.md`
for Standard/SAFE; inline in the PR for small FAST changes), plus residual risks
and updated `state`/`audit`.

## Depth by mode
FAST = relevant local checks (often just `unit`/`regression`). Standard =
acceptance + regression evidence. SAFE = the applicable strategies with formal
evidence, including integration/contract/e2e/perf/security as the risk requires.
