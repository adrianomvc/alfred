# Notification Defaults

## destination
Configured by the adopting sigla/HUB. Do not hardcode personal addresses in framework logic.

## default triggers
- demand completed
- critical checkpoint requiring action
- escalation or Risk Mode change
- incident stabilized
- optional periodic status

## guardrails
Notify only configured destinations and triggers automatically. New destination, unusual content, or sensitive data requires human confirmation and an `audit` entry.

