---
name: phase-inception
description: Lifecycle — Inception ("What?")
load: phase
triggers:
  phase: inception
  lane: all
  demand-type: all
  agent: all
---

# Lifecycle — Inception ("What?")

Understand the demand before designing a solution. Owner agent: **Discovery**. Subject to the supreme law and scaled by the active lane.

## Steps
0. **Opening framing checkpoint (new demand)** — before any clone, id stamping,
   state write, or scaffolding, propose target app/source, initiative id, demand
   id, scope, lane, and artifact set; wait for explicit human confirmation.
1. Detect **stream/type** and, if **Produto**, ingest the external `inception-input` — do not redo business discovery.
2. **Intent analysis** — classify clarity (clear/vague/incomplete), type (mapped to streams), scope (1 file → cross-app), complexity. This output **pre-fills the Risk Mode checklist**.
3. Produce **`tech-inception`** (technical lens: affected systems/apps via reverse-eng, integration points, technical risks).
4. Generate **requirements questions** in a file (multiple choice + `[Resposta]:`, see `../../common/question-format.md`) → instruct the human to edit the file and say `pronto`/`terminei` → **gate** awaits answers in the file → detect contradictions. **Alfred never fills the `[Resposta]:` slots** (only the human does, D7); on "continue" the gate stays closed and Alfred never auto-accepts recommended answers to advance. Exception: explicit human delegation → mark answers `assumida` + record in `audit` (see `sub-activities/requirements-elicitation.md`).
5. Pre-fill and **propose Risk Mode** (intent → checklist); human confirms in Standard/SAFE.
6. Consolidate `problem`/`requirements`; record risks; satisfy **DoD Inception** (active lane) → checkpoint.

Each step has concise JIT guidance in `sub-activities/` (`business-inception` / `technical-inception` / `requirements-elicitation` / `risk-mode-proposal`) — load only the rungs the demand triggers. These are sub-activities **inside Inception**, never new phases.

## Two lenses
- **Business** — for Produto, imported from an external agent (`inception-input`). Alfred validates completeness, does not redo it.
- **Technical** — always done by Alfred (`tech-inception`): what is affected, constraints, technical risks, feasibility, technical questions.
For Engineering/Operacional the business lens is minimal — Alfred does both (or only the technical).

## Outputs
problem statement · objective · scope/out-of-scope · initial risks · **proposed Risk Mode** · stream/type · consolidated `requirements`.

## Human roles
PM (scope/value), Domain Expert (context). Sponsor only in SAFE.

## Checkpoint
Confirm the opening framing before creating a new demand. Later, confirm Risk
Mode (Std/SAFE); confirm scope again for SAFE.

## Depth by mode
FAST = 1 paragraph in the state · Standard = problem statement + risks · SAFE = + stakeholders + risk analysis.

## Avoid bureaucracy
If FAST and the problem is clear, Inception is just recording the intent and moving on.
