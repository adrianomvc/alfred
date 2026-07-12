---
name: common-question-format
description: Common rule — question format
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule — question format

How Alfred asks humans. Inherited from AI-DLC `question-format-guide`. Used in Inception requirements and in unit decomposition. Questions go to people in **pt-BR** (language policy).

## Principles
- **All questions live in the `requirements` artifact** — the **question list is worked in the file, never in chat**: portable across hosts and resilient (survives context loss). **Always state the file path** so the person knows where to answer (see `## Where the questions live`).
- **The human answers in the artifact** — Alfred creates/updates `003-requirements.md`, tells the human to edit each `[Resposta]:` line, save the file, and then say `pronto`/`terminei` in chat. Chat confirms completion only; it does not carry the answers.
- **No host-native question widgets for requirements** — Claude/Codex/Devin UI prompts, popups, or multiple-choice widgets must not be used to ask or collect requirements answers. Chat/UI may only notify that `003-requirements.md` has open questions and point to the file.
- **AI-DLC-compatible default: single choice + free text** — offer 2 to 5 meaningful options using `A` to `E`, with `Outra / A confirmar` as the last option when the listed options may not cover the answer. The human answers with one letter in `[Resposta]:`.
- **Alfred extension: multiple selection** — only when the question explicitly says `selecione uma ou mais`, use checkbox options (`[ ]` / `[x]`) with no `A)`/`B)` labels. Use `[Resposta]:` only for extra detail.
- **Recommended option** — when there is a safer/default path, mark one option with `(Recomendado)`. For unknown SAFE facts, recommend confirming before execution instead of guessing.
- **Never pre-fill `[Resposta]:`** — the tag only orients; the human always answers (D7). No auto-confirm, not even for low-risk.
- **Layout by priority** — group blocking questions (`🔴 bloqueiam o avanço`) before optional ones (`🟡 podem responder depois`), each with a one-line "Por quê" and a status marker (`◻ aberta` · `✓ respondida` · `⚠ contradição`). See `templates/hub/requirements.md`.
- **`[Resposta]:` tag** — each question is followed by a `[Resposta]:` line the human fills.
- **One decision per question** — do not bundle several decisions into one item. If more than one option can be selected independently, prefer splitting the question; otherwise label it explicitly as `selecione uma ou mais` and present each option as a checkbox.
- **Option limit** — use the fewest useful options. Minimum 2, maximum 5. Do not add filler options just to reach 5.
- **No emergent behavior** — do not invent options the context does not support; if you do not know, ask, do not guess (supreme law).

## Format
```markdown
### Q1 — <clear, specific question?>
- A) <opcao recomendada> (Recomendado)
- B) <opcao alternativa>
- C) Outra / A confirmar
- D) <opcional, se necessario>
- E) <opcional, se necessario>

[Resposta]:
```

For explicit multiple selection (Alfred extension, not AI-DLC stock):

```markdown
### Q2 — <pergunta com selecao multipla?> (selecione uma ou mais)
Por quê: <impacto>.
- [ ] <opcao>
- [ ] <opcao>
- [ ] Outra / A confirmar

[Resposta]:
```

## Where the questions live
- **HUB:** `<id-iniciativa>/<id-demanda>/01-inception/003-requirements.md` — the canonical question list for the demand.
- Unit-decomposition questions use the same file (or the unit's `questions` block) — never loose in chat.
- **Surface, do not embed:** the toolbar/response points to the file, e.g. `⏸ 1 decisão pendente → 003-requirements.md`. The response must tell the human exactly what to do: open the file, fill `[Resposta]:`, save, then say `pronto`/`terminei`. Do not duplicate the question text/options in chat.
- State the path explicitly each time there are open questions, so it is reachable without searching.

## Gate
Do not advance to the next phase until the answers are filled in the artifact and validated. After the human says `pronto`/`terminei`, read the file, validate that required `[Resposta]:` slots are filled, **detect contradiction/ambiguity** (e.g. "bug" + "affects the whole system"), and generate a follow-up in the same file when needed.

## Depth per mode
- **FAST** — few or no questions; if a material question is needed, it still goes in the requirements artifact.
- **Standard** — a clarification set.
- **SAFE** — comprehensive + traceability.
