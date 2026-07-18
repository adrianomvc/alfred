# Usage Rate Card Connector

## type
`usage-rate-card`

## activation
Activate only when a human/FinOps owner has approved a rate table for the
models and billing units used by the host. The rate card must be stored as a
versioned local artifact or approved export; Alfred must not fetch public prices
at runtime to invent cost.

## operations
- `read_rate_card(path)` loads currency, approval metadata, effective window,
  confidence, and per-model rates.
- `price_usage(usage_event, rate_card)` computes interaction cost from exact
  token/ACU usage already present in an append-only usage event.
- `append_cost_event(event)` appends a separate `usage_cost_attributed` event
  that references the original usage event through `parent_event_id`.

## degradation
If no approved rate card exists, keep interaction `cost_usd: null` and
`cost_confidence: unavailable`. Do not allocate `ccusage` or other session
totals across interactions. Session totals remain state fields for toolbar
display and must not drive demand forecasts.

## audit fields
- `rate_card_source`
- `rate_card_effective_from`
- `rate_card_approved_by`
- `rate_card_currency`
- `rate_card_hash`
- `cost_confidence` (`exact`, `rated`, `estimated`, `allocated`, `unavailable`)

## ACU block (DEVIN)
DEVIN bills in **ACU**, and Devin publishes no ACU→USD rate. To show USD on the
toolbar for Devin, the approved rate card may carry an `acu` block:
`{ "usd_per_acu": <approved contract value> }`. `scripts/metrics/session-cost.py`
converts the demand's ACU delta to USD **only** from this field; with no `acu`
block, keep `cost usd` empty and show ACU (never invent a USD value — D10).

## Rule
Interaction cost needs two inputs: exact interaction/request usage plus an
approved rate card or a source that already provides per-interaction cost.
ccusage session totals satisfy neither requirement for JSONL interaction cost;
they update `001-state.md` only.

Rate cards must include approval metadata (`source`, `approved_by`,
`effective_from`, `currency`) and are hashed into every
`usage_cost_attributed` event for auditability.

The optional `effective_to` is also enforced. Invalid, future, expired,
non-positive, or non-finite ACU rates degrade to unavailable. Shared validation
lives in `scripts/shared/observability/infrastructure/rate_cards/`; command
drivers must not implement a second approval rule.
