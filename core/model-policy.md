# Model policy — model routing per step

Alfred **defines which model to use per step** and may **switch during execution** (the Orchestrator chooses per step). This file is the **source of truth** — declared, versioned, transparent: you always know which model runs in each step.

## Selection rule — risk (floor) + step (adjustment)
The key is composite: **lane (risk/mode) + phase + agent + type**.
- **Risk (lane) sets a FLOOR** — the minimum model tier.
- **Phase/agent adjusts ABOVE the floor, never below.**
- Conflict between dimensions → **the highest wins** (safety > economy).

Final resolution = `max(risk floor, step adjustment)`.

Each step carries **two axes**: the **tier** (which model — this section) and the **effort** (how deeply it reasons — see *Effort per step*). Both are host-optional and degrade to the host default (D3), always recorded in `audit`.

## Floor per lane (risk) — do not go below
| Lane | Minimum tier |
|------|--------------|
| FAST | cheap |
| Standard | medium |
| SAFE | strong |

## Adjustment per step (rises above the floor, never below)
| Phase / agent / type | Adjustment |
|----------------------|------------|
| Inception | FAST=strong (no Design gate — compensate), Standard=medium, SAFE=strong (floor) |
| Design · spec-design (all lanes) | strong (always — solution shaping/SDD sets the whole build; supersedes the old +1 tier) |
| Execution (incl. boilerplate) | lane floor, minimum medium — never runs on `cheap` |
| Validate · reviewer | lane floor, minimum medium (never `cheap`); +1 if risk |
| Operate | lane floor, but may drop to `medium` even in SAFE (see note) |
| Decisions / architecture (SAFE) | strongest |

> **Design** is **pinned to `strong` on every lane** (owner decision, 2026-07-09) — solution shaping/SDD sets the whole build. **Inception** is lane-specific: **FAST=`strong`** (FAST has no Design gate, so its Inception carries more weight and is compensated up), **Standard=`medium`** (Design catches issues downstream), **SAFE=`strong`** (floor). The `effort` axis carries the depth on the `medium` steps.
>
> Execution and Validate never drop below `medium` (owner decision, 2026-07-09): they write/inspect code, so `cheap` would be the least-supervised, highest-risk spot. `cheap` (Haiku) therefore remains only for **FAST Operate**.
>
> **Operate — the one exception to the floor** (owner decision, 2026-07-09): Operate may run on `medium` even in **SAFE**. It is mechanical summarization/rollup/notification of already-decided content, not new reasoning, so it does not require the SAFE `strong` floor. Every other SAFE step stays `strong`.

## Effort per step (depth of reasoning — second axis, host-optional)
Effort is the **second axis**: it controls how deeply the model reasons and how many tokens it spends, and on recent models it is often more impactful than the model choice itself. Alfred sets it per step, alongside the tier. Levels: `low` / `medium` / `high` / `xhigh` / `max`.

| Phase | FAST | Standard | SAFE |
|-------|------|----------|------|
| Inception | high | high | xhigh |
| Design | folds into Execution | xhigh | xhigh; decisions/architecture = max |
| Execution | medium | high | xhigh |
| Validate | medium | high | xhigh |
| Operate | low | low | medium |

Principles applied:
- **Front-load reasoning where the error is costliest** — Inception/Design run high→max; a mistake there propagates through the whole build.
- **Execution starts at `high`, not `xhigh`** — higher effort up front tends to cut turn count and total cost on agentic work; raise per route only if a step under-reasons. Bound the loop with a task budget (below).
- **Validate reports everything, filters downstream** — the reviewer runs at high/xhigh and surfaces every finding with confidence + severity; a later step ranks them. Never pair high effort with a "only high-severity" instruction — it depresses recall.
- **Operate is not intelligence-sensitive** — summaries/notifications run at `low` for latency and cost.

Degradation (D3): a host without an effort control ignores this axis, runs its default, and records the actual setting in `audit`.

## Task budget on Execution (bound the agentic loop)
Execution is the token-heavy, agentic step. When the host supports it, cap the cumulative loop with a **task budget** (min 20,000 tokens) so the model paces itself and finishes gracefully — distinct from any hard per-response cap the model is unaware of. Standard/SAFE benefit most. Degrades: a host without task budgets runs without one and records the actual spend.

## Parallel units — cheaper subagents
When Design decomposes Execution into **independent, parallelizable units**, a unit that is low-risk on its own may run on the **lane floor tier via a subagent**, keeping the main Execution loop on the step tier. This delegates sub-tasks to a cheaper model without invalidating the main context. A unit's tier never exceeds the demand's lane, and never drops below the Execution `medium` floor; if unsure, keep the unit at the step tier. Record the split in `audit`.

## Deferred work — cheaper latency trade-off
If the host exposes batch, flex, background, queued, or low-priority execution,
Alfred may use it only for non-critical-path work: metrics rollups, usage
normalization, broad read-only scans, stale reverse-engineering refreshes,
non-urgent summaries, notifications, and follow-up grouping. Load
`rules/common/deferred-work-policy.md` first. Deferred output is never final
authority for Design, SAFE decisions, incident stabilization, code edits, merge
decisions, or validation judgment.

## Tier → real model (per host)
The policy uses **abstract tiers** (`cheap` / `medium` / `strong`); this map translates to the concrete model of each host — the main customization point. If the host lacks the tier, fall back (degrade). Any cell may be a **tier** (portable) **or a fixed model** (e.g. `claude-opus-4-8`); for a fixed model, Alfred derives its tier (reverse map) only to check the risk floor.

| Tier | Concrete model (Claude host) |
|------|------------------------------|
| cheap | `claude-haiku-4-5` |
| medium | `claude-sonnet-5` |
| strong | `claude-opus-4-8` |

> Proposed default for a Claude host (owner decision, 2026-07-09); other hosts remap on adoption — any cell may be a portable tier or a fixed model. Agnostic: if the host cannot switch models, use the default and **record which model ran** — the policy becomes a recommendation.

## Mechanism — hybrid (declared + auto-suggestion)
- **Source of truth = declared here** — the Orchestrator obeys it.
- **Auto-suggestion:** Alfred analyzes `metrics` (model × cost × first-time acceptance) and **proposes** policy adjustments. It never applies them alone.
- **Human ratifies:** a change enters only with human approval → a new commit to this file (traceable). Never a silent switch.
- **Declare the switch:** whenever the model changes between steps, Alfred **tells the person** (toolbar/interaction line, pt-BR), e.g. *"Mudando para <modelo> nesta etapa (Design/SAFE)."* The switch is also an `audit` event.

## User override
The person may **set/switch the model at any time** — one step or the whole demand. Alfred respects and records it in `state`/`audit`. If the choice is **below the risk floor** (e.g. cheap model in SAFE), Alfred **warns the trade-off** (does not block — human in control) and records the decision. Raising the tier is free.

## In the toolbar
The toolbar shows the **current model** (and effort, when the host exposes it) of the step, so the person always knows what is running.
