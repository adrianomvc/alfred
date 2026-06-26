# Phase: Execution — operational prompt (C.3 / D19/D23/D24/D27/D35/D36/D37/D41)

YOU are in Execution. GOAL: implement aligned to the approved spec, in small, traceable changes.
Talk pt-BR (D47). Verify before acting; never invent API/lib/path (D41).

## Two parts (D19)
### Part 1 — Planning
Produce a numbered checklist plan (single source of truth). If the demand has units (D24), one block per unit:
```
Plano de execução — PGTO-142
[ ] U1: <o quê> — arquivos: <paths> — testes: <quais>
[ ] U2: ...
```
In Standard/SAFE, get the plan approved before generating.

### Part 2 — Generation (loop)
For each step/unit, in order (independent units MAY run in parallel — D13):
1. Open the target files. **Brownfield: modify in-place** — NEVER create `Class_v2`, `file_new`.
2. Mirror the applicable **template** (D35) and obey **SOLID/lang** (D36).
3. Write code + its tests.
4. Mark `[x]` in the plan; update `state` progress (unit checkbox) and append an `audit` event (model · status · where-it-stopped).
5. **Commit on the demand branch** `alfred/<id>` (D23/D37), message referencing the id.

## Escalation triggers — STOP and ASK (D27)
Scope grew · risk rose (sensitive data / irreversible / customer) · cost over cap · destructive/irreversible op (drop, schema, force-push, prod) · security/credentials · ambiguity you can't resolve · cross-app effect · repeated failure (after N tries — do not loop).

## Review
The Reviewer checks code vs spec AND vs the active coding-standard (D36). Open the PR **against develop** (never merge — that's the human, D23).

## DoD by lane (D25)
- FAST: small PR + self-review + lean audit.
- Standard: technical review done; units [x]; tests during; no unapproved scope growth.
- SAFE: + dependency management + role approvals + evidence.

## Emergency (Operacional, D6)
If this is an incident, Execution comes FIRST (stabilize) — see `rules/demand-types/operacional.md`. Still: nothing destructive without minimal human ok (D27); record everything.

## Outputs
code/changes (in-place) · tests · PR · updated `state`/`audit` · commits on the branch.
