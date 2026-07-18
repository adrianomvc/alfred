---
name: common-verification-loop
description: Executable verification, fresh review, and context recovery
load: event
triggers:
  phase: execution
  lane: all
  demand-type: all
  agent: all
---

# Common Rule - Verification Loop

Before a unit starts, record its executable verification command, expected
success signal, evidence path, and reviewer requirement. A unit is not complete
because it looks plausible; run the verification, inspect its result, and fix the
cause rather than suppressing the signal.

FAST requires deterministic verification and adds independent review when a risk
trigger fires. Standard uses a fresh read-only reviewer. SAFE uses a fresh strong
context and checks acceptance, security, rollback, and the diff against the plan.
Review findings must affect correctness or a declared requirement; style-only
preferences do not block completion.

## Guided-then-strict corrections
Use at most three implementation attempts before replanning:
1. **Guided autonomy:** give the objective, evidence, plan, write scope, and
   verification. The executor reads current source and may adapt implementation
   details, but reports every deviation.
2. **Corrective:** add the failed signal, likely cause, affected files/symbols,
   and explicit constraints. Keep judgment only where current source requires it.
3. **Strict minimal:** name the exact allowed scope and correction. No unrelated
   work. If instructions conflict with current source, acceptance, safety, or a
   SAFE gate, stop instead of following them blindly.

After the third failed attempt, persist the evidence and rejected approaches,
then return to Design/replanning or escalate. Attempts are an Execution
sub-loop, never lifecycle phases.

After two failed correction loops following the guided attempt, restart from a
clean context before replanning. Unrelated demands use separate sessions.
Host-specific goals or stop hooks may enforce the portable verification contract,
but their absence never removes it.
