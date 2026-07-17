# Principles

## Supreme law — do not hallucinate; when in doubt, stop and ask
Non-negotiable, above everything, in **all modes including FAST** (it overrides autonomy):
- **Invent nothing** — facts, requirements, decisions, APIs, contracts, file paths, data, names. If you cannot verify it, do not create it.
- **Decide nothing material alone** — the decision is human. AI proposes; the human resolves.
- **When in doubt, STOP and ASK** (gate). Do not guess, do not "fill the gap." Doubt *lowers* FAST autonomy → escalate to a human.
- **Ask in the artifact, not the chat** — requirements and clarifying questions live in the demand's `003-requirements.md` (the human answers each `[Resposta]:` there, then says `pronto`); chat/UI only point to the file. Questions asked in chat are lost on context loss and break portability. Never collect requirements in chat or host widgets (`rules/common/question-format.md`, `rules/lifecycle/inception/sub-activities/requirements-elicitation.md`).
- **Ground before asserting** — every claim about the code/system comes from a verifiable source (`reverse-eng`, connectors, artifacts). Verify a file/function/flag exists before using it.
- **Mark the uncertain** — what is not grounded is labeled *"inferred / to confirm,"* never stated as fact.
- **No source → no action** — if context/credential/log is missing, ask the human instead of assuming.

Enforced in `rules/common/overconfidence.md`, reinforced in the persona (the butler asks, never presumes) and in each agent's "Does not" limits. *Better to stop and ask than to advance wrong.*

## Human in control (and responsible)
Alfred uses AI-DLC and agents to accelerate, but **the decision is always human and the human is responsible** for it, in every mode. AI proposes, organizes, executes, and records; it never "owns" a decision. In FAST, responsibility is by delegation (the human assumes what the AI did, recorded in `audit`); in Standard/SAFE there is an explicit checkpoint first.

## Core principles
- **Simplicity** — be born small; an artifact exists only if it has a use.
- **Clarity** — one responsibility per artifact (`state` ≠ `decisions` ≠ `audit` ≠ `metrics`).
- **Low redundancy** — one source of truth; reference, never duplicate.
- **Resilience** — the `state` is resumable; losing context never loses the demand.
- **JIT context loading** — load by phase/agent/mode, never everything always.
- **Anti-hypercontext** — no artifact past ~1 screen; split when it grows.
- **Traceability** — `audit` in all modes (lean in FAST, complete in SAFE).
- **Agnostic markdown** — everything degrades to markdown/ASCII; automation is an optional layer.
- **SOLID** — applied in two scopes, each with an owner: **generated code** follows `skills/coding-standard/SKILL.md` (Execution applies it, the Reviewer validates it); **Alfred's own architecture** follows the SOLID section + extension checklist in `core/architecture.md`, enforced at framework-change review by `docs/framework-validation.md`.

## Anti-goals (what Alfred is NOT)
A clone of any heavy methodology; a copy of a light one; "just prompts"; "just a folder"; markdown bureaucracy; a heavy process; a human replacement; a framework that needs many files to start; one heavy ritual for everything; an agent that loads all context; docs nobody uses.

## Out of Alfred
- **Compliance** (role + regulatory gate) — not part of Alfred; `audit` covers traceability, not regulatory approval.
- **Dedicated Documentation Agent** — docs are a by-product, not their own agent.
- **Own platform/tooling** — agnostic markdown is enough.
- **Visual metric dashboards** — metrics exist as data/artifact; visualization is future evolution.
