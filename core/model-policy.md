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
| Design | high | xhigh | xhigh; decisions/architecture = max |
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

## Parallel units — isolated subagents
Use Devin's native `explore` profile for read-only research and `general` for an
independent write unit. The built-in general profile inherits the parent model,
so Alfred never promises a cheaper write subagent. Parallel writers require
separate worktrees and serialized integration; without isolation, parallelism is
read-only. Record the profile, model, worktree, and integration owner in audit.

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

**DEVIN CLI concrete map:** `swe-1-6-fast` (cheap) · `adaptive` (common medium work) · `opus` (strong default) · `gpt` (configured strong alternative). Adaptive is a router, not evidence of the effective tier: record the actual model when exposed, otherwise mark it `unconfirmed`. Design, SAFE, and critical operations select an explicit strong family. The DEVIN CLI switches models mid-session with `/model`.

**Cost of switching mid-demand:** changing the model mid-demand **invalidates the prompt cache** (cache is per model), tensioning `rules/common/prompt-caching-policy.md`. So a switch is a deliberate step-level decision — raise a tier for a hard step, then let it settle — not a per-turn habit. Devin's `adaptive` deliberately stays on one model across turns to preserve cache; follow the same principle.

## Mechanism — hybrid (declared + auto-suggestion)
- **Source of truth = declared here** — the Orchestrator obeys it.
- **Auto-suggestion:** Alfred analyzes `metrics` (model × cost × first-time acceptance) and **proposes** policy adjustments. It never applies them alone.
- **Human ratifies:** a change enters only with human approval → a new commit to this file (traceable). Never a silent switch.
- **Declare the switch — two surfaces, two roles:** the **toolbar carries state** (a compact flag: the running model, and `(política: <alvo>)` when it diverges). The **chat interaction line carries the action**, emitted at the phase transition (not permanently in the toolbar): a one-line pt-BR advisory that names the target and invites the switch — e.g. *"Esta etapa (Design) roda melhor em `claude-opus-4-8` (tier strong, esf xhigh). Você está em `claude-sonnet-5` — use `/model` para alinhar, ou siga assim que registro o modelo real."* `scripts/workflow/resolve-model-policy.py --actual-model <running>` prints this exact line (also in `--json` as `advisory`). When aligned, there is no line. Any actual switch is also an `audit` event.

## Evidence for future changes
Model comparisons must consider the full context: model, effort, phase, lane,
cost, first-pass acceptance, rework, validation result, duration, and
interaction/request count. A cheaper model is not recommended on cost alone.
Insights may propose a pilot, but this policy changes only after a human
decision and explicit commit.

## User override
The person may **set/switch the model at any time** — one step or the whole demand. Alfred respects and records it in `state`/`audit`. If the choice is **below the risk floor** (e.g. cheap model in SAFE), Alfred **warns the trade-off** (does not block — human in control) and records the decision. Raising the tier is free.

## In the toolbar
The toolbar shows the **model actually running** (and effort, when the host exposes it), so the person always knows what is running — never the policy target dressed up as the running model. The resolved target is shown only as guidance: when the running model matches, the line is compact (`model · tier · esf`); when it differs (forced but not switched, or a human override), the line shows the **running** model and flags the target (`running (política: target)`); when the running model is unknown, the target is shown explicitly as `alvo … não confirmado`. Alfred records the running model in the demand `state` (`model:`) or passes it to the toolbar so this stays truthful.

## Applying the policy (runtime)
This file is the source of truth; `scripts/shared/model_policy.py` mirrors its table so the runtime can **apply** it, and `scripts/workflow/resolve-model-policy.py` resolves `{tier, model, effort, task_budget}` for a demand step (`lane`+`phase`). The toolbar renders that resolved model instead of `default`. `scripts/validators/validate-model-policy.py` checks the mirror against this table (floors, tier→model map, key outcomes) so "written" and "applied" cannot drift. Hosts that cannot switch models keep their default and record which ran (D3).
