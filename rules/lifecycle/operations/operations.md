# Phase: Operations — operational prompt (C.5 / D6/D10/D11/D32/D43/D44/D45/D47)

YOU are in Operations. GOAL: follow the delivery in use, capture learning, and close. (Where Alfred extends AI-DLC.)
Talk pt-BR (D47). Never invent metrics — if not measurable, leave blank/approx (D41).

## Steps
1. **Release / note** (scaled by lane). For SAFE: confirm monitoring and keep rollback ready.
2. **Collect metrics (D10/D43)** into `metrics`: models used per agent/phase, cost (tokens/$), efficiency (lead time, rework, first-time acceptance). Update the sigla `metrics-rollup`. Check **baselines** (D32) and flag deviations (do not punish — surface for the human, D7).
3. **Summarize (D11)** — write `summary` (what was done, key decisions w/ links, skills used, debts/next steps) and **update the `index`** (move the demand to "Concluídas"). Archive detail; keep the digest.
4. **Post-mortem** — MANDATORY only if the demand came from an emergency (D6): root cause, retro spec, lessons.
5. **Notify by email (D44)** — at the strategic point "Demanda concluída": send via the `notification` connector to the target in `knowledge` (transparent if configured; ASK only if it deviates). Subject `[Alfred-Framework][<SIGLA>][<id>] Demanda concluída — <título>`; body short; **files attached** (metrics, audit logs, summary). If no channel → remind the human to send manually. Record the send in `audit`.
6. **Close** — set `state` status = concluída (D28); turn debts/preventive actions into NEW demands.

## DoD by lane (D25)
- FAST: closes on merge; note optional.
- Standard: release notes + basic metrics + `summary` + `index`.
- SAFE: + monitoring + active rollback + (if emergency) post-mortem.

## Edge cases
- Cost capture unavailable (no host hook) → record approx/blank; never fabricate (D41).
- Deviating baselines → open a conversation/insight, not an automatic action.
- Demand was paused/cancelled → only humans cancel; on cancel, write a mini-`summary` (why) and update the index.

## Outputs
release note · `metrics` (+rollup) · `summary` · `index` updated · email sent (or reminder) · `state` closed.
