# Common Rule - Escalation Triggers

Escalation protects the human decision boundary. It applies in all lanes. FAST can move quickly, but it still stops when a hard trigger fires.

## Hard Triggers
Stop and ask the responsible human when any of these occur:
- scope changes after Inception;
- a new repo, system, provider, or data domain enters the demand;
- sensitive data is discovered or classification changes;
- rollback is unclear for an irreversible or hard-to-reverse action;
- a required connector/credential/log is missing and cannot be inferred safely;
- validation fails twice for the same reason;
- a unit wants to write outside its declared write scope;
- model/user instruction conflicts with the lane floor or safety policy;
- the agent would need to invent an API, schema, path, policy, or business rule;
- a protected branch merge, release, or production action is required.

## Soft Triggers
Record and consider escalation when:
- cost/tokens grow beyond the baseline;
- SAFE share is unusually high for the sigla;
- the same question repeats across demands;
- cycle time exceeds the lane baseline;
- a dependency blocks progress for more than one session.

## Output
When escalating, update:
- `001-state.md`: status, blocker, next step, checkpoint owner;
- `05-operation/007-audit.md`: what triggered escalation and who owns it;
- observability JSONL: `event_type: "escalation_triggered"`;
- `02-design/006-decisions.md` if a human decision changes scope, risk, or architecture.

## Degradation
If the host cannot notify the human automatically, Alfred records the escalation and says plainly what decision is needed.

