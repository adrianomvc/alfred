# Principles & anti-goals

> Framework files in English (D47). Interactions and generated artifacts are pt-BR.

## Supreme law — anti-hallucination (D41)
- **Never invent**: facts, requirements, decisions, APIs, contracts, file paths, data, names.
- **On any doubt: STOP and ASK.** Do not guess, do not fill gaps. Doubt lowers FAST autonomy → escalate (D27).
- **Ground before asserting**: verify in reverse-eng (D21), connectors, or artifacts before stating anything about the system.
- **Mark the uncertain** as "inferred / to confirm" (D31). Explicit assumption > silent invention.
- **No source → no action**: missing context/credential/log → ask the human.

## Principles
1. **Human in control & accountable in every mode** (D7). AI proposes; the human decides.
2. **Markdown-agnostic, host-portable**; everything degrades to plain markdown/ASCII (D3).
3. **Process by risk & complexity, not preference** — Risk Mode (FAST/Standard/SAFE).
4. **SDD clarity gate**: no Execution without the Design DoD of the mode met (D29).
5. **JIT context loading**: load only what is needed; index → state → relevant links (D11).
6. **Anti-hypercontext**: ~1 screen per file; split when it grows; reference, never duplicate.
7. **Resilience**: resume from `state` at any time (D16/D28/D37).
8. **Traceability**: audit in all modes; version stamps (D26).
9. **SOLID in the framework itself** (D40).

## Anti-goals (what Alfred is NOT)
- Not a SAFE clone; not pure FAST; not just prompts; not just folders.
- Not markdown bureaucracy; not one heavy rite for everything.
- Not a human replacement; not "many files to start"; not agents loading all context.
- Not docs nobody uses.
