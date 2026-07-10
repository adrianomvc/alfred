---
name: lane-fast
description: Lane — FAST
load: lane
triggers:
  phase: all
  lane: fast
  demand-type: all
  agent: all
---

# Lane — FAST

Low risk/complexity. Light process, minimal spec, **delegated autonomy**, few checkpoints. The supreme law still applies (no hallucination; on doubt, stop and ask).

> Contract (uniform across lanes): `DoD per phase` · `HITL checkpoints` · `minimal artifacts` · `tracking`. The lifecycle asks for "the active lane," not a fixed mode.

## DoD per phase
| Phase | Done when |
|---|---|
| Inception | problem + objective clear; Risk Mode proposed |
| Design | approach clear (inline) — no separate Design phase; folds into Execution |
| Execution | small PR; self-review; lean audit |
| Validate | relevant local tests pass |
| Operation | merge done; optional note |

## HITL checkpoints
**Delegated autonomy** — the AI executes and **records in `audit`** (the human stays responsible). Explicit human call **only** when an escalation trigger fires (`../common/escalation-triggers.md`): scope grew, risk rose, cost over ceiling, destructive op, security, unresolved ambiguity, cross-app effect, repeated failure.

## Minimal artifacts
`state` (1 entry) + lean `audit` + PR. The spec **is** the PR's title + description. No formal `decisions`.

## Tracking
`state` + lean `audit`. Lean audit = action + responsibility (`Sob delegação de: <human>`), **not** a raw input/output log. Minimum fields: date, action, under-delegation-of.

## Toolbar (single line)
```
ALFRED | SIGLA:ABC | #001-ajuste-cache | FAST | Execution (3/5) | missing: PR + merge
```
Includes compact cost. In rich-capable hosts, FAST renders as a compact rich
block; in text fallback, it stays a single line.

## Anti-degeneration
A critical thing must not be treated as FAST: hard overrides (`core/risk-mode.md`) force the mode up; on detecting a trigger, reclassification is mandatory.
