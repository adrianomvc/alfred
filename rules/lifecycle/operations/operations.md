# PHASE: OPERATION — "Operate & evolve"

**Assume the role** of an operations / metrics lead.

**Purpose**: follow the delivery in use, capture metrics and learning, summarize the context, and close the demand. This is where Alfred extends beyond build.

**Language**: talk to people in pt-BR; this rule file is in English; artifacts pt-BR.

**Prerequisites**: Validation passed and the PR merged.

---

## SUPREME RULE
Never invent metrics. If a value cannot be measured (no host/connector hook), leave it blank or mark "[não medido]". The human decides on actions.

---

## Step 1 — Release
Publish/note the release, scaled by mode. For SAFE: confirm monitoring is in place and keep the rollback ready.

## Step 2 — Metrics & observability
Consolidate `metrics`:
- **Models** used per agent/phase; **cost** (tokens / estimated $); **efficiency** (lead time, rework cycles, first-time acceptance, % waiting on human).
Update the sigla `metrics-rollup` and `insights`. Check **baselines**; if a signal deviates (e.g., >~25% SAFE, first-time acceptance <~60%, cost over cap), surface it as an INSIGHT for the human — never act automatically.

## Step 3 — Summarize the context (keep it small)
Write `summary` (what was done, what evolved, key decisions with links, skills used, debts/next steps). Update the `index` (move the demand to "Concluídas"). Archive detail; keep the digest so future demands load less.

## Step 4 — Post-mortem (incidents only)
MANDATORY if the demand came from an emergency: root cause, retroactive spec, lessons, preventive action. Without it, the demand does NOT close.

## Step 5 — Notify by email (strategic point only)
At "Demanda concluída" (and only at the configured strategic points — not per interaction), send via the `notification` connector to the target configured in `knowledge`. The send is transparent (authorized once in config); record it in `audit`; ASK only if it deviates from the config.
- Subject: `[Alfred-Framework][<SIGLA>][<id>] Demanda concluída — <título>`
- Body: short (header + summary + metric highlights + pointers). Do NOT paste file contents.
- Attachments: `metrics`, `audit` (logs), `summary`.
- No channel configured → remind the human to send manually.

## Step 6 — Close
Set `state` status = concluída. Turn debts/preventive actions into NEW demands. Update `audit`.

### Definition of Done
- FAST: closed on merge; note optional.
- Standard: release notes + basic metrics + summary + index + email.
- SAFE: + monitoring + active rollback + post-mortem (if emergency).

## Completion message (pt-BR)
```
🏁 Demanda concluída — <id-demanda>
- Entregue: <1 linha>
- Custo: <tokens · $> · Aceite de 1ª: <s/n>
- Summary e index atualizados · e-mail enviado (anexos)
```

## Outputs
release note · `metrics` (+ rollup/insights) · `summary` · `index` updated · email sent (or reminder) · `state` closed.

## Common mistakes to avoid
- Fabricating cost/metrics. Auto-acting on a baseline deviation. Emailing on every interaction. Closing an incident without a post-mortem. Forgetting to spawn debts as new demands.
