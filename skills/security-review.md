---
name: security-review
description: Security review lens. Load for security-sensitive changes or any SAFE-lane demand.
---

# Skill - Security Review

## name
`security-review`

## purpose
Optional review lens for security-sensitive demands.

## trigger
Sensitive data, auth/authz, secrets, external input, permissions, payments, or SAFE lane.

## inputs
- active demand `state`
- risk artifact
- technical `spec`
- changed files and configuration
- validation evidence when present

## expected output
- security findings
- required mitigations
- residual risks
- lane escalation recommendation when needed

## link
`skills/security-review.md`

## sections to load
- `checks`
- `output`

## checks
- Data exposure and logging.
- Authn/authz boundaries.
- Secret handling.
- Input validation and injection risk.
- Dependency and configuration risk.
- Rollback and incident evidence.

## output
Security findings, required mitigations, residual risks, and whether the lane must rise.
