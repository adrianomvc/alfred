# Skills registry + contract (D12/D22/E-2)

Skill = pluggable CAPABILITY/knowledge (≠ knowledge base = always-in-force policy; ≠ connector = access).
Opt-in, loaded JIT (only active skills, only the relevant section).

## Contract (each skill declares)
- `name` · `purpose` · `trigger` (stream/type · mode · phase) · `inputs` · `expected output` · `link` · `sections` (for internal JIT).

## Precedence in conflict (D22)
1. more restrictive/safer wins · 2. more specific (app/sigla) > generic (framework) · 3. tie → human decides (logged).

## Registry
| Skill | Purpose | Trigger |
|---|---|---|
| coding-standard | SOLID + good practices (base) | Execution/Validation (all) |
| lang-<language> | language-specific standard (overrides base) | Execution in that language |
| security-review | security review | security/SAFE |
| (external) | pointer to another repo | per trigger |
