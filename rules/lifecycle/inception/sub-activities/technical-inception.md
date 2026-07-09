---
name: sub-activity-technical-inception
description: Inception sub-activity — Technical Inception
load: sub-activity
triggers:
  phase: inception
  lane: all
  demand-type: all
  agent: all
---

# Inception sub-activity — Technical Inception

> Trigger: **always** — Alfred performs the technical lens for every demand
> (the `tech-inception` output). Optional only in the sense of depth by mode.

## Purpose
Establish what is technically affected before designing, via reverse-engineering
of the target systems — so Design starts from reality, not assumption.

## Inputs
The demand intent, target HUB/App repos, reverse-engineering of affected code,
`connectors/git.md` for repo access, active language/platform skills (D12/D36).

## Steps
1. Reverse-engineer the **affected systems/apps**: which repos, modules, and
   boundaries the demand touches.
2. Identify **integration points**: APIs, queues, schemas, jobs, external deps.
3. List **technical risks and constraints**: coupling, data volume, migration
   needs, security/compliance surface.
4. Assess **feasibility** and surface unknowns as **technical questions** (route
   to `requirements-elicitation`).
5. Record the lens as `tech-inception`; feed signals into `risk-mode-proposal`.

## Output
`tech-inception`: affected systems, integration points, technical risks,
constraints, feasibility notes, and technical questions.

## Depth by mode
FAST = the one or two systems touched, inline · Standard = affected systems +
integration points + risks · SAFE = + constraints, compliance surface, and a
risk analysis that can raise the lane.
