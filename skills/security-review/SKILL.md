---
name: security-review
description: Security review lens. Load for security-sensitive changes or any SAFE-lane demand.
trigger: Sensitive data, auth/authz, secrets, external input, permissions, payments, or SAFE lane.
sections_to_load:
  - checks
  - output
---

# Skill - Security Review

## purpose
Optional review lens for security-sensitive demands.

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

## checks
- Data exposure and logging.
- Authn/authz boundaries.
- Secret handling.
- Input validation and injection risk.
- Dependency and configuration risk.
- Rollback and incident evidence.

## output
Security findings, required mitigations, residual risks, and whether the lane must rise.
