# 004-skills - ABC

## Active Skills
| Skill | Trigger | Status | Reason |
|---|---|---|---|
| `coding-standard` | every Execution/Validate step | active | base engineering standard |
| `lang-python` | Python files or tests touched | active | `abc-app-api` uses Python |
| `security-review` | SAFE lane or sensitive data | available | loaded only when triggered |

## Precedence Example
- `coding-standard` says tests should be proportional to risk.
- `lang-python` says Python tests go under `tests/` and runtime entrypoints stay thin.
- Result: Python demand uses both; `lang-python` supplies the specific structure.

## JIT Loading
For a Python execution unit, load:
- `skills/coding-standard/SKILL.md`
- `skills/lang-python/SKILL.md#rules`
- `skills/lang-python/SKILL.md#testing`

Do not load the whole skill catalog.

