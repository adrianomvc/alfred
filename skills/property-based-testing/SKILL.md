---
name: property-based-testing
description: Property-based testing for Validate. Load in SAFE or when units have clear invariants worth checking across generated inputs.
trigger: SAFE lane, or any unit whose logic has clear invariants (parsing, encoding, serialization, math, idempotent/CDC operations, data reconciliation). Opt-in, activated per demand.
sections_to_load:
  - properties
  - generators
  - oracle
  - shrinking and seed
  - integration
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

## properties
Derive invariants from the functional design: round-trip (encode/decode),
idempotency (applying twice = once), commutativity/associativity where claimed,
bounds/ranges, and conservation (nothing lost or duplicated in reconciliation).

## generators
Define input domains and strategies from the spec's data contracts; bias toward
edge values (empty, maximum, unicode, negative, boundary timestamps) rather than
uniform random data.

## oracle
Decide pass/fail without re-implementing the logic under test: compare against
an inverse operation, a simpler reference model, or an invariant that must hold
— never a copy of the production algorithm.

## shrinking and seed
On failure, record the minimal failing case and the generator seed in the
validation evidence so the run is reproducible.

## integration
The concrete tool/framework comes from the active `lang-*` skill; this pack is
the language-agnostic guidance (precedence D22/D36).
