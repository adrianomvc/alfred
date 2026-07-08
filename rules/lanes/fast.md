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
ALFRED | SIGLA:SQ9 | #001-implantacao-alfred | FAST | Execution (3/5) | falta: PR + merge
```
Includes compact cost. FAST does not render the full ASCII block.

## Anti-degeneration
A critical thing must not be treated as FAST: hard overrides (`core/risk-mode.md`) force the mode up; on detecting a trigger, reclassification is mandatory.
