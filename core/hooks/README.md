# Hooks

Optional host hooks make selected Alfred rules deterministic in a local
environment. They are never required for Alfred to work; every hook must degrade
to the matching Markdown rule.

## Hooks
| Hook | Purpose |
|---|---|
| [`rtk.md`](rtk.md) | Terminal token control for DEVIN CLI sessions |
| [`usage-attribution.md`](usage-attribution.md) | Stamp exact per-turn token usage from the Claude Code transcript |

## Rule
Hook setup is host-specific and must not change Alfred's core lifecycle. If a
hook is unavailable, load the related rule and continue manually.
