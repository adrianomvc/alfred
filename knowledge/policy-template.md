---
name: policy-template
description: Template for always-on Alfred knowledge policies
scope: template
trigger: creating or changing a knowledge policy file
---

# Policy Template

Use this template for always-on Alfred knowledge policies.

## identity
- policy id:
- title:
- scope: org | sigla | app | demand
- owner:
- status: draft | active | deprecated
- version:
- updated at:

## applies to
- streams:
- lanes:
- repositories:
- environments:
- data classes:
- phases:

## rule
State the mandatory rule in operational language.

## rationale
Explain why the rule exists and what risk it controls.

## enforcement
- block action:
- require human approval:
- require audit entry:
- require evidence:
- escalation owner:

## exceptions
- allowed: yes | no
- required approver:
- expiry required: yes | no
- record location:

## audit evidence
| Event | Required fields | Artifact |
|---|---|---|
| policy applied | policy id, demand id, action, result | audit/JSONL |
| exception approved | owner, reason, expiry, scope | decisions/audit |

## related artifacts
- state:
- decisions:
- audit:
- metrics:
