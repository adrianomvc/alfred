---
name: lang-python
description: Python engineering standard; overrides coding-standard where more specific. Load when Python files, tests, Glue jobs, FastAPI, or scripts are touched.
trigger: Load when the active unit changes Python files, Python tests, Glue Python jobs, FastAPI apps, scripts, or Python packaging.
sections_to_load:
  - rules
  - testing
  - review checklist
---

# Skill - Python Standard

## purpose
Python-specific engineering standard. It overrides `skills/coding-standard/SKILL.md` only where it is more specific.

## inputs
- active demand `state`
- app `reverse-eng`
- technical `spec`
- existing Python files and tests
- base `skills/coding-standard/SKILL.md`

## expected output
- Python implementation plan
- Python review findings
- test strategy proportional to risk

## rules
- Prefer small pure functions around business rules and IO boundaries.
- Keep cloud/runtime entrypoints thin; move testable logic to importable modules.
- Use explicit dataclasses or typed dictionaries for structured values when useful.
- Avoid broad `except Exception` unless re-raising with useful context.
- Avoid hidden runtime configuration; pass parameters explicitly or through a small config object.
- Keep imports side-effect light so unit tests can import modules without cloud credentials.

## testing
- Put tests under `tests/`.
- Test pure helpers without requiring cloud/runtime SDKs.
- For AWS Glue or serverless jobs, keep a thin entrypoint and test transformation/reconciliation helpers separately.
- Use integration tests only when environment parameters and credentials are available.

## review checklist
- code is importable locally;
- business logic is separated from runtime entrypoint;
- tests cover normal and failure paths relevant to the lane;
- sensitive data is not logged;
- runtime parameters are validated before use.
