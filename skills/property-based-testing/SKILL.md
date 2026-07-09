---
name: property-based-testing
description: Property-based testing for Validate. Load in SAFE or when units have clear invariants worth checking across generated inputs.
trigger: SAFE lane, or any unit whose logic has clear invariants (parsing, encoding, serialization, math, idempotent/CDC operations, data reconciliation). Opt-in, activated per demand.
sections_to_load:
  - properties: derive invariants from the functional design (round-trip, idempotency, commutativity, bounds, conservation).
  - generators: define input domains/strategies; bias toward edge values.
  - oracle: how to decide pass/fail without re-implementing the logic.
  - shrinking + seed: record the minimal failing case and seed for reproducibility.
  - integration: language-specific tool comes from the active `lang-*` skill; this pack is the agnostic guidance (precedence D22/D36).
---

# Skill - Property-Based Testing

Optional specialty pack for property-based testing. Loaded just in time when the
demand's logic has invariants worth checking across many generated inputs.

## purpose
Strengthen Validate by testing **properties/invariants** over generated inputs,
instead of only example-based cases — surfacing edge cases example tests miss.

## inputs
The unit's functional design (rules, invariants), acceptance criteria, and the
active language skill (D36) for the concrete framework/tooling.

## expected output
A set of properties (invariant + generator strategy) added to the test plan and
exercised in Validate, with shrinking on failure and the failing seed recorded
in the evidence.
