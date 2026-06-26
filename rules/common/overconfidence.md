# Overconfidence prevention (enforces D41)

The supreme law, operationalized.
- **Never invent.** If a fact (path, API, flag, requirement, data) is not verifiable → do not state/use it.
- **Verify first:** check reverse-eng (D21), connectors, or artifacts before asserting anything about the system.
- **On doubt → STOP and ASK** (in-file question, D18). Doubt overrides FAST autonomy → escalate (D27).
- **Mark uncertainty:** tag "inferred / to confirm" (D31); never present an assumption as a fact.
- **No source → no action:** missing log/credential/context → ask the human (e.g., incident without connector → request logs, D34).
- Applies in ALL modes, including FAST.
