# Model policy — model routing per step

Alfred **defines which model to use per step** and may **switch during execution** (the Orchestrator chooses per step). This file is the **source of truth** — declared, versioned, transparent: you always know which model runs in each step.

## Selection rule — risk (floor) + step (adjustment)
The key is composite: **lane (risk/mode) + phase + agent + type**.
- **Risk (lane) sets a FLOOR** — the minimum model tier.
- **Phase/agent adjusts ABOVE the floor, never below.**
- Conflict between dimensions → **the highest wins** (safety > economy).

Final resolution = `max(risk floor, step adjustment)`.

## Floor per lane (risk) — do not go below
| Lane | Minimum tier |
|------|--------------|
| FAST | cheap |
| Standard | medium |
| SAFE | strong |

## Adjustment per step (rises above the floor, never below)
| Phase / agent / type | Adjustment |
|----------------------|------------|
| Design · spec-design | +1 tier |
| Execution · boilerplate | keep floor |
| Validate · reviewer | keep / +1 if risk |
| Decisions / architecture (SAFE) | strongest |

## Tier → real model (per host)
The policy uses **abstract tiers** (`cheap` / `medium` / `strong`); this map translates to the concrete model of each host — the main customization point. If the host lacks the tier, fall back (degrade). Any cell may be a **tier** (portable) **or a fixed model** (e.g. `claude-opus-4-8`); for a fixed model, Alfred derives its tier (reverse map) only to check the risk floor.

| Tier | Example (Claude host) |
|------|------------------------|
| cheap | (host's fast/small model) |
| medium | (host's mid model) |
| strong | claude-opus-4-8 |

> Fill this map per host on adoption. Agnostic: if the host cannot switch models, use the default and **record which model ran** — the policy becomes a recommendation.

## Mechanism — hybrid (declared + auto-suggestion)
- **Source of truth = declared here** — the Orchestrator obeys it.
- **Auto-suggestion:** Alfred analyzes `metrics` (model × cost × first-time acceptance) and **proposes** policy adjustments. It never applies them alone.
- **Human ratifies:** a change enters only with human approval → a new commit to this file (traceable). Never a silent switch.
- **Declare the switch:** whenever the model changes between steps, Alfred **tells the person** (toolbar/interaction line, pt-BR), e.g. *"Mudando para <modelo> nesta etapa (Design/SAFE)."* The switch is also an `audit` event.

## User override
The person may **set/switch the model at any time** — one step or the whole demand. Alfred respects and records it in `state`/`audit`. If the choice is **below the risk floor** (e.g. cheap model in SAFE), Alfred **warns the trade-off** (does not block — human in control) and records the decision. Raising the tier is free.

## In the toolbar
The toolbar shows the **current model** of the step, so the person always knows what is running.
