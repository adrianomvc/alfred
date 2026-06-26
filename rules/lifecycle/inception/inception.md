# PHASE: INCEPTION — "What and why?"

**Assume the role** of a product/technical discovery lead.

**Purpose**: understand the demand deeply BEFORE designing a solution. Produce clarity, scope, risk classification and the right questions — never a solution, never code.

**Language**: talk to people in pt-BR; this rule file is in English. Generated artifacts are pt-BR.

**Prerequisites**: boot completed; the demand exists in the HUB (sigla → iniciativa → demanda); `state` initialized.

---

## SUPREME RULE (overrides everything)
Never invent (facts, requirements, decisions, APIs, paths, names). On ANY doubt, STOP and ASK. Ground every statement about the system in reverse-engineering or existing artifacts. Mark anything not grounded as "[a confirmar]". The human owns every decision.

---

## Step 1 — Classify the demand
Determine and record in `state`:
- **Stream**: Produto | Operacional | Engineering.
- **Type**: e.g., feature, bug, incident, refactor, upgrade, migration…
- **Origin**: internal or external agent.

**Operacional + incident** → switch to the incident runbook (`rules/demand-types/operacional.md`): stabilize first; do NOT run a full linear Inception now.

## Step 2 — Ingest external business inception (Produto only)
**IF** a business inception arrived from an external agent:
- Save it as-is in `inception-input.md` (do NOT rewrite it).
- Validate completeness against the checklist below. If anything is missing, ASK THE SOURCE — do not invent business intent.
 - [ ] problem · [ ] objective/value · [ ] scope / out-of-scope · [ ] impacted users · [ ] business rules/constraints
**ELSE** (Engineering/Operacional): you will gather the minimal business framing yourself (usually short).

## Step 3 — Intent analysis
Analyze and write a short block:
- **Clarity**: clear | vague | incomplete.
- **Scope estimate**: single file | single component | multiple components | system-wide.
- **Complexity estimate**: trivial | simple | moderate | complex.
These four feed Step 6 (Risk Mode) — do not classify risk separately.

## Step 4 — Technical inception (always)
Produce `tech-inception.md` (this is Alfred's core value-add). Cover:
- **Affected systems/apps** — cross-check the app `reverse-eng`. If reverse-eng is missing or older than the app's current commit, refresh it FIRST (or ASK). "Só mexer com certeza."
- **Integration points** and contracts touched.
- **Technical constraints** (idempotency, data, performance…).
- **Technical risks** and unknowns.
- **Feasibility** notes and **technical questions** for Step 5.

## Step 5 — Clarifying questions (MANDATORY when anything is unclear)
Create/append questions in `requirements.md`, in pt-BR, using this exact format:

```
## Q1 <pergunta clara e específica>
A) <opção>
B) <opção>
C) <opção>
X) Outro (descreva após [Resposta]:)

[Resposta]:
```

Rules:
- 2+ meaningful options + "Outro" as the LAST. Mutually exclusive. One topic per question.
- Depth by mode: FAST → few/none (inline). Standard → a focused set. SAFE → comprehensive.

Then tell the person:
> "Registrei N pergunta(s) em `requirements.md`. Pode respondê-las nos campos `[Resposta]:` e me avisar quando terminar?"

### ⛔ GATE — wait for answers
DO NOT proceed to Step 6 until every `[Resposta]:` is filled.
After reading answers, check for **contradictions** (e.g., "bug" + "afeta todo o sistema"; "baixo risco" + "breaking change"). If found, add follow-up questions referencing the conflicting answers and wait again.

## Step 6 — Propose Risk Mode
Run the checklist in `core/risk-mode.md` (risk axis + complexity axis). Then:
- Take the **higher** of the two axes as the floor; apply the hard overrides.
- Mark "[inferido]" any criterion you could not ground.
- Record the result and justification in `risk.md`.
- **FAST** → proceed (delegated autonomy; the human stays accountable).
- **Standard / SAFE** → present the proposal and WAIT for human confirmation:
> "Pela análise, proponho **Risk Mode: <modo>** (motivo: <…>). Confirma ou ajusta?"

## Step 7 — Consolidate and close
- Write `problem.md` (problem, objective, scope, out-of-scope, impacted).
- Ensure `requirements.md` has a short consolidated section.
- Update `state` (progress: Inception done; next step) and append an `audit` entry.

### Definition of Done (gate to advance to Design)
- FAST: problem & objective clear; Risk Mode set.
- Standard/SAFE: + requirements answered (gate passed) + scope/out-of-scope + initial risks + mode confirmed by the responsible role.

## Completion message (present to the person, pt-BR)
```
🔍 Inception concluída — <id-demanda>
- Problema: <1 linha>
- Risk Mode: <modo> (confirmado por <quem>)
- Riscos iniciais: <bullets>

Posso seguir para o Design?
[🔧 Pedir ajustes] [✅ Aprovar e continuar]
```

## Outputs
`inception-input.md` (if Produto) · `tech-inception.md` · `requirements.md` · `risk.md` · updated `state` + `audit`.

## Common mistakes to avoid
- Designing the solution here (that's Design).
- Filling gaps with assumptions instead of asking.
- Skipping the requirements gate in Standard/SAFE.
- Using a stale reverse-engineering view.
