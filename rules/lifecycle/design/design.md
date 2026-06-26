# Phase: Design — operational prompt (C.2 / D19/D24/D29/D35/D36/D41)

YOU are in Design. GOAL: define HOW to solve before any code. SDD gate (D29): no Execution without this phase's DoD.
Talk pt-BR (D47). Never invent — verify in reverse-eng/artifacts or ASK (D41).

## Inputs to load (JIT)
`requirements` + `tech-inception` + `risk` (from Inception); applicable `knowledge` policies; the template registry (D35); the active coding-standard/lang skill (D36). Do NOT load other phases.

## Steps
1. **Solution shaping.** Draft the solution. In SAFE, list **alternatives considered** with trade-offs and pick one with rationale.
2. **Write the spec (SDD).** Fill `spec` (HUB business view) and the app `spec` (technical, per repo). Always include **acceptance criteria** that are verifiable (D29).
3. **By-trigger sub-activities (D19) — include ONLY if the trigger applies:**
   - new component/service → application-design notes;
   - decomposition needed → **units** (D24): list U1..Un, each small and, if independent, parallelizable (D13);
   - new/complex business logic → functional-design notes;
   - performance/security/scalability → NFR notes;
   - deploy/infra change → infrastructure notes.
   For each one you SKIP, state why in one line (no silent skips).
4. **Execution plan.** Impact, sequence, parallelization (D13), and the **test plan** (what will be tested and how).
5. **Confirm standards.** Resolve the applicable **template** (D35) and **coding-standard/lang** (D36); if a needed language skill is missing, ASK before assuming.
6. **Record decisions** in `decisions` (append-only): context · options · decision · who · trade-offs.
7. **Revalidate Risk Mode.** If anything raises risk (sensitive data, irreversibility, more apps), reclassify and escalate (D27/2.8).

## DoD by lane (D25) — gate
- FAST: approach clear inline (spec = the PR).
- Standard: spec + acceptance criteria + decisions + execution/test plan.
- SAFE: + alternatives + dependencies + rollout/rollback + **architecture approved by Tech Lead**.

## Checkpoint (HITL)
Present the standard 2-option message in pt-BR:
> "Design pronto. Permita-me prosseguir para Execution, ou deseja ajustes? [🔧 Pedir ajustes] [✅ Aprovar e continuar]"
In FAST it is implicit (delegated autonomy); in Standard/SAFE wait for explicit approval (spec/architecture).

## Edge cases
- Requirements still ambiguous → go back to Inception gate; do not 'fill the gap'.
- Spec growing > ~1 screen → split by unit/theme and index it (D11).
- Demand touches an app whose mode should rise → record per-app override in `risk` (2.11).

## Outputs
`spec` (HUB + app) · acceptance criteria · `decisions` · execution/test plan · updated `state`/`audit`.
