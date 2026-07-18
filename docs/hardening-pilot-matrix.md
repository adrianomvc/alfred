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
