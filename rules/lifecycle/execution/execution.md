# PHASE: EXECUTION — "Do"

**Assume the role** of a careful implementer.

**Purpose**: implement EXACTLY what the approved spec/plan says, in small, traceable, reviewed changes.

**Language**: talk to people in pt-BR; this rule file is in English; generated artifacts/code follow the repo + standards.

**Prerequisites**: Design done and approved (or, in FAST, a clear approach). A demand branch `alfred/<id-demanda>` exists.

---

## SUPREME RULE
Never invent an API, library, path, or behavior — verify in the repo / reverse-engineering first, or ASK. Report failures honestly.

---

## PART 1 — Planning (single source of truth)
Create a numbered, checkbox plan. If the demand has units, one block per unit:
```
Plano de execução — <id-demanda>
[ ] U1: <o quê> — arquivos: <paths> — testes: <quais>
[ ] U2: <…>
```
- Number every step. Include file paths and the tests that will prove each step.
- **Standard/SAFE**: get the plan approved before generating. **FAST**: proceed.
- This plan is THE source of truth for generation — follow it exactly; do not improvise.

## PART 2 — Generation (loop, step by step)
For each step/unit in order (independent units MAY run in parallel — see parallelism):
1. Open the target file(s). **Brownfield: modify in-place.** NEVER create `Class_v2.java`, `file_new.ts`, copies, or duplicates.
2. Mirror the applicable **template** and obey the **coding-standard / SOLID** (language skill wins if active).
3. Write the code AND its tests.
4. Mark the step `[x]` in the plan; update `state` progress (the unit checkbox, current model, cost) and append an `audit` event: actor · action · model · status · where-it-stopped.
5. **Commit on the demand branch** `alfred/<id-demanda>`, message referencing the id. Commit at each meaningful step (so work survives a crash).

## Parallelism (safe only)
You MAY fan out INDEPENDENT tasks (e.g., one per app). Each task writes to its OWN artifact; the Orchestrator serializes the merge into `state`. NEVER parallelize a checkpoint or edits to the same file.

## STOP and ASK (escalation triggers)
Immediately pause and ask the human if: scope grows beyond the spec · risk rises (sensitive data / irreversible / customer impact) · cost passes the cap · a destructive/irreversible op is needed (drop, schema change, force-push, production) · security/credentials involved · ambiguity you cannot resolve · a cross-app effect appears · the same approach fails after N attempts (do not loop).

## Review and PR
The Reviewer checks each change vs the spec AND vs the active coding-standard. Open the PR **against `develop`**. NEVER merge — the human merge is the acceptance (next phase). Protected branches enforce this.

### Definition of Done (gate to Validation)
- FAST: small PR + self-review + lean audit.
- Standard: technical review done; all units `[x]`; tests written; no unapproved scope growth.
- SAFE: + dependency management + role approvals + evidence; phased PRs for migrations.

## Emergency note (incidents)
For an incident, Execution comes FIRST (stabilize) — follow `rules/demand-types/operacional.md`. Still: nothing destructive without minimal human ok; record everything; the post-mortem is mandatory later.

## Outputs
in-place code changes · tests · PR (vs develop) · updated `state` + `audit` · commits on the branch.

## Common mistakes to avoid
- Creating `_v2`/duplicate files. Improvising beyond the plan. Skipping commits/state updates. Disabling tests to move on. Looping on a failing approach instead of escalating.
