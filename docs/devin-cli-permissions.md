# DEVIN CLI — permissions and sandbox readiness

Alfred runs helper scripts from `~/.alfred/scripts/**` and shells out to `git`,
`rtk`, and `python`. On the DEVIN CLI two host features decide whether those run
smoothly, add approval turns, or fail outright: **permission scopes** and the
**OS sandbox**. This is optional hardening — Alfred degrades to advisory markdown
and bounded native commands without it (D3) — but on a locked-down corporate
install it is the difference between usable and blocked.

Source template: `hosts/devin-cli/config.template.json`. The `/alfred` skill
offers to create `.devin/config.json` from it after human confirmation. Project
config accepts only `permissions`, `mcpServers`, `read_config_from`, and `hooks`.

## Why an allowlist

By default every `exec` prompts for approval. Alfred renders the toolbar, builds
the context manifest, checks for updates, and imports usage several times per
demand — each unapproved `exec` is an extra turn, which is extra tokens. An
allowlist of the exact commands Alfred runs removes those prompts without
widening blanket permissions.

| Allow rule | Covers | Note |
|---|---|---|
| `Read(~/.alfred/**)` | reading framework markdown/scripts | `~` expands to home |
| `Exec(python ~/.alfred/scripts)` | `render-toolbar.py`, `context-manifest.py`, `check-update.py`, `sync-host-shims.py`, `import-ccusage.py` | prefix match |
| `Exec(rtk)` | terminal-token-policy commands | |
| `Exec(git)` | status/diff/commit on the demand branch | |

**Must be validated in a real session (not yet confirmed here):** the `Exec(...)`
matcher matches a command **prefix**, and Alfred resolves `~/.alfred` to an
absolute path before running (on Windows, `cygpath -w` → `C:\Users\...`). So
`Exec(python ~/.alfred/scripts)` may not match a command that starts with a
resolved `C:\Users\...\.alfred\scripts` path. Confirm with the plan's check —
run `render-toolbar.py` and see whether it prompts — and widen or adjust the
prefix (e.g. `Exec(python)`, accepting the broader scope) only if needed. Do not
assume these strings are correct without observing a session.

## The sandbox blocks helpers outside the workspace

With `--sandbox` (`devin sandbox`, Linux/macOS; admins can force it org-wide),
the CLI restricts filesystem access to granted scopes plus the workspace, and
**blocks scripts outside the project workspace unless explicitly granted**.
`~/.alfred/scripts/**` is outside the workspace, so under sandbox the helpers
fail closed. To keep Alfred working:

- grant `Read(~/.alfred/**)` (and, if the sandbox also gates execution of files,
  the corresponding scope) so the interpreter can read the scripts;
- or run the framework from inside the workspace when policy forbids home-dir
  access;
- or degrade: Alfred falls back to advisory markdown + bounded native commands,
  recording the limitation (this is the D3 guarantee, not a failure).

Sandbox network filtering is separate (allow/deny domains); Alfred's core needs
no network, so this only affects optional catalog/MCP fetches.

## Duplicate `alfred` skill (`read_config_from.claude=false`)

The DEVIN CLI imports `.claude/skills/**/SKILL.md` by default. A machine with
both the Claude Code and DEVIN CLI shims installed then exposes **two**
`name: alfred` skills, and the Claude-Code copy carries host-specific
instructions that are wrong for Devin (ccusage, `/cost`, `-RegisterActive`). The
template sets `read_config_from.claude=false` so Devin loads only its own
`alfred` skill. This also stops Devin from importing the Claude-Code RTK hook —
which is intended: that hook's matcher targets `Bash`, not Devin's `exec` tool,
so it never fires anyway (see `hosts/capabilities.md`). The correct Devin-native
hook is installed separately.

To keep Claude imports on a machine that does not have both shims, remove the
`read_config_from` block.
