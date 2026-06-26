# Skills registry + contract — operational prompt (D12/D22/E-2)

Skill = pluggable CAPABILITY/knowledge. NOT a policy (that is `knowledge/`, always-in-force) and NOT access (that is `connectors/`).
Opt-in and loaded JIT: load only ACTIVE skills, and only the relevant SECTION of each (D11).

## How the Orchestrator uses this
1. At demand start, read this registry; propose the skills whose `trigger` matches (stream/type · mode · phase).
2. The human confirms activation; record active skills in the HUB `skills.md`.
3. The phase agent loads only the active skill(s), only the needed section. External skills: resolve the pointer (repo/URL) on activation; read only the needed part.
4. At close, the `summary` records which skills were used.

## Contract (each skill file declares)
name · purpose · trigger · inputs · expected output · link · sections (for internal JIT).

## Precedence on conflict (D22)
1. more restrictive/safer wins · 2. more specific (app/sigla) > generic (framework) · 3. tie → human decides (logged in `decisions`/`audit`).

## Registry
| Skill | Purpose | Trigger |
|---|---|---|
| coding-standard | SOLID + good practices (base) | Execution/Validation (all) |
| lang-<language> | language standard (overrides base) | Execution in that language |
| security-review | security review | security / SAFE / sensitive data |
| <external> | pointer to another repo | per its trigger |
