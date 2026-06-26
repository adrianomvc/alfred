# Lane: Standard — operational prompt (D2/D23/D25)

When Risk Mode = Standard, APPLY this. Balance of speed, clarity, control.

## Checkpoints (HITL)
Two explicit checkpoints: (1) approve the spec at Design->Execution; (2) acceptance = merge of the PR at Validation (D23). Present the 2-option message (Request Changes / Approve & Continue) in pt-BR.

## Per-phase behavior
- Inception: problem statement + scope/out-of-scope + initial risks; requirements gate (D18) with answers.
- Design: spec + acceptance criteria + decisions; execution/test plan; revalidate mode.
- Execution: planning approved -> generation; technical review; units [x]; no unapproved scope growth; commits per step.
- Validation: acceptance criteria OK + regression; PR ready.
- Operation: release notes + basic metrics; summary + index; email at "demanda concluída".

## Artifacts (minimum)
state · spec · decisions · audit · metrics · PR.

## DoD
Per phase as above; advance only when met. Acceptance is the human merge.
