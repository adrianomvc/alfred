# Phase: Inception — operational prompt (C.1 / D18/D31/D33/D41)

GOAL: understand the demand before designing. Produce clarity, not a solution.
Talk pt-BR (D47). Never invent; ask on doubt (D41).

## 1. Identify
Determine stream/type (D5). If **Produto** and a business inception arrived from an external agent, INGEST it into `inception-input` — do NOT redo business discovery; only validate completeness (ask the source if something is missing).

## 2. Intent analysis (D18)
Classify and write down: clarity (clear/vague/incomplete) · type · scope (1 file → cross-app) · complexity. Use this to pre-fill the Risk Mode checklist (D31).

## 3. Technical inception (D33)
Produce `tech-inception`: affected systems/apps (cross-check `reverse-eng`, D21), integration points, technical constraints, technical risks, feasibility. If reverse-eng is missing/stale → produce/refresh it first (D21), or ASK.

## 4. Requirements questions (gate, D18)
If there is ANY ambiguity, create/append questions in `requirements.md`:
- multiple choice `A) … B) … X) Outro`, with `[Answer]:` per question, in pt-BR.
- STOP and wait for answers (gate). Do not advance.
- When answered, check for contradictions (e.g., "bug" + "afeta tudo") → ask follow-ups.
Depth by lane: FAST few/none (inline) · Standard a set · SAFE comprehensive.

## 5. Propose Risk Mode (D31/D2)
Fill the checklist (mark "inferred" what you could not ground), apply hard overrides, and PROPOSE the mode. In FAST proceed (delegated autonomy); in Standard/SAFE ask the human to confirm. Record in `risk.md`.

## 6. Close the phase
Write `problem` + consolidated `requirements`; update `state`; append `audit`.
**Inception DoD (D25):** problem & objective clear; Risk Mode proposed/confirmed; (Std/SAFE) requirements answered. Present the checkpoint (Request Changes / Approve & Continue) before Design.

## Outputs
`inception-input` (if Produto) · `tech-inception` · `requirements` · `risk` · updated `state`.
