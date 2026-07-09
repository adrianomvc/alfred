---
name: common-terminal-token-policy
description: Common rule - Terminal Token Policy
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Terminal Token Policy

Load this rule before running shell commands, reading logs, or showing command
output to a human. The goal is not to hide evidence; it is to avoid flooding the
agent context with unbounded terminal text.

## Rule
- Prefer RTK-filtered commands when RTK is installed in the active host.
- If RTK is unavailable, use bounded native commands: `head`/`tail`, `Select-Object
  -First`, `--stat`, `--name-only`, `--max-count`, or equivalent.
- Never run an unbounded command when the output can reasonably be huge: full
  logs, full diffs, recursive file dumps, dependency trees, generated files, or
  binary-adjacent artifacts.
- Inspect summaries first, then drill into the smallest useful slice.
- When a command fails because RTK is missing, fall back to bounded native
  commands and record only if it affects the demand.

## Preferred patterns
| Need | Preferred |
|---|---|
| read a file | `rtk cat <path>` or bounded `Get-Content -TotalCount` |
| search | `rtk grep <pattern>` or `rg -n <pattern>` |
| diff | `git diff --stat` before `rtk diff` or a scoped `git diff -- <path>` |
| tests | `rtk test <command>` or run the narrowest relevant test target |
| logs | `rtk cat <log>` with filters, or `tail`/`Select-Object -Last` |

## Human-facing output
- Summarize command results; do not paste large raw outputs unless explicitly
  requested.
- Include the command's important failure line, count, path, or status so the
  human can act without reading the full transcript.
- If the full output is required as evidence, write it to the correct artifact
  or attach it as a bounded evidence file instead of flooding chat.

## Scope
RTK is a local terminal tool and hook. It is optional automation, not a new
Alfred runtime requirement. The current supported automatic setup path is DEVIN
CLI only; other hosts follow this policy manually until they receive a native
RTK hook.
