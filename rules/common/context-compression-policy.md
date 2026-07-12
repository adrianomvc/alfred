---
name: common-context-compression-policy
description: Common rule - safe RAG/context compression
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Context Compression Policy

## Trigger
Load this rule when Alfred uses RAG, search snippets, compressed summaries,
retrieval ranking, log summarization, codebase-memory output, or any other
compressed context instead of opening full sources up front.

## Rule
Compression may select and prioritize context; it must not become the source of
truth for decisions, edits, or validation.

Safe uses:
- triage large docs, logs, codebases, and reverse-engineering inputs;
- identify likely files, symbols, requirements, tests, and decisions to inspect;
- create short working summaries with source pointers;
- reduce repeated reading during resume.

Unsafe uses:
- editing code without opening the original source file;
- approving Design, SAFE decisions, or incidents from a compressed summary only;
- using compressed logs/summaries as final validation evidence;
- dropping acceptance criteria, constraints, exceptions, or rollback details
  because they did not appear in the compressed output.

## Required Evidence
Every compressed claim used materially must carry:
- source path or external source identifier;
- line/range, symbol, event id, timestamp, or query window when available;
- commit/ref or index version when available;
- confidence/limitation if the compressor reports one.

## Execution Guardrail
Before changing code, Alfred must open the original source files and the original
spec/decision excerpts relevant to the unit. Compressed context can point to what
to open; it cannot be the only input for the edit.

## Validation Guardrail
Validation evidence must come from original sources: test output, original logs,
diffs, source files, PRs, or human acceptance. A compressed summary may explain
evidence, but must point to the original artifact.

## Degradation
If compression is unavailable, stale, conflicts with source, or lacks pointers,
fall back to normal JIT loading, `rg`, bounded reads, and direct artifacts. If
the original source cannot be opened and the action depends on it, pause and ask.

## Audit
Record material use of compression in `audit` or observability metadata:
compressor/tool, query, sources returned, source refs opened, limitations, and
fallbacks.

## Observability
When compression is used, record candidate count, original sources opened,
estimated/actual reduction when measured, validation outcome, and later failures
that may relate to omitted context. Compression metrics inform proposals only;
original sources remain required for edits and validation evidence.
