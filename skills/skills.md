# Skills Registry

Skills are optional specialty packs loaded just in time. They extend Alfred without changing core rules.

## Required sections per skill
- `name`
- `purpose`
- `trigger`
- `inputs`
- `expected output`
- `link`
- `sections to load`

## Precedence
When skills conflict: safer/more restrictive wins; then more specific wins; unresolved conflict goes to the human.

## Loading
The Orchestrator loads only active skills for the current phase, lane, demand type, and app context.

## Built-in skills
| Skill | Link | Trigger |
|---|---|---|
| `coding-standard` | `skills/coding-standard.md` | default Execution/Validate guidance |
| `lang-python` | `skills/lang-python.md` | Python files, tests, Glue jobs, FastAPI, scripts |
| `lang-sql` | `skills/lang-sql.md` | SQL files, DDL, validation queries, reconciliation, embedded SQL |
| `lang-terraform` | `skills/lang-terraform.md` | Terraform files, IaC modules, providers, variables, outputs, plans |
| `platform-aws-data` | `skills/platform-aws-data.md` | AWS Glue, DMS, S3, Catalog, Lake Formation, Step Functions, IAM, CloudWatch |
| `security-review` | `skills/security-review.md` | security-sensitive changes or SAFE lane |

See `docs/skills-activation.md` for activation and precedence examples.
