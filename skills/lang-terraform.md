---
name: lang-terraform
description: Terraform engineering standard; overrides coding-standard where more specific. Load for Terraform files, IaC modules, providers, variables, outputs, or plans.
---

# Skill - Terraform Standard

## name
`lang-terraform`

## purpose
Terraform-specific engineering standard. It overrides `skills/coding-standard.md` only where it is more specific.

## trigger
Load when the active unit changes Terraform files, IaC modules, provider configuration, variables, outputs, state backends, or deployment plans.

## inputs
- active demand `state`
- app `reverse-eng`
- technical `spec`
- existing Terraform files and modules
- environment variables and tfvars examples when available
- base `skills/coding-standard.md`

## expected output
- Terraform implementation plan
- Terraform review findings
- validation strategy proportional to risk

## link
`skills/lang-terraform.md`

## sections to load
- `rules`
- `validation`
- `review checklist`

## rules
- Keep modules focused on one infrastructure responsibility.
- Prefer explicit variables with descriptions, types, and safe defaults only when defaults are operationally valid.
- Do not hardcode account IDs, regions, bucket names, credentials, ARNs, secrets, or environment-specific values.
- Keep backend configuration and provider credentials outside reusable modules.
- Expose outputs only when another unit, repo, pipeline, or operator needs them.
- Use tags/labels consistently when the target cloud and organization pattern require them.
- Avoid destructive lifecycle changes unless the demand explicitly calls them out and evidence is recorded.
- Treat generated plans as sensitive when they may contain resource names, topology, or secret-adjacent values.

## validation
- Run `terraform fmt -check` for changed Terraform roots when Terraform is available.
- Run `terraform validate` only after `terraform init` has succeeded for that root.
- Run `terraform plan` only when environment parameters, backend access, and credentials are available.
- If real credentials are not available, record the skipped command, missing input, and expected command in validation evidence.
- For multi-repo or multi-root demands, validate each changed root separately.

## review checklist
- variables are typed and documented;
- examples or tfvars templates do not contain real secrets;
- provider/backend boundaries are clear;
- resources use stable names derived from demand/app conventions;
- outputs are intentional and not leaking sensitive values;
- destructive changes are visible in plan evidence or explicitly deferred;
- validation evidence records every root checked or skipped.
