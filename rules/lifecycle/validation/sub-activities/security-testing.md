---
name: sub-activity-security-testing
description: Validate sub-activity — Security Testing
load: sub-activity
triggers:
  phase: validation
  lane: all
  demand-type: all
  agent: all
---

# Validate sub-activity — Security Testing

> Trigger: **sensitive data** or a changed **attack surface** (auth, input,
> secrets, external exposure). Optional, inside Validate.

## Purpose
Prove the change does not introduce a security regression — that data, access,
and inputs stay protected.

## Inputs
`nfr-design` security choices, `knowledge` security policies (D42), the active
security skill if present (D12/D36), the changed surface from `tech-inception`.

## Steps
1. Map the **attack surface** the change adds or alters (inputs, auth, secrets,
   exposure).
2. Check **input handling** (injection, validation) and **authz** (least
   privilege) on the changed paths.
3. Verify **secrets/data handling**: no secrets in code/logs, sensitive data
   protected in transit/at rest.
4. Run available **security checks** (SAST/dependency/secret scan) by role.
5. Record findings; route high-severity issues to `decisions` / a stronger lane.

## Output
Security findings with severity, checks run, and residual risks in the validation
evidence.

## Depth by mode
FAST = basic input/secret sanity on the change · Standard = surface review +
available scans · SAFE = full review with documented evidence and sign-off.
