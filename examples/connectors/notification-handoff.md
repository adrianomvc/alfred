# Notification Handoff Example

Connector contract: `connectors/notification-email.md`

## Context
- trigger: checkpoint or demand close
- destination source: `knowledge/notification.md`
- content: pointers, not full pasted artifacts

## Handoff
```markdown
## Notification
- subject: `[Alfred-Framework][SQ9][005-parallel-units] Checkpoint Validate`
- to: configured in knowledge
- attachments:
  - `001-state.md`
  - `05-operation/007-audit.md`
  - `05-operation/008-metrics.md`
  - `04-validate/013-validation-evidence.md`
- body: short summary + links
```

## Degradation
If no email connector is configured, Alfred records a manual reminder in `audit` and shows the subject/attachments to the human.

