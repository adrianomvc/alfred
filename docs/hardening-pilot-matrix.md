# Alfred 2.0 Hardening Pilot Matrix

This matrix is the release evidence gate for the hardening work. Code fixtures
and unit tests do not substitute for these real runs. Never mark a row accepted
without links to the demand state, validation evidence, audit, host/environment
identity, and measured token/usage output.

| Pilot | Required scenario | Acceptance | Status |
|---|---|---|---|
| P1 | Devin Standard demand with `/usage` baseline and checkpoint | typed unit, non-negative delta, same-unit budget decision | pending external run |
| P2 | Devin cycle reset or quota-percent account | reset detected or explicit migration unit; no false ACU/USD | pending external run |
| P3 | Brownfield retrieval using memory and structural exploration | >=30% median token reduction, >=95% recall, no missed acceptance evidence | pending external run |
| P4 | SAFE demand with budget pressure | no phase, acceptance, security, rollback, or SAFE gate skipped | pending external run |
| P5 | Enterprise Devin environment rollout | tier placement, secrets UI, least privilege, context reinjection, health evidence | pending external run |

For each accepted row, record the pinned Alfred commit/tag, Devin environment
revision, repository commit, commands executed, expected versus actual signal,
fresh-reviewer result, and unresolved gaps. Redact secret values; a secret's
presence may be evidenced by its configured name only.

Release remains **in progress** until all rows are accepted, CI is required on
`main`, and a human creates the immutable stable tag.

## Organizational-routing eval
Before changing default model routing, compare on the same representative Devin
tasks: current Alfred, strong direct, strong director + eligible medium executor,
and review-only. Add a same-tier director/worker arm only to measure coordination
overhead. Stratify by simple/local versus ambiguous/multi-file work and repeat
runs because model execution is non-deterministic.

Record first-pass acceptance, acceptance/regression result, correction count,
scope drift, human interventions, duration, interactions, strong-model usage,
total usage, ACU, and USD only when an approved rate card exists. A routing
change needs better quality or lower measured cost without weaker safety; lower
strong-model tokens alone is insufficient.
