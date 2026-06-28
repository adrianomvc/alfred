# Git / PR Handoff Example

Connector contract: `connectors/git.md`

## Context
- demand id: `005-parallel-units`
- branch: `alfred/005-parallel-units`
- base branch: `develop`
- merge policy: human only

## Handoff
```markdown
## PR Handoff
- demand: `005-parallel-units`
- branch: `alfred/005-parallel-units`
- base: `develop`
- state: `alfred-docs-hub/iniciativa-001-piloto/005-parallel-units/001-state.md`
- execution plan: `03-execution/012-execution-plan.md`
- validation evidence: `04-validate/013-validation-evidence.md`
- merge owner: Tech Lead
- AI merge allowed: no
```

## Degradation
If the host cannot open a PR, Alfred records this handoff in `05-operation/007-audit.md` and asks the human to open the PR manually.

