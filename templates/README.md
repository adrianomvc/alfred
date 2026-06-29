# Templates

Framework-owned molds for generated artifacts. The label/instructions are in
English (D47); the **content Alfred generates from them is pt-BR**.

## Buckets
| Path | Holds | Examples |
|---|---|---|
| `hub/` | HUB artifacts (per sigla/initiative/demand) | `state.md`, `decisions.md`, `metrics.md`, `summary.md`, `risk.md` |
| `app/` | App artifacts (per repo the demand touches) | `reverse-eng.md`, `spec.md`, `audit.md`, `investigation.md` |
| root | **cross-cutting** templates that are neither a HUB nor an App artifact | `email.md` (notification body, owned by the `notification` connector) |

A template belongs in the root only when it is not produced inside a demand's
HUB/App tree. Today that is just the notification email body; if a second
cross-cutting template appears, group them in a named bucket then.
