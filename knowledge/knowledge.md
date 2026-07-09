# Knowledge Registry

Company knowledge is loaded by scope and event. This registry tells agents which policy file to load without reading the whole folder.

## Registry
| Policy | Scope | Trigger | Link |
|---|---|---|---|
| `policy-template` | template | creating or changing a policy file | [policy-template.md](policy-template.md) |
| `notification` | org | demand completion, checkpoint notification, escalation, incident stabilization, periodic status, or telemetry batch | [notification.md](notification.md) |
| `external-catalogs` | org | skill or documentation discovery from an external catalog | [external-catalogs.md](external-catalogs.md) |

## Rule
Load only the policy whose trigger matches the active event. Sigla/HUB and demand knowledge may harden these policies, but must not weaken company policy without an explicit human exception in the audit.
