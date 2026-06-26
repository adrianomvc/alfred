# Lane: FAST — operational prompt (D2/D7/D25/D27)

When Risk Mode = FAST, APPLY this. Low risk & complexity → speed and flow.

## Autonomy
Delegated autonomy: proceed WITHOUT per-step human confirmation; the human remains accountable, recorded in `audit` (D7). Immediately STOP and ask on any escalation trigger (D27): scope grew · risk rose · cost over cap · destructive/irreversible op · security · ambiguity · cross-app · repeated failure.

## Per-phase behavior (compressed, never skipped)
- Inception: 1 paragraph (problem+objective); requirements inline, few/no questions.
- Design: inline (spec = the PR; no separate spec file).
- Execution: implement; small PR; self-review; lean `audit`.
- Validation: relevant local tests pass.
- Operation: closes on merge; note optional.

## Artifacts (minimum)
`state` + lean `audit` + PR. No formal spec/decisions.

## DoD (gate)
problem/objective clear · tests pass · PR merged (human merge = acceptance, D23).

## Toolbar (one line, still shows cost+model — D10/D46)
ALFRED · id · FAST · fase (x/5) · falta: ... · modelo: m · ~US$ c

## If unsure it is really FAST
Re-run the checklist; if any hard override applies → raise the mode and re-confirm. Never keep a critical change in FAST.
