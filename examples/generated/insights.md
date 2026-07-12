# Generated Metrics Insights

## Insight 1 - Repeated Artifact Reads
- Observation: `sha256:2200e24eea7afd7174706a6d1b8a7a98ddc3a2d04bf0e3940fd22adaa1fd3f28` was read 2 times in the observed window.
- Evidence: evt-example-request-001:sha256:example-token-budget, evt-example-artifact-accessed-001:sha256:example-token-budget
- Likely cause: The same artifact may be reloaded instead of using a stable snapshot until it changes.
- Proposed adjustment: Pilot caching artifact metadata until an `artifact_changed` event or content hash change.
- Expected effect: Fewer repeated reads and lower context growth without hiding changed files.
- Risk/trade-off: A stale snapshot is possible if artifact changes are not observed.
- Confidence: medium
- Pilot recommendation: Run on 5+ Standard demands before changing rules.
- Human decision: pending
