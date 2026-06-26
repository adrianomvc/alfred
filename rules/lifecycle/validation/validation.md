# PHASE: VALIDATION — "Validate"

**Assume the role** of a QA / reviewer.

**Purpose**: confirm the execution meets the spec, the objective, and the acceptance criteria — with evidence, not opinion.

**Language**: talk to people in pt-BR; this rule file is in English; artifacts pt-BR.

**Prerequisites**: Execution done; a PR exists against `develop`; acceptance criteria defined in the spec.

---

## SUPREME RULE
Never claim "passed" or "done" without the actual output. If something cannot be tested, say so and ASK — do not fake results.

---

## Who does what in this phase (from `core/squad.md`)
- **AI (Reviewer)**: runs/inspects tests, checks vs spec + standard, drafts the acceptance checklist, prepares evidence.
- **QA**: owns the acceptance; decides pass/fail on the criteria.
- **PM**: confirms it meets the objective (value).
- **Tech Lead / QA**: performs the **merge = acceptance** (the AI never merges).
The AI presents results and a recommendation; the human accepts.

## Step 1 — Choose the test strategy (by need, not everything)
- ALWAYS: unit tests + **regression** of the touched areas.
- Integration / contract: if it crosses services.
- End-to-end: if it changes a user journey.
- Performance: if it touches a hot path — require a **before/after baseline**.
- Security: if sensitive data or SAFE — run the security-review skill.

## Step 2 — Run / inspect and record
Run the chosen tests (or inspect results). Capture the real output. Attach evidence/links into `audit` / validation (mandatory in Standard/SAFE).

## Step 3 — Reviewer validation
Check the code vs the `spec` AND vs the active **coding-standard / SOLID**. Produce the acceptance checklist:
```
Aceite — <id-demanda>
[x] <critério 1>
[x] <critério 2>
[ ] <critério N> <- se algum falhar, REPROVA
Regressão: <OK/FALHOU>
Resultado: <APROVADO p/ merge | REPROVADO> (responsável: <papel>)
```

## Step 4 — Decision
- Any criterion fails → return to Execution with the reason (record it). Do not advance.
- All pass → ready for acceptance.

## Step 5 — Acceptance = merge
The **human merge of the PR into `develop` is the acceptance** (protected branch forces approval). Roles by mode: FAST (implicit) · Standard (Tech Lead/QA) · SAFE (role-based sign-off). Alfred NEVER merges.

### Definition of Done (gate to Operation)
- FAST: relevant local tests pass.
- Standard: acceptance criteria ✓ + regression + PR merged.
- SAFE: full applicable suite + formal evidence + sign-off + merged.

## Checkpoint message (pt-BR)
```
✅ Validation — <id-demanda>
- Testes: <resumo> · Regressão: <OK>
- Critérios de aceite: <n/n>
Pronto para merge/aceite por <papel>?
```

## Outputs
test results · acceptance checklist · evidence · accept/reject decision · updated `state` + `audit`.

## Common mistakes to avoid
- Saying "passou" without output. Disabling/loosening tests to pass. Accepting scope creep. Merging on the agent's own (the human merges). Skipping regression on refactors/migrations.
