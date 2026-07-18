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
| Event | Purpose | Status | Degrades to |
|---|---|---|---|
| `PreToolUse` (matcher `^exec$`) | rewrite shell commands through RTK so large output is bounded at 0 model-token cost | **implemented** — `scripts/workflow/devin-rtk-hook.py` | `rules/common/terminal-token-policy.md` (explicit `rtk` calls) |
| `SessionStart` | re-anchor active state and compact memory index via `additionalContext` | implemented — `devin-context-hook.py` | `core/boot.md` sequence in-band |
| `PostCompaction` | re-anchor state and memory pointers after compaction | implemented — `devin-context-hook.py` | re-read state next turn (`context-compaction-policy.md`) |

## The RTK rewrite hook (implemented)
RTK ships no Devin preset — its stock hook matches the Claude `Bash` tool, not
Devin's `exec` — so the imported Claude preset loads but never fires
(`core/hooks/rtk.md`). `scripts/workflow/devin-rtk-hook.py` bridges the gap: it
reads the `PreToolUse` event on stdin, and for an `exec` command asks
`rtk rewrite` for a compact equivalent, returning it as
`hookSpecificOutput.updatedInput.command`. rtk is the single source of truth.

Install (idempotent; the framework installer does this automatically when rtk is
present):
```
python ~/.alfred/scripts/workflow/sync-host-shims.py -Host devin-cli -InstallHooks
```
It writes a `PreToolUse`/`^exec$` entry into the DEVIN CLI **user** config
(`%APPDATA%\devin\config.json` on Windows, `~/.config/devin/config.json` on
POSIX), so it applies to every project.

**rtk exit-code note:** `rtk rewrite` (0.43.0) prints the rewritten command with a
**non-zero** exit code (3) when an equivalent exists, and prints nothing (exit 1)
when it does not. The documented "exit 0" is not what the binary does, so the hook
trusts **stdout**, not the exit code. Empty output → the original command runs
unchanged.

## Fail-open (D3)
Any mismatch — non-`exec` tool, missing rtk, a command rtk cannot compact,
unparseable stdin — makes the hook print nothing and exit 0, so the original
command runs unchanged. The hook never blocks.

## Capability probe
Do not infer hook behavior from a hard-coded version number. After installation,
use `/hooks`, run one command with a known RTK rewrite, and verify that `rtk gain`
increments. Record the result as observed evidence. If the probe fails, use RTK
explicitly and keep the hook capability unconfirmed.

## Confirm it fires in a real session
After install, in the DEVIN CLI: `/hooks` lists the PreToolUse entry; run a shell
command with a known rewrite (e.g. `git status`, `cat <file>`) and confirm
`rtk gain` increments. If it does not fire, the `exec` tool may name its command
field differently than `command`; the hook already no-ops safely, and the field
can be adjusted in `devin-rtk-hook.py`. The `SessionStart`/`PostCompaction` rows
above stay contract-only until similarly confirmed. Record in the demand `audit`
which hooks were active.
