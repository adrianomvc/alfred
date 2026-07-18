---
name: common-context-retrieval-policy
description: Progressive disclosure and advisory large-file reads
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Context Retrieval

## Trigger
Before loading memory details, a large source file, or a cross-file explanation.

## Rule
Start with the cheapest authoritative selector: compact index, `rg`, manifest,
symbol search, or outline. Load details and current source only when the active
decision needs them. Show approximate retrieval cost when it is available.

For a file estimated above 1,500 tokens, an optional host hook may suggest this
order once per session: related memory metadata, structural outline, current
symbol, bounded source range, then full file. The hook is **advisory** and may
add context; it must never deny a read. Before editing, open the relevant current
source. A stale index or observation is a pointer only.

## Degradation
Without hooks or structural tools, use `rg`, byte/line counts, and bounded reads.
Correctness, acceptance, security, SAFE gates, and original evidence always take
precedence over token savings.

## Grounding
This rule adapts Claude-Mem's context-engineering, progressive-disclosure,
file-read-gate, and smart-explore benchmark documentation at
`https://docs.claude-mem.ai/`. Alfred deliberately keeps the read gate advisory:
memory is a pointer, not authority, and current source may be required for a
safe decision.
