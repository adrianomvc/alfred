# Templates

Framework-owned molds for generated artifacts. Structure — headings, table
columns, field labels — is **English** (D47); the **content Alfred generates
into them (answers, prose, interactions with the human) is pt-BR**. Legacy
artifacts with pt-BR headings remain valid: validators accept both while they
exist.

## Buckets
| Path | Holds | Examples |
|---|---|---|
| `hub/` | HUB artifacts (per sigla/initiative/demand) | `state.md`, `decisions.md`, `metrics.md`, `summary.md`, `risk.md` |
| `app/` | App artifacts (per repo the demand touches) | `reverse-eng.md`, `spec.md`, `audit.md`, `investigation.md` |
| root | **cross-cutting** templates that are neither a HUB nor an App artifact | `email.md` (notification body, owned by the `notification` connector) |

A template belongs in the root only when it is not produced inside a demand's
HUB/App tree. Today that is just the notification email body; if a second
cross-cutting template appears, group them in a named bucket then.

## Artifact → template map (manual fallback)
When creating an artifact by hand (no CLI), copy from exactly these molds —
never guess a template path (agents have hallucinated a nonexistent
"templates/demand" folder before; only `hub/`, `app/`, and root exist):

| Demand artifact | Template |
|---|---|
| `001-state.md` | `hub/state.md` |
| `01-inception/002-problem.md` | `hub/problem.md` |
| `01-inception/003-requirements.md` | `hub/draft-requirements.md` (draft) → `hub/requirements.md` (started demand) |
| `01-inception/004-risk.md` | `hub/risk.md` |
| `01-inception/005-tech-inception.md` | `hub/tech-inception.md` |
| `02-design/006-decisions.md` | `hub/decisions.md` |
| `03-execution/012-execution-plan.md` | `hub/execution-plan.md` |
| `04-validate/013-validation-evidence.md` | `hub/validation-evidence.md` |
| `04-validate/014-environment-parameters.md` | `hub/environment-parameters.md` |
| `05-operation/007-audit.md` | `hub/audit.md` |
| `05-operation/008-metrics.md` | `hub/metrics.md` |
| `05-operation/009-summary.md` | `hub/summary.md` |
| `05-operation/010-post-mortem.md` | `hub/post-mortem.md` |
| App `001-index.md` / `02-design/003-spec.md` / ... | `app/index.md` / `app/spec.md` / matching `app/` mold |
