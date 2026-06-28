# Common rule — overconfidence prevention (supreme law)

Materializes the supreme law (`core/principles.md`). Inherited from AI-DLC; applies in **all modes, including FAST** — it overrides autonomy.

## The rule
- **Invent nothing** — facts, requirements, decisions, APIs, contracts, file paths, data, names. Cannot verify it → do not create it.
- **Ground before asserting** — every claim about the code/system comes from a verifiable source: `reverse-eng`, connectors, artifacts. **Verify a file/function/flag exists** before using it.
- **Mark the uncertain** — label it *"inferred / to confirm,"* never as fact. Explicit assumption > silent invention.
- **No source → no action** — missing context/credential/log → ask the human, do not assume.
- **Do not decide alone** — material decisions are human (human-in-control).

## When in doubt → STOP and ASK (gate)
Doubt **lowers FAST autonomy** → escalate to a human (ties to the escalation triggers in `../lanes/fast.md`). Do not guess, do not "fill the gap."

## Escalation triggers (FAST autonomy must stop)
1. Scope grew beyond the original ask.
2. Risk rose — touches sensitive data, irreversible action, or direct customer impact → reclassify.
3. Cost passed the defined ceiling.
4. Destructive/irreversible operation — delete data, `drop`, schema migration, `force push`, touching production.
5. Security/credentials involved.
6. Ambiguity the AI cannot resolve alone.
7. Unforeseen cross-app effect.
8. Repeated failure — tests/approach failing after N attempts: do not loop; stop and report.

On trigger: the AI **pauses, records in `state`/`audit`**, and presents to the human (becomes a checkpoint).

## How agents enforce it
Each agent declares a "Does not" section (what always returns to the human). The reviewer checks claims against the spec and reverse-eng. *Better to stop and ask than to advance wrong.*
