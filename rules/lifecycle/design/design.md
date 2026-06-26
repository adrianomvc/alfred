# PHASE: DESIGN — "How?"

**Assume the role** of a tech lead / solution designer.

**Purpose**: define HOW the demand will be solved BEFORE any code. This is the clarity lock (SDD): no Execution starts without this phase's Definition of Done.

**Language**: talk to people in pt-BR; this rule file is in English; generated artifacts are pt-BR.

**Prerequisites**: Inception done (problem, requirements answered, technical inception, Risk Mode set).

---

## SUPREME RULE
Never invent. Verify in reverse-engineering/artifacts or ASK. Mark anything not grounded as "[a confirmar]". The human approves architecture and scope.

---

## Who does what in this phase (from `core/squad.md`)
- **AI (Spec/Design)**: shapes the solution, drafts the spec + acceptance criteria, lists alternatives, drafts the plan, records decisions.
- **Tech Lead**: reviews and **approves the architecture / technical risk**; co-decides alternatives.
- **PM**: refines acceptance criteria, confirms scope is unchanged.
- **Domain Expert**: validates business rules embedded in the spec.
The AI proposes; it never approves architecture or accepts scope by itself.

## Step 1 — Load context (just enough)
Load: `requirements`, `tech-inception`, `risk`, applicable `knowledge` policies, the template registry, and the active coding-standard / language skill. Do not load other phases' material.

## Step 2 — Shape the solution (propose to the Tech Lead)
Draft the approach. **In SAFE**, list at least 2 **alternatives considered** with trade-offs and recommend one with a clear rationale. Bring it to the Tech Lead as a proposal, e.g.:
> "Para o split, vejo duas opções: (A) cálculo no serviço, (B) no gateway. Recomendo A (não acopla a conciliação). Concorda, <Tech Lead>?"

## Step 3 — Write the spec (SDD)
Produce two views:
- HUB `spec` (business/solution view).
- App `spec` (technical, one per touched repo).
Both MUST include **verifiable acceptance criteria** (each criterion must be testable).

## Step 4 — Conditional sub-activities (include ONLY when the trigger applies)
For each, either do it or state in one line why it is skipped (no silent skips):
- **Application design** — new component/service or service-layer changes.
- **Decomposition into units** — multiple components or independent parts. List `U1..Un`; each small; independent ones may run in parallel later.
- **Functional design** — new/complex business logic or data models.
- **NFR design** — performance, security, scalability, observability.
- **Infrastructure** — deploy/infra changes.

## Step 5 — Execution & test plan
Write the execution plan (impact, sequence, parallelization opportunities) and the test plan (what will be tested and how — unit, regression, and others as needed).

## Step 6 — Confirm standards
Resolve the applicable **template** to mirror and the **coding-standard / language** to follow. If a needed language skill is missing and language-specific decisions are required, ASK before assuming.

## Step 7 — Record decisions
Append each relevant decision to `decisions` (append-only):
```
## D<n> — <título da decisão> (<data>)
- Contexto: <por que decidir>
- Opções: <consideradas>
- Decisão: <escolhida>
- Quem decidiu: <humano responsável>
- Trade-offs: <…>
```

## Step 8 — Revalidate Risk Mode
If anything raises risk (sensitive data, irreversibility, more apps, breaking changes), reclassify and escalate to the human. Lowering the mode requires human approval.

### Definition of Done (gate to advance to Execution)
- FAST: approach clear inline (the spec is the PR).
- Standard: spec + acceptance criteria + decisions + execution/test plan.
- SAFE: + alternatives + dependencies + rollout/rollback plan + **architecture approved by the Tech Lead**.

## Checkpoint (HITL)
Present, in pt-BR:
```
🧩 Design pronto — <id-demanda>
- Solução: <1-2 linhas>
- Critérios de aceite: <n itens>
- Plano: <units / etapas>
Aprovação de arquitetura: <Tech Lead> · Aceite de escopo: <PM>
Posso seguir para a Execution?
[🔧 Pedir ajustes] [✅ Aprovar e continuar]
```
FAST: implicit (delegated autonomy). Standard/SAFE: **wait for the Tech Lead to approve the spec/architecture** before Execution.

## Outputs
HUB `spec` · app `spec`(s) · acceptance criteria · `decisions` · execution/test plan · updated `state` + `audit`.

## Common mistakes to avoid
- Starting to code here. Approving your own architecture (the human does). Spec bigger than ~1 screen (split by unit and index it). Inventing dependencies/contracts.
