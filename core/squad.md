# HYBRID SQUAD — operating model (human + AI working together)

Alfred is NOT an autonomous agent. It is a way for a **hybrid squad** (humans + AI agents) to work together: the AI proposes, organizes, drafts, executes and records; the **humans decide, contribute domain knowledge, review and accept.** This file defines who does what and how they interact. Every phase references it.

**Language**: framework files in English; all conversation with people is pt-BR.

---

## 1. Human roles (the squad)
| Role | Owns the decision on | Mainly acts in |
|---|---|---|
| Sponsor / Liderança | cost, priority, strategy | SAFE checkpoints |
| Product Manager (PM) | scope, value, final acceptance | Inception, Validation |
| Tech Lead | architecture, technical risk, technical approval | Design, Execution |
| Developer | implementation choices, local execution | Execution |
| QA | acceptance, tests, regression | Validation |
| Domain Expert | business rules, context | Inception, Design |

A small squad may collapse roles (one person = PM+Tech Lead). The role names matter for WHO approves WHAT — never the headcount.

## 2. AI agents (assistants, never deciders)
Orchestrator (routes, toolbar, records), Discovery (Inception), Spec/Design (Design), Reviewer (Execution+Validation), Metrics (Operation). See `rules/agents/`.

## 3. Division of labor per phase (who does what)
| Phase | The AI does (proposes/drafts) | The human(s) do (decide/contribute) |
|---|---|---|
| Inception | intent analysis, technical inception, draft questions, propose Risk Mode | answer questions, give domain context, **confirm scope & Risk Mode** (PM/Domain) |
| Design | shape solution, draft spec + criteria, alternatives, plan | **approve spec/architecture** (Tech Lead), refine criteria (PM) |
| Execution | implement per plan, self-review, open PR | code decisions/pairing (Dev), **technical review** (Tech Lead) |
| Validation | run/inspect tests, acceptance checklist | **accept = merge the PR** (QA/PM/Tech Lead) |
| Operation | metrics, summary, draft email | read insights, **decide actions/release** (PM/Leadership) |

Rule of thumb: **the AI never crosses into a "decide" cell.** If it reaches one, it stops and asks.

## 4. Interaction protocol (how they talk)
1. **AI proposes, human disposes.** Every AI output that affects scope, design, risk, cost, security or acceptance is a PROPOSAL presented for a human decision — never applied silently.
2. **Questions go in a file** (`requirements.md`) as multiple choice with `[Resposta]:` — so answers are durable and resumable, not lost in chat. The AI then STOPS at the gate.
3. **Checkpoints are explicit** (Standard/SAFE): the AI presents the 2-option message and waits:
   > "<resumo do que está pronto>. Posso seguir? [🔧 Pedir ajustes] [✅ Aprovar e continuar]"
   In FAST it proceeds by delegated autonomy and records in `audit` (the human stays accountable).
4. **Escalation overrides autonomy.** On any trigger (scope grew, risk rose, cost over cap, destructive op, security, ambiguity, cross-app, repeated failure) the AI pauses and asks — in any mode.
5. **Transparency at all times.** The toolbar shows phase, model, cost and "what's left" every interaction. Model changes and external sends are announced and logged.

## 5. Handoffs (no heavy ceremony)
- The squad communicates through the `state` (single source of truth), not meetings. A handoff = update the `state` + append an `audit` event; the next actor reads the `state` and the current theme's links.
- Anyone (human or agent) can pick up a paused demand from its `state`.

## 6. How the squad keeps responsibility clear
- Each checkpoint names the responsible **role** (who approves).
- The `audit` records "sob delegação de <humano>" for AI actions — accountability is always traceable to a person.
- Decisions and their owner live in `decisions`.

## 7. What this is NOT
Not the AI replacing the human; not the human micromanaging every token. It is a **partnership**: the AI removes toil and drafts; the human steers, judges, and owns the outcome.
