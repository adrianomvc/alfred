# Framework Validation

Use this checklist after changing Alfred itself.

## Static Checks
- `rg --files` lists expected framework areas.
- No generated HUB/App demand data is added under `core/`, `rules/`, `skills/`, `connectors/`, `metrics/`, or `templates/`.
- Framework files remain in English.
- Generated example artifacts may be in pt-BR.
- Templates keep framework labels in English and generated-content instruction in pt-BR.

## Required Structure
- `core/`
- `rules/common/`
- `rules/demand-types/`
- `rules/lanes/`
- `rules/lifecycle/`
- `rules/agents/`
- `skills/`
- `connectors/`
- `metrics/`
- `templates/hub/`
- `templates/app/`
- `docs/`
- `examples/`

## One-shot Validation
Run all structure, JSONL, and behavioral sub-checks at once. Python is the
canonical gate:

```bash
python scripts/python/validators/validate-framework.py
```

## Example Validation Tiers
- `validate-framework` is the required framework gate. It validates examples as framework fixtures, including JSONL, links, generated outputs, toolbar states, connector behavior, and declared strict regression fixtures wired into the validator.
- `validate-demand --strict` is required only for examples explicitly declared as strict regression fixtures in `examples/README.md`.
- Historical or illustrative demand snapshots are not kept in-tree. Migrate them to strict regression fixtures or extract narrow behavior into small fixtures such as `examples/toolbar-states/`.

## JSONL Checks
Run a JSON parse over all observability logs in examples and active pilots.

Python:
```bash
python scripts/python/validators/validate-framework.py
```

## Link/Path Checks
- Demand root keeps only `001-state.md` in HUB examples.
- App demand root keeps only `001-index.md` in app examples.
- HUB artifacts use phase folders:
  - `01-inception/`
  - `02-design/`
  - `03-execution/`
  - `04-validate/`
  - `05-operation/`
- App artifacts use the same phase folders.

## Behavioral Checks
- Risk Mode still has FAST, Standard, SAFE.
- Execution-first still requires post-mortem before close.
- `rules/common/overconfidence.md` still requires grounding before action.
- `rules/common/escalation-triggers.md` stops hard-trigger cases.
- `rules/common/units.md` keeps units inside one demand state.
- `rules/common/question-format.md` keeps pt-BR `[Resposta]:` with 2-5 options.
- `rules/common/terminal-token-policy.md` keeps terminal output bounded and RTK optional/degradable.
- `rules/common/prompt-caching-policy.md` keeps stable framework context before volatile demand context without requiring host-specific caching.
- `rules/common/tool-discovery-policy.md` keeps tool/skill/adapter discovery JIT and avoids loading all tool schemas at boot.
- `rules/common/context-compression-policy.md` keeps RAG/compressed context as a selector only; original sources remain required for editing, decisions, and validation evidence.
- `rules/common/token-budget-policy.md` requires a preflight context budget before large loads or token-heavy steps.
- `rules/common/deferred-work-policy.md` keeps batch/flex/background work off the critical path and out of final decision authority.
- `core/hooks/rtk.md` scopes automatic RTK setup to DEVIN CLI until another host explicitly supports it.
- `docs/version-adoption.md` keeps active-demand framework upgrades explicit and human-approved.
- `docs/release-governance.md` and `CHANGELOG.md` record release intent and compatibility notes.
- `docs/adapter-implementation.md` keeps concrete host adapters explicit, auditable, and degradable.
- `validate-connectors` checks connector contracts and adapter-shaped examples.
- `validate-email-adapter` checks the Python-only notification adapter dry-run, allowlist refusal, and audit JSONL.
- `validate-tool-discovery-policy` checks the JIT tool policy, host shims, connector guidance, and MCP tool description size.
- `validate-context-compression-policy` checks that compression guardrails stay wired into boot, Design, Execution, and Validate.
- `validate-token-economy-policy` checks token-budget and deferred-work guardrails.
- `validate-model-policy` checks lane floors, tier map, adjustments, override warning, and toolbar transparency.
- `validate-links` checks that internal Markdown references (links and inline framework paths) still resolve after moves/renames.
- The architecture SOLID **extension checklist** in `core/architecture.md` passes for any added/moved module, file, or artifact (one reason to change; extend by adding; substitutable via contract; loads only what it needs; depends on a role, not a concrete).

## Acceptance
A framework change is acceptable when:
- the changed rule/template has a clear owner module;
- the architecture SOLID extension checklist (`core/architecture.md`) passes for added/moved files;
- examples or docs reflect the new convention;
- JSONL examples still parse;
- connector contracts and adapter examples pass validation;
- model policy validation passes;
- no instruction conflicts with markdown-first agnostic operation;
- remaining gaps are recorded in `docs/implementation-status.md`.
- release-relevant changes are recorded in `CHANGELOG.md`.
