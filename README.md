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

> In the terminal the same flow renders as plain ASCII (see [`core/welcome.md`](core/welcome.md)); richer profiles are optional layers over one source — see [`core/presentation/`](core/presentation/README.md).

## Repository map
One responsibility per folder — the mental model: **`core/` = what Alfred is · `rules/` = how it works · `knowledge/` = what the company mandates · `skills/` = what it knows (opt-in) · `connectors/` = what it reaches (contracts) · `scripts/` = what it automates (optional) · `templates/` = what it produces · `hosts/`+`install/` = where it runs · `docs/`+`examples/` = how to learn and verify.**

- `core/` - principles, architecture, boot, risk mode, squad, model policy, glossary.
- `rules/` - lifecycle, lanes, demand types, common rules, and agents.
- `knowledge/` - the company-wide rules and values every squad inherits (notification/telemetry destinations, catalog allowlist, policies).
- `skills/` - optional specialty packs and coding standards.
- `connectors/` - plug-in contracts for VCS, tracker, notification, telemetry, observability (+ the MCP e-mail adapter in `scripts/python/adapters/`).
- `metrics/` - measurement contract, baselines, and insight rules.
- `templates/` - framework-owned molds for generated HUB/App artifacts.
- `scripts/` - optional helpers in two runtimes, by category: `validators/` · `workflow/` · `metrics/` · `adapters/`.
- `hosts/` - per-host entry points (DEVIN CLI, Claude Code, Copilot, Codex); sources live here, installation lands in each host's native location.
- `install/` - turn-key installer (framework + skill + e-mail/telemetry + MCP).
- `docs/` and `examples/` - adoption guidance and the example suite (also the regression evals).

## Where to start
- **I want to USE Alfred in my squad** → run `install/` and read [`docs/onboarding-sigla.md`](docs/onboarding-sigla.md), then [`docs/quickstart-real-demand.md`](docs/quickstart-real-demand.md).
- **I want to UNDERSTAND how it works** → [`core/README.md`](core/README.md) → [`core/risk-mode.md`](core/risk-mode.md) → [`rules/README.md`](rules/README.md).
- **I want to CHANGE the framework** → [`AGENTS.md`](AGENTS.md) (invariants + validation) and [`docs/plan/implementation-plan-2.0.0.md`](docs/plan/implementation-plan-2.0.0.md) (active plan).

## Operating rule
The framework is referenced by HUB and App repos; it is not copied into them. Generated artifacts live under `alfred-docs-hub` (HUB) and `.alfred-docs-app` (App) and are written in pt-BR. Framework files stay in English.
