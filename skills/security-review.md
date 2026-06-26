# Skill: security-review — operational prompt (D12/D22)

ACTIVATE for security demands, SAFE, or changes touching sensitive/regulated data. Opt-in, loaded JIT.
Precedence: more restrictive/safer wins (D22).

## Inputs
The changed code/diff, the `spec`, and any relevant `knowledge` policy (org/sigla).

## Review sections (load only what applies — JIT)
- AuthN/AuthZ: missing checks, broken access control, privilege escalation.
- Input validation: injection (SQL/command/template), deserialization, path traversal.
- Secrets: hardcoded credentials/keys; secrets in logs.
- Dependencies: known-vulnerable libs; unpinned versions.
- Data: PII handling, encryption at rest/in transit, least privilege.

## Output
Findings list, each with: severity (low/med/high/critical) · location (file:line) · recommendation. Write into validation/`audit`. If high/critical → flag as a checkpoint/escalation (D27); do not silently pass.

## Hard rules
- Never weaken a control to "make it pass". Never invent a vuln or a fix — ground it (D41).
- If a security policy in `knowledge` applies, it is mandatory (cannot be relaxed by the squad, D42).
