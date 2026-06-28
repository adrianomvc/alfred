# Layer 1 - Framework Closure

This records the practical closure criteria for Alfred Framework Layer 1.

## Current Result
Layer 1 is operational for pilots and real demands.

It is not a full hosted product. It is a markdown-first framework with optional helpers, connector contracts, templates, rules, skills, examples, and validation checks.

## Core Framework
The following are part of the framework core:
- AI-DLC customized lifecycle: Inception, Design, Execution, Validate, Operation.
- Risk Mode: FAST, Standard, SAFE, plus Execution-first for urgent operational work.
- Framework/HUB/App separation.
- Markdown-first artifact model.
- State, audit, decisions, metrics, summary, and JSONL observability contracts.
- Human-in-control and anti-overconfidence rules.
- JIT context loading through indexes, links, active phase, lane, demand type, and skills.
- Demand-to-units decomposition inside one governed demand.
- Skill registry and precedence.
- Connector contracts and degradation rules.
- Templates for HUB and App artifacts.

## Optional Helpers
The scripts under `scripts/` are optional helpers. They make framework rules easier to verify, but Alfred must still work manually through Markdown if scripts cannot run.

Daily-use helpers:
- `alfred-boot.ps1`
- `render-toolbar.ps1`
- `validate-demand.ps1`
- `validate-framework.ps1`

Specialized helpers:
- `validate-sdd-gate.ps1`
- `validate-reverse-eng-staleness.ps1`
- `validate-skills-registry.ps1`
- `validate-toolbar-fixtures.ps1`
- `collect-observability.ps1`
- `generate-metrics-rollup.ps1`
- `normalize-usage-cost.ps1`

## Validated Behaviors
- Framework structure is validated.
- Example JSONL files parse.
- Toolbar fixtures do not drift from the renderer.
- Skills registry entries exist and have required sections.
- Example demand validation checks state, phase folders, SDD gate, audit, metrics, JSONL, active skills, and adapter readiness.
- Reverse-engineering staleness can be checked by recorded app commit.
- Boot can detect context and list resumable demands from `001-state.md`.

## Still External / Not Layer 1 Core
These items are intentionally not closed inside Layer 1 because they need a real host, credentials, or organization-specific policy:
- automatic model/token/cost collection from the host;
- real VCS/PR adapter;
- real tracker adapter;
- real notification/email/Teams/Slack channel;
- real telemetry API or dashboard;
- organization/sigla policies in `knowledge/`;
- real template repositories from the house standard;
- real incident log connector such as CloudWatch, Datadog, or Splunk.

## Exit Criteria
Layer 1 can be considered ready to apply to Layer 2 when:
- `scripts/validate-framework.ps1` passes;
- `docs/implementation-status.md` lists only host/credential/policy-dependent gaps;
- a pilot example passes `validate-demand.ps1 -Strict`;
- README and roadmap point the next step to HUB/App adoption.

## Next Layer
Layer 2 is the SQ9 HUB application:
`D:\Projetos\Teste Alfred\itau-sq9-modules-hub`

Layer 2 should apply the framework conventions to `alfred-docs-hub`, validate real demand artifacts, and prepare synchronization with App repos.

## Adoption Update
The SQ9 HUB/App pilot has exercised Layer 2 and Layer 3 conventions with a real multi-repo demand. Remaining work is not Layer 1 framework closure; it is integrated validation and operation using real environment parameters, credentials, and host adapters supplied by the adopting context.
