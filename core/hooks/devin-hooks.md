# DEVIN CLI hooks

Optional deterministic layer for the DEVIN CLI. Like every hook (D3), these are
never required: each degrades to the matching Markdown rule. They exist because
advisory rules can be missed under long context, while a hook always runs.

The DEVIN CLI runs eight lifecycle hooks and imports `.claude/` config by
default (`hosts/capabilities.md`). Hooks are configured in `.devin/hooks.v1.json`,
`.devin/config.json`, or the user config, and are **collected from all sources
without override**. Verify what loaded with `/hooks`.

Config shape (per event): an array of `{ "matcher": <regex>, "hooks": [ {"type":
"command", "command": <cmd>, "timeout": <s>} ] }`. Tool events receive
`tool_name`/`tool_input` on stdin; a hook rewrites input by printing
`hookSpecificOutput.updatedInput`, or injects context via
`hookSpecificOutput.additionalContext`.

## Hooks Alfred uses
| Event | Purpose | Degrades to |
|---|---|---|
| `PreToolUse` (matcher `exec`) | rewrite shell commands through RTK (`updatedInput.command`) so large output is bounded at 0 model-token cost | `rules/common/terminal-token-policy.md` (explicit `rtk` calls) |
| `SessionStart` | detect host capabilities, ensure RTK, re-anchor the active demand via `additionalContext` | `core/boot.md` sequence in-band |
| `PostCompaction` | re-anchor the `001-state.md` path after compaction | re-read state next turn (`context-compaction-policy.md`) |

## Why the RTK rewrite needs a Devin-specific entry
RTK's stock preset matches the `Bash` tool; Devin's shell tool is `exec`, so the
imported Claude preset loads but never fires (`core/hooks/rtk.md`). A DEVIN CLI
`PreToolUse` entry with `"matcher": "exec"` is what actually enables the
transparent rewrite here.

## Must be verified in a real DEVIN CLI session (do not assume)
This contract states the documented mechanism; three details need a live session
before the hooks are installed — never invent them:
1. the exact field name RTK must rewrite inside `updatedInput` for the `exec`
   tool (the doc example uses `command`);
2. where `rtk init -g` writes its hook and with which matcher, to avoid a
   conflicting or duplicate entry;
3. whether `PostCompaction` actually supports an `additionalContext` output — the
   docs list "re-inject lost context" as a use case but do not show the output
   format. If it does not, use `SessionStart` for re-anchoring instead.

Until verified, the DEVIN CLI keeps the advisory path (explicit `rtk`, in-band
boot, re-read state after compaction). Record in the demand `audit` which hooks
were actually active.
