# Risk Mode — the governance selector

Risk Mode classifies **risk × complexity** per demand and selects one of three modes. It regulates *depth, artifacts, and checkpoints* — **it never skips a phase**.

## Risk ≠ Complexity (two independent axes)
- **Risk = consequence if it goes wrong** — reversibility, blast radius, security/sensitive data, cost, customer impact, organizational impact.
- **Complexity = difficulty of getting it right** — number of components/systems, technical novelty, requirement ambiguity, effort, integration points, people involved.
- **Rule: the mode is set by the GREATER of the two axes (floor).** "Simple and dangerous" (drop a production table) = high risk → not FAST. "Complex and safe" (broad refactor with tests) can rise by complexity, but with technically-focused governance.

## Checklist (objective; each criterion scores 0/1/2)

**RISK axis**
| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Reversibility | trivial to revert | revertible with effort | hard/irreversible |
| Blast radius | local | 1 system/squad | multi-system/squad |
| Sensitive/regulated data | none | light PII | regulated/sensitive |
| Customer impact | internal | indirect | direct in production |
| Cost / financial risk | low | medium | high |

**COMPLEXITY axis**
| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Components affected | 1 | few | many |
| Technical novelty | known | partial | unprecedented |
| Requirement ambiguity | clear | some doubts | vague |
| Integrations | none | 1 | several/external |
| Estimated effort | hours | days | weeks |

## Score → mode
Take the **greater** of the two sums (0–10 each):
- **0–3 → FAST**
- **4–6 → Standard**
- **7–10 → SAFE**

## Hard overrides (force the mode up, regardless of score)
- Any risk criterion = 2 in *sensitive/regulated data* OR *irreversible* OR *direct customer impact* → **minimum Standard; if 2+ of these, SAFE.**
- Architectural change or multi-squad → **SAFE**.

## Anti-SAFE brake (so not everything becomes SAFE)
- SAFE requires an **explicit justification** in `decisions` (which override/score fired). No justification → drops to Standard.
- Periodic review: if the squad classifies > ~25% as SAFE in a window, it is fear, not risk → revisit criteria (see `../metrics/baselines.md`).

## Decision flow (compact)
The whole classification as one scannable flow (degrades to plain ASCII):

```text
  RISK (0-10) ─┐
               ├─► take the GREATER ─► 0-3 FAST · 4-6 Standard · 7-10 SAFE
  COMPLEX(0-10)┘                                   │
                                                   ▼  hard overrides (force UP, never down)
   sensitive | irreversible | customer-impact = 2 ─► min Standard  (2+ of these ─► SAFE)
   architectural change | multi-squad             ─► SAFE
                                                   │
                                                   ▼
   SAFE chosen? ─► justify in `decisions`  (no justification ─► drop to Standard)
                                                   │
                                                   ▼
   AI proposes ─► human confirms (Standard/SAFE) · delegated autonomy (FAST)
   later: rises any time on a trigger · lowering needs human approval
```

## Time axis (Operational stream)
Risk Mode measures *governance*. For critical Operational (incident/hotfix/rollback) there is an orthogonal axis — **urgency**:
- **Normal** — full cycle at the mode's depth.
- **Emergency** — Execution-first flow (`../rules/demand-types/operacional.md`): stabilize with minimal human authorization; Inception/Design/Validate become a mandatory post-mortem afterward. Risk Mode still applies — only the *order* and *timing* change.
- Golden rule: emergency **never waives** the record; it only **defers** it. No post-mortem, the demand does not close.

## Who classifies — AI proposes, human is responsible
The AI runs the checklist and proposes the mode. In **FAST** it proceeds by delegated autonomy (human responsible, recorded in `audit`). In **Standard/SAFE** a human confirms/adjusts before advancing. Intent analysis (Inception, `rules/lifecycle/inception/`) pre-fills this checklist.

## Reclassification during the cycle
- Mode is **initial in Inception** and **revalidated in Design**.
- It can **rise at any time** if an override trigger appears → the AI **must** pause and escalate.
- **Lowering the mode requires human approval** (governance does not loosen for convenience).
- Every mode change becomes a `decisions` entry with the reason.

## Scope — per demand, override per app
The demand has a **base mode**. When it touches several apps, a specific app may **rise** in its scope (e.g. payment app becomes SAFE inside a Standard demand). The override **only rises**, never falls; each is recorded in `004-risk.md` with justification. The toolbar shows the base mode and flags `app X: SAFE` when elevated.

## What changes per mode → see the lanes
`../rules/lanes/fast.md` · `../rules/lanes/standard.md` · `../rules/lanes/safe.md` carry the DoD per phase, checkpoints, minimal artifacts, and tracking for each mode.
