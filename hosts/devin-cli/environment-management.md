# DEVIN Enterprise Environment Management

This policy is capability-gated: Alfred prepares and validates the handoff, but
changes an Enterprise or Organization blueprint only after an authorized human
confirms admin access and rollout scope.

## Tier placement
| Tier | Put here | Never put here |
|---|---|---|
| Enterprise | shared runtimes, corporate CA/proxy, security tools, internal CLIs | repository dependency installation |
| Organization | team-only registry/tooling and procedures | configuration intended for every org |
| Repository | dependency sync, build/test commands, repo knowledge | shared credentials duplicated from higher tiers |

Knowledge is additive in Devin. Use unique names and make conflicts explicit;
Alfred safety rules remain the precedence authority. Secrets are references in
Markdown and values only in the Devin Secrets UI or an approved secret store.
Never place secret values in blueprint YAML, project JSON, logs, or argv.

## Rollout and health
Run post-build health checks and retain the last known-good snapshot. Roll out to
one pilot organization, then at most 10%, 50%, and 100%; each stage requires a
healthy build and human approval. On widespread failure, restore the last
known-good blueprint before investigating in isolation.

Review failed, partial, and stale builds weekly. A pin is a temporary exception:
record snapshot id, reason, owner, pinned-at, and review-by. Alfred warns after
review-by; only an authorized human pins or unpins.

## Grounding
This policy adapts Devin's official
`https://docs.devin.ai/enterprise/environment-management/best-practices`.
Repository-specific commands stay at repository tier; shared configuration
defaults to Enterprise, while Organization is the intentional exception tier.
