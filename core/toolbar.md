# Toolbar

The toolbar is rendered by the Orchestrator at the top of every interaction. It is derived from `state`; it is never a separate source of truth.

`scripts/render-toolbar.ps1` is an optional helper that renders the same information from a `001-state.md`. Hosts that cannot run scripts render the toolbar manually from the same fields.

## FAST format
One line only:

```text
ALFRED | SIGLA:SQ9 | #001-implantacao-alfred | FAST | Execution (3/5) | model: <current> | cost: <compact> | left: PR + merge
```

## Standard/SAFE format
ASCII block with demand, lane, model, progress, phase track, current step, checkpoint, next step, and accumulated cost.

```text
+-- ALFRED ------------------------------- SIGLA:SQ9 | #001-implantacao-alfred --+
| Lane: STANDARD        Model: <current>       Progress: 45%     |
| Cost: 312k tokens | ~US$ 4.80 | 18 interactions                |
| 1 Inception [x] -> 2 Design [>] -> 3 Execution [ ] -> 4 Validate [ ] -> 5 Operation [ ] |
| Step : generating technical spec (app: sq9-app)                |
| HITL : spec approval - Tech Lead                               |
| Next : review routing alternatives                             |
+----------------------------------------------------------------+
```


## Rules
- Show where the demand is, what remains, and the next human checkpoint.
- Use pt-BR when rendered to people.
- If model changes, announce it and record an audit event.
- If emergency Execution-first is active, mark Inception/Design as post-mortem pending.
- Optional tooling must never become the source of truth; `state` remains authoritative.
