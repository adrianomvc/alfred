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

After two failed correction loops on the same problem, save state, record failed
approaches, and restart from a clean context. Unrelated demands use separate
sessions. Host-specific goals or stop hooks may enforce the portable verification
contract, but their absence never removes it.
