# Alfred

**Alfred is the framework that lets a hybrid squad (humans + AI) run every demand at the right level of process — light when risk is low, rigorous when it is high — using AI-DLC as the cycle, SDD as the clarity brake, and Risk Mode as the governance selector.**

> Anchor: *Alfred does not choose process by preference. Alfred chooses process by risk and complexity.*

## What it is
A framework of **adaptive governance + squad operation built on AI-DLC**. It does not replace the coding agent or the lifecycle; for each demand it decides *how much* clarity (SDD), *how many* checkpoints (HITL), *which* artifacts, and *what depth* of each phase to apply. Specialties (discovery, design, spec, review, metrics) are materialized as **interaction artifacts loaded on demand (JIT)**.

It avoids two symmetric failures: **bureaucracy on a simple demand** and **loss of control on a critical one**.

## Pillars
1. **AI-DLC** — the cycle backbone (5 phases: Inception → Design → Execution → Validate → Operation).
2. **SDD** — no relevant delivery starts without an understood problem, a minimal spec, acceptance criteria, risks, and recorded decisions.
3. **Hybrid Squad** — clear human and agent roles; agents are specialty artifacts.
4. **Risk Mode** — adaptive selector (FAST / Standard / SAFE) that regulates depth, artifact, and checkpoint per demand.
5. **HITL** — humans decide what is critical (scope, architecture, risk, cost, security, final acceptance).
6. **JIT Context Loading** — context loaded on demand by phase/agent/mode, never everything always.

## How to use it
The framework is the **single source, referenced — not copied — into HUBs/apps**. Adopting a system (a *sigla*) means: reference this repo, create `alfred-docs-hub`, create `.alfred-docs-app` per app, run reverse-engineering, then run the first demand. See [`boot.md`](boot.md) and `docs/`.

## Map
- [`principles.md`](principles.md) — supreme law (no hallucination), principles, anti-goals.
- [`risk-mode.md`](risk-mode.md) — the selector: checklist, scale, hard overrides. Loaded **JIT at Inception** (via `rules/lifecycle/inception/sub-activities/risk-mode-proposal.md`), not at boot.
- [`architecture.md`](architecture.md) — the 3 layers (Framework / HUB / App).
- [`boot.md`](boot.md) — session start: detect HUB/APP → pull → JIT load.
- [`welcome.md`](welcome.md) — the butler's voice (persona); the rendered screen lives in `presentation/welcome-screen.md` (JIT).
- [`presentation/`](presentation/README.md) — optional rendering layer (profiles · `toolbar-quick.md` · `toolbar.md` · `welcome-screen.md`) over one `state`; degrades to text.
- [`hooks/`](hooks/README.md) — optional deterministic host hooks such as RTK terminal token control; degrades to rules.
- [`squad.md`](squad.md) — human/agent responsibilities and HITL ownership.
- [`model-policy.md`](model-policy.md) — model per phase/agent/lane (tunable). Loaded **only when selecting/switching the model**, not at boot.
- [`glossary.md`](glossary.md) — terminology (sigla / initiative / demand / unit / lane).
- `../rules/` — the customized AI-DLC engine (lanes · demand-types · lifecycle · agents · common).
- `../skills/`, `../connectors/`, `../metrics/`, `../knowledge/`, `../templates/`, `../examples/`.
- `../hosts/` — per-host entry points (DEVIN CLI, Claude Code, Copilot, Codex) that load this framework via each host's native mechanism.

## Operating model
Alfred has **no runtime of its own**. It is markdown instructions/artifacts consumed by host agents (DEVIN CLI/Web, Claude CLI, GitHub Copilot). Everything **degrades to plain markdown/ASCII** — any automation (metrics collection, cost, rich toolbar) is an optional layer. Nothing in the framework may require a specific model, API, CI, or UI.
