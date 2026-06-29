# Operation sub-activity — Closure Summary

> Trigger: **always**. Optional only in depth. The artifact future sessions load
> instead of re-reading everything.

## Purpose
Write the demand `summary` and refresh the `index` so a future session resumes
from the outcome without re-reading all phase artifacts (D11 cascaded loading).

## Inputs
The demand `state`, collected `metrics`, drift flags, release/PR link, the
HUB/App index templates.

## Steps
1. Write the `summary`: outcome, what changed, evidence/PR link, residual risks.
2. Add a short **resume note** — where future work should start.
3. Refresh the **index**:
   - HUB: `alfred-docs-hub/index.md` open/closed rows, metrics/insights links,
     follow-ups.
   - App: `.alfred-docs-app/<id-iniciativa>/<id-demanda>/001-index.md`
     reverse-eng status, evidence links, HUB sync status.
4. Ensure the summary is **self-contained** (no need to re-open phase folders).

## Output
A resumable `summary` plus an updated `index` that supports cascaded context
loading for the next session.

## Depth by mode
FAST = short close note · Standard = summary + index refresh · SAFE = + post-
release watch notes and explicit follow-up links.
