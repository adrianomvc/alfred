# RTK Hook

RTK is a local terminal tool plus shell hook that keeps command output bounded.
It supports Alfred's terminal token policy; it is not a source of truth and not
a framework dependency.

## Supported host
Automatic RTK setup is currently scoped to **DEVIN CLI** installs only. Other
hosts may use RTK manually, but Alfred must not require it there.

## Install inputs
- RTK binary/package source: provided by the organization, currently expected
  from Artifactory.
- Installer variable: `ALFRED_RTK_URL=<artifact-url> bash install/install.sh`
- Skip flag: `ALFRED_SKIP_RTK=1`

No URL means no download. The installer records that RTK setup was skipped and
Alfred falls back to `rules/common/terminal-token-policy.md`.

## Setup (idempotent — safe to re-run every session)
1. Resolve the installed `rtk` command from `PATH` (`rtk --version`). If absent
   and an approved artifact URL was provided, install it into the user's local
   tool directory. If absent with no approved source, stop and fall back — never
   invent an install source.
2. If the Claude Code CLI is present, run `rtk init -g` once (idempotent). It
   installs Claude's command-rewrite hook and writes `RTK.md` plus the global
   config. Skip this on Devin-only machines; it may fail trying to write under
   a missing `~/.claude` directory and Devin does not use that preset.
3. For Devin, install Alfred's own `PreToolUse` bridge with
   `sync-host-shims.py -Host devin-cli -InstallHooks`.
4. In a project whose host needs local hook state, run `rtk init` from the repo root.
5. Verify: `rtk --version` **and** `rtk gain` (neither may be "command not
   found"; a collision with a different `rtk` binary shows up here).

## Devin and the auto-rewrite hook (important)
RTK's transparent rewrite (`git status` → `rtk git status`) is delivered by a
Claude-Code-style **`PreToolUse` hook**. The DEVIN CLI **does** run `PreToolUse`
and imports `.claude/` config by default, so the hook is *loaded* — but RTK's
Claude-Code preset matches the `Bash` tool, while Devin's shell tool is `exec`
(`read`, `edit`, `grep`, `glob`, `exec`). The matcher never matches, so the
rewrite **loads yet never fires**. The RTK docs ship presets for Claude
Code/Copilot (default), Gemini, Cursor, Windsurf, Cline, and OpenCode —
**none targets Devin's `exec` tool**. Until a Devin hook entry with an `exec`
matcher is installed, guarantee the savings by **calling `rtk` explicitly** for
shell and large-output commands. `rtk init -g` is not required on a Devin-only
machine: Alfred's `exec` bridge calls RTK directly and RTK uses its defaults
when no optional global config exists.

## Use
When RTK is available, call it explicitly for bounded output:
- `rtk cat`  ·  `rtk grep`  ·  `rtk diff`  ·  `rtk test`
- `rtk <cmd>` for any other shell command; `rtk gain` to confirm real savings.

Still inspect summaries first (`git diff --stat`, targeted searches, limited
logs). RTK reduces terminal noise; it does not replace judgment. Telemetry is
opt-in (`rtk telemetry enable|disable|status`) — leave it to the human/org.

## Degradation
If RTK cannot be installed or initialized, use bounded native commands and
record the limitation only when it affects validation, evidence, or a human
decision.
