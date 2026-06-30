# Common rule — question format

How Alfred asks humans. Inherited from AI-DLC `question-format-guide`. Used in Inception requirements and in unit decomposition. Questions go to people in **pt-BR** (language policy).

## Principles
- **All questions live in the `requirements` artifact** — the **question list is worked in the file**, not the chat: portable across hosts and resilient (survives context loss). **Always state the file path** so the person knows where to answer (see `## Where the questions live`).
  - *Only exception:* a **single, one-off clarification** the model needs right now may be asked inline in chat. The moment it becomes a list, or the answer is material (scope, risk, a decision), it goes to the file.
- **Multiple choice + free-text answer** — offer 2 to 5 options (`A` to `E`) so the human answers fast; free text goes directly in `[Resposta]:`.
- **Recommended option** — when there is a safer/default path, mark one option with `(Recomendado)`. For unknown SAFE facts, recommend confirming before execution instead of guessing.
- **`[Resposta]:` tag** — each question is followed by a `[Resposta]:` line the human fills.
- **One decision per question** — do not bundle several decisions into one item.
- **Option limit** — use the fewest useful options. Minimum 2, maximum 5. Do not add filler options just to reach 5.
- **No emergent behavior** — do not invent options the context does not support; if you do not know, ask, do not guess (supreme law).

## Format
```markdown
### Q1 — <clear, specific question?>
- A) <opcao recomendada> (Recomendado)
- B) <opcao alternativa>
- C) A confirmar
- D) <opcional, se necessario>
- E) <opcional, se necessario>

[Resposta]:
```

## Where the questions live
- **HUB:** `<id-iniciativa>/<id-demanda>/01-inception/003-requirements.md` — the canonical question list for the demand.
- Unit-decomposition questions use the same file (or the unit's `questions` block) — never loose in chat.
- **Surface, do not embed:** the toolbar/response points to the file, e.g. `⏸ 1 decisão pendente → 003-requirements.md`. The person may answer in chat; Alfred then writes the answer into the `[Resposta]:` line of the file.
- State the path explicitly each time there are open questions, so it is reachable without searching.

## Gate
Do not advance to the next phase until the answers are filled and validated. On reading the answers, **detect contradiction/ambiguity** (e.g. "bug" + "affects the whole system") and generate a follow-up.

## Depth per mode
- **FAST** — few or no questions, inline.
- **Standard** — a clarification set.
- **SAFE** — comprehensive + traceability.
