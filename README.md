# Alfred Framework

Alfred is a markdown-first framework for hybrid squads (humans + AI agents). It adapts process depth by **risk and complexity**, not preference.

## Implementation status
Layer 1 of the framework is operational for pilots and real demands, and the SQ9 HUB/App adoption path has been exercised with a real multi-repo demand. It is not a full hosted product: host adapters, credentials, real environment parameters, and organization-specific policy remain external. Track closure and remaining gaps in [`docs/layer-1-framework-closure.md`](docs/layer-1-framework-closure.md) and [`docs/implementation-status.md`](docs/implementation-status.md).

## Core idea
- **AI-DLC backbone:** Inception -> Design -> Execution -> Validate -> Operation.
- **SDD clarity brake:** relevant work needs a clear problem, acceptance criteria, risks, and decisions.
- **Risk Mode:** FAST, Standard, or SAFE sets depth, artifacts, checkpoints, and model floor.
- **Human in control:** AI proposes, organizes, executes, and records; humans decide.
- **JIT context:** load only the current phase, lane, demand type, and active specialty.

![Fluxo do Alfred: as 5 fases (Inception, Design, Execution, Validate, Operation) e os modos de risco FAST, Standard e SAFE](docs/assets/alfred-fluxo.svg)

> In the terminal the same flow renders as plain ASCII (see [`core/welcome.md`](core/welcome.md)); richer profiles are optional layers over one source — see [`core/presentation.md`](core/presentation.md).

## Repository map
- `core/` - principles, architecture, boot, risk mode, model policy, glossary.
- `rules/` - lifecycle, lanes, demand types, common rules, and agents.
- `templates/` - framework-owned templates for generated HUB/App artifacts.
- `skills/` - optional specialty packs and coding standards.
- `connectors/` - plug-in contracts for VCS, tracker, notification, telemetry, observability.
- `metrics/` - measurement contract, baselines, and insight rules.
- `knowledge/` - org-level defaults and policy hooks.
- `docs/` and `examples/` - adoption guidance and minimal examples.

## Operating rule
The framework is referenced by HUB and App repos; it is not copied into them. Generated artifacts live under `alfred-docs-hub` (HUB) and `.alfred-docs-app` (App) and are written in pt-BR. Framework files stay in English.
