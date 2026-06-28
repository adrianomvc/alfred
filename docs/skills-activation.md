# Skills Activation

Skills are optional capability packs loaded just in time. They are not always-on knowledge.

## Activation Flow
1. Orchestrator reads the demand `state`, active phase, lane, demand type, and touched repos/files.
2. Orchestrator reads the sigla/app skills registry when present.
3. Candidate skills are selected by trigger.
4. Only sections relevant to the current step are loaded.
5. If skills conflict, precedence applies.

## Precedence
1. Safer or more restrictive rule wins.
2. More specific skill wins over generic skill.
3. Sigla/app policy may add restrictions, but cannot relax org/framework guardrails.
4. Unresolved conflict escalates to the human.

## Example
If a unit changes Python Glue code:
- load `skills/coding-standard.md` as base;
- load `skills/lang-python.md` because Python files are touched;
- use `lang-python` for Python-specific testing and importability rules;
- keep base SOLID guidance where `lang-python` is silent.

If a unit changes Terraform infrastructure:
- load `skills/coding-standard.md` as base;
- load `skills/lang-terraform.md` because Terraform roots/modules are touched;
- use `lang-terraform` for variable, backend, plan, and validation rules;
- record skipped `init`, `validate`, or `plan` commands when credentials or environment parameters are missing.

If a unit changes SQL or data reconciliation logic:
- load `skills/coding-standard.md` as base;
- load `skills/lang-sql.md` because SQL, DDL, or validation queries are touched;
- use `lang-sql` for sensitive-field handling, source-to-target type mapping, joins, watermarks, and reconciliation evidence;
- record skipped source/target checks when database access or credentials are missing.

If a unit changes AWS data-platform components:
- load `skills/coding-standard.md` as base;
- load `skills/platform-aws-data.md` because Glue, DMS, S3, Glue Catalog, Lake Formation, Step Functions, IAM, or CloudWatch are touched;
- also load `lang-python`, `lang-sql`, or `lang-terraform` when the unit touches those artifact types;
- use `platform-aws-data` for cross-service concerns: permissions, orchestration, data classification, CDC behavior, observability, and AWS validation evidence.

## Audit
When a skill materially changes the implementation or review plan, record:
- skill name;
- trigger;
- sections loaded;
- decision or rule applied;
- output artifact affected.
