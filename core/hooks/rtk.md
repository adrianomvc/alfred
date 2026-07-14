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
- Installer variable/flag:
  - PowerShell: `install.ps1 -RtkUrl <artifact-url>`
  - bash: `ALFRED_RTK_URL=<artifact-url> bash install/install.sh`
- Skip flag:
  - PowerShell: `-SkipRtk`
  - bash: `ALFRED_SKIP_RTK=1`

No URL means no download. The installer records that RTK setup was skipped and
Alfred falls back to `rules/common/terminal-token-policy.md`.

## Setup (idempotent — safe to re-run every session)
1. Resolve the installed `rtk` command from `PATH` (`rtk --version`). If absent
   and an approved artifact URL was provided, install it into the user's local
   tool directory. If absent with no approved source, stop and fall back — never
   invent an install source.
2. Ensure the global hook + docs exist: run `rtk init -g` once (idempotent). It
   installs RTK's command-rewrite hook and writes `RTK.md` plus the global config
   at `~/.config/rtk/config.toml` (Windows: the AppData equivalent).
3. In a project that needs local hook state, run `rtk init` from the repo root.
4. Verify: `rtk --version` **and** `rtk gain` (neither may be "command not
   found"; a collision with a different `rtk` binary shows up here).

## Devin and the auto-rewrite hook (important)
RTK's transparent rewrite (`git status` → `rtk git status`) is delivered by a
Claude-Code-style **`PreToolUse` hook**. The RTK docs ship agent presets for
Claude Code/Copilot (default), Gemini, Cursor, Windsurf, Cline, and OpenCode —
**there is no Devin preset**, so do not assume Devin executes that hook. On DEVIN
CLI, guarantee the savings by **calling `rtk` explicitly** for shell and
large-output commands, whether or not the rewrite fires. Running `rtk init -g`
still matters: it creates the `~/.config/rtk/config.toml` and `RTK.md` the tool
reads, and `config.toml` (`[hooks] exclude_commands`, `[tee]`) tunes behavior.

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
