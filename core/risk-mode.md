# Risk Mode (D2/D31)

Risk Mode selects the **lane** (governance level) per demand: FAST / Standard / SAFE.
Rule: **risk ≠ complexity** (two axes); the **higher axis sets the floor**.
AI proposes, human confirms (FAST proceeds by delegated autonomy; Std/SAFE confirmed). D2.10.

## Checklist (0/1/2 each; sum per axis, 0–10)
### Risk (consequence if it goes wrong)
| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Reversibility | trivial | reversible w/ effort | hard/irreversible |
| Blast radius | local | 1 system/squad | multi-system/squad |
| Sensitive/regulated data | none | light PII | regulated/sensitive |
| Customer impact | internal | indirect | direct in production |
| Cost / financial risk | low | medium | high |

### Complexity (difficulty to do right)
| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Components affected | 1 | few | many |
| Technical novelty | known | partial | new |
| Requirement ambiguity | clear | some | vague |
| Integrations | none | 1 | several/external |
| Estimated effort | hours | days | weeks |

## Score → lane (take the higher of the two sums)
- 0–3 → **FAST** · 4–6 → **Standard** · 7–10 → **SAFE**

## Hard overrides (force mode up, regardless of score)
- Any risk=2 in *sensitive/regulated* OR *irreversible* OR *direct customer impact* → **min Standard; if 2+, SAFE**.
- Architectural change or multi-squad → **SAFE**.

## Anti-degeneration
- **Anti-SAFE:** SAFE requires explicit justification in `decisions`; review if >~25% of demands are SAFE (D32).
- **Anti-FAST-for-critical:** hard overrides + mandatory reclassification on trigger.
- **Emergency:** governance still applies; only order/timing compress (Execution-first, D6).

## Per-app override (D2.11)
Demand has a **base mode**; a specific app may **rise** (never fall). Record in `risk.md` with justification.

## Reclassification
Initial in Inception, revalidated in Design. Rises on any override trigger (AI must pause/escalate). Lowering requires human approval. Every change logged in `decisions`.

## Inputs from intent analysis (D31)
Scope→components/blast; complexity→novelty/effort; clarity→ambiguity; type→override hints; data/customer→hard overrides. AI pre-fills, marks "inferred", proposes the mode.
