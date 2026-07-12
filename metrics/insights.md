# Metrics Insights

Insights convert metrics into human-reviewable proposals.

## Output format
- Observation
- Evidence
- Likely cause
- Proposed adjustment
- Expected effect
- Risk/trade-off
- Confidence
- Pilot recommendation
- Human decision

## Examples
- Change model tier for a phase if acceptance improves at lower cost.
- Tighten FAST criteria if many FAST demands escalate.
- Add a skill if repeated review findings share a domain cause.

## Example artifact
`examples/generated/insights.md` shows how to convert an observability rollup into human-reviewable improvement proposals.

## Governance rule
Insights never change `core/model-policy.md`, rules, lanes, skills, templates,
or triggers automatically. They create `policy_insight_proposed` evidence for a
human decision and a later explicit commit.
