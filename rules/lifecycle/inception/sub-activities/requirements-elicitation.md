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
2. Write them as **multiple-choice questions** with an explicit `[Answer]:` slot
   (see question-format), grouped by topic.
3. Open the **gate**: do not advance to Design until the required answers land.
4. On answers, **detect contradictions** against earlier inputs; re-ask if needed.
5. Consolidate answers into `requirements`; record the gate in `audit`.

## Output
A requirements-questions file, gate status, contradiction checks, and a
consolidated `requirements` artifact.

## Depth by mode
FAST = skipped when the problem is clear; otherwise one or two inline questions ·
Standard = grouped questions + gate · SAFE = + traceability of each answer to a
requirement and explicit sign-off.
