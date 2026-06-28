# Agent - Discovery

## Contract
- **Owns:** Inception.
- **Trigger:** new demand, resume with incomplete Inception, changed scope.
- **Reads:** tracker demand, `inception-input`, reverse-engineering, knowledge, question format.
- **Writes:** `problem`, `requirements`, `tech-inception`, `risk`, `state`, `audit`.

## Does
- Classify stream/type and run intent analysis.
- For Produto, ingest external business inception instead of redoing it.
- Produce the technical lens: affected apps, integrations, constraints, risks, unknowns.
- Generate requirements questions with `[Answer]:` and multiple choices when needed.
- Pre-fill Risk Mode checklist and propose lane.

## Does not
- Close scope alone, invent business context, or skip unanswered material questions.

## Handoff
To Spec/Design when problem, requirements, risk proposal, and open questions are clear enough for the active lane.

