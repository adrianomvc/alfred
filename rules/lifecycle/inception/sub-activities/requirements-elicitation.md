---
name: sub-activity-requirements-elicitation
description: Inception sub-activity — Requirements Elicitation
load: sub-activity
triggers:
  phase: inception
  lane: all
  demand-type: all
  agent: all
---

# Inception sub-activity — Requirements Elicitation

> Trigger: clarity is **vague or incomplete** (from intent analysis). Optional,
> inside Inception. The gate blocks Design until answers arrive.

## Purpose
Turn open questions into structured, answerable requirements so Design does not
start on guesses — honoring the supreme law (if unsure, stop and ask).

## Inputs
Intent analysis (clarity class), `tech-inception` unknowns, business gaps from
`business-inception`, the question format (`../../../common/question-format.md`).

## Steps
1. Collect open points from the business and technical lenses.
2. Write them as **multiple-choice questions** with an explicit `[Resposta]:` slot
   (see question-format), grouped by topic.
3. Tell the human exactly what to do: open the `003-requirements.md` path, fill
   each required `[Resposta]:`, save the file, then say `pronto`/`terminei` in
   chat.
4. Open the **gate**: do not advance to Design until the required answers land
   in the file. Do not open host-native question widgets for requirements; chat
   or UI may only say that the file is waiting for answers and provide the path.
5. After the human confirms completion, read the file and **detect
   contradictions** against earlier inputs; re-ask in the same file if needed.
6. Consolidate answers into `requirements`; record the gate in `audit`.

## Output
A requirements-questions file, gate status, contradiction checks, and a
consolidated `requirements` artifact.

## Depth by mode
FAST = skipped when the problem is clear; otherwise one or two questions in the
requirements artifact · Standard = grouped questions + gate · SAFE = +
traceability of each answer to a requirement and explicit sign-off.
