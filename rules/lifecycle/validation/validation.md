# Lifecycle - Validate ("Does it work?")

Prove the change satisfies the spec and avoids relevant regressions. Owner agent: **Reviewer**. Validation depth comes from the active lane and the actual risk.

## Steps
1. Load `spec`, acceptance criteria, execution plan, PR/change, and active lane.
2. Select the test strategy by need: unit, regression, integration, contract, e2e, performance, security.
3. Run or request the relevant checks; record commands, result, and gaps.
4. Review implementation against `spec`, SOLID/coding-standard, and acceptance criteria.
5. Prepare evidence; satisfy **DoD Validate**; request final human acceptance when required.
6. Treat merge to the protected branch as human acceptance; the AI never merges protected branches.

Use `../../../templates/hub/validation-evidence.md` for Standard/SAFE evidence. FAST may inline the same fields in the PR or summary when the change is small.

## Outputs
validation result, test evidence, review findings, residual risks, updated `state` and `audit`.

## Human roles
QA/PM for acceptance; Tech Lead for technical risk; Sponsor only when SAFE requires it.

## Depth by mode
FAST = relevant local checks and self-review. Standard = acceptance + regression evidence. SAFE = formal evidence plus integration/contract/e2e/perf/security as applicable.
