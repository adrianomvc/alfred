---
name: coding-standard
description: Default engineering standard (SOLID). Load during Execution/Validate when code, configuration, tests, or automation change and no language-specific skill overrides it.
trigger: Load during Execution and Validate when code, configuration, tests, or automation artifacts are changed.
sections_to_load:
  - rules
  - output
---

# Skill - Coding Standard

## purpose
Default engineering standard when no language-specific skill is active.

## inputs
- active demand `state`
- technical `spec`
- execution plan when present
- changed files and tests

## expected output
- implementation guidance
- review findings
- proportional test strategy

## rules
- Prefer small, cohesive changes.
- Respect existing architecture and naming.
- Apply SOLID pragmatically: one reason to change, explicit dependencies, substitutable contracts, narrow interfaces.
- Keep brownfield changes in place; never create `file_v2` as a workaround.
- Add tests proportional to risk and blast radius.
- Never remove, weaken, or skip a test to satisfy a gate: a failing test means fix the cause or escalate — deleting/loosening tests to "pass" hides missing or buggy functionality.
- Make automation-friendly UI/API changes where applicable.

## output
Execution and Reviewer use this as the baseline for code plans, implementation, and review findings.
