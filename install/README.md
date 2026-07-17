# Install — Alfred for the DEVIN CLI

This installer sets up Alfred for use inside the [DEVIN CLI](https://devin.ai):

1. Clone (or update) the Alfred framework into `~/.alfred`.
2. Install the `/alfred` skill into the DEVIN CLI user skills directory, so you
   can type `/alfred` in any repo to load the framework and operate as Alfred.
3. Set up the **notification adapter** (owner decision: MCP + Python): register
   your e-mail in `~/.alfred-email.json` (dry-run by default — nothing is sent
   until you fill `smtp{}` and set `mode: active`) and, when the Claude Code CLI
   and Python are available, register the `alfred-email` MCP server (user scope).
   The config also receives the **org telemetry destination** (`telemetry_to`,
   from `knowledge/notification.md` or `ALFRED_TELEMETRY_TO`): every runner's
   observability logs are batched and e-mailed there automatically (provisional
   transport until the telemetry API exists, D45) so the org can aggregate metrics.
   Existing config is never overwritten; every part degrades gracefully (D3).
4. Optionally set up **RTK** for DEVIN CLI terminal sessions. RTK is a local
   tool/hook that bounds large command output. Alfred downloads the configured
   RTK URL when RTK is not already on `PATH`. The default URL is a public GitHub
   Windows zip placeholder that should be replaced by the corporate Artifactory
   zip when available.
5. Optionally install approved npm tools from the corporate npm registry /
   Artifactory: `ccusage` for local Claude/Codex usage attribution. This is
   best-effort: missing npm, registry access, or packages never break the Alfred
   install. `codebase-memory` is **not** installed by default (see
   `connectors/codebase-memory.md`).

The framework stays a **single referenced source** (D15): the skill points at
`~/.alfred`; nothing is copied into your project repos.

> **Other hosts (Claude Code, GitHub Copilot, Codex):** this installer is the
> turn-key path for the DEVIN CLI. The per-host entry points live in `hosts/`
> (see `hosts/README.md`) — clone the framework, then register that host's entry
> file. The DEVIN skill source itself now lives at `hosts/devin-cli/SKILL.md`.

## Install
The installer is **bash-only** (`AGENTS.md` § Conventions). On Windows, run it
from **Git Bash** — the primary corporate path; the installer detects
`MINGW`/`MSYS`/`CYGWIN` and adapts.

```bash
bash install/install.sh
```

One-liner:
```bash
curl -fsSL https://raw.githubusercontent.com/itau-corp/itau-sq9-modules-alfred-v2/main/install/install.sh | bash
```

Installs the skill to the DEVIN CLI documented global skills path:
`~/.config/devin/skills/alfred/SKILL.md` on Linux/macOS
(`%APPDATA%\devin\skills\alfred\SKILL.md` on Windows).

## Corporate Machine Setup
When preparing this installer for a company computer, there are three external
locations you normally need to replace:

1. **Alfred framework repo**
   - Edit `DEFAULT_FRAMEWORK_URL` in the `COMPANY SETTINGS` block at the top of
     `install/install.sh`.
   - Temporary alternative:
     ```bash
     ALFRED_FRAMEWORK_URL="<internal-alfred-git-url>" bash install/install.sh
     ```

2. **RTK download URL**
   - Edit `DEFAULT_RTK_URL` in the same `COMPANY SETTINGS` block.
   - The default RTK URL is intentionally the public Windows zip placeholder
     because the primary company path is Windows/Git Bash and the Artifactory
     package will also be a zip. Replace it with the internal Artifactory zip
     when available.
   - Temporary alternative:
     ```bash
     ALFRED_RTK_URL="<artifactory-rtk-url>" bash install/install.sh
     ```

3. **npm registry / Artifactory**
   - Set `ALFRED_NPM_REGISTRY="<artifactory-npm-registry>"`.
   - If the corporate packages have scoped/internal names, override them with
     `ALFRED_CCUSAGE_PACKAGE` and `ALFRED_CODEBASE_MEMORY_PACKAGE`.

If the one-line install command is used inside the company network, replace the
`raw.githubusercontent.com/.../install/install.sh` URL with the internal
raw-file URL from the company mirror.

## Options
| Setting | bash env var | Default |
|---|---|---|
| Framework repo | `ALFRED_FRAMEWORK_URL` | `https://github.com/itau-corp/itau-sq9-modules-alfred-v2.git` |
| Install dir | `ALFRED_INSTALL_DIR` | `~/.alfred` |
| Version (tag) | `ALFRED_VERSION` | latest on default branch |
| Branch | `ALFRED_BRANCH` | repo default |
| Skills dir | `ALFRED_SKILLS_DIR` | `~/.config/devin/skills` (POSIX) |
| Notification e-mail | `ALFRED_EMAIL` | interactive prompt (skipped when non-interactive) |
| Skip e-mail/MCP setup | `ALFRED_SKIP_EMAIL=1` | setup runs |
| RTK package URL | `ALFRED_RTK_URL` | public Windows zip placeholder |
| Skip RTK setup | `ALFRED_SKIP_RTK=1` | setup runs if URL or `rtk` exists |
| npm registry / Artifactory | `ALFRED_NPM_REGISTRY` | corporate Artifactory npm-remote |
| ccusage npm package | `ALFRED_CCUSAGE_PACKAGE` | `ccusage` |
| codebase-memory npm package | `ALFRED_CODEBASE_MEMORY_PACKAGE` | empty (not installed) |
| Skip npm tools | `ALFRED_SKIP_NPM_TOOLS=1` | setup runs if `npm` exists |
| Skip AI Stack check | `ALFRED_SKIP_AI_STACK_CHECK=1` | check runs if `npm` exists |

## RTK terminal hook (DEVIN CLI only)
RTK setup is optional and currently scoped to the DEVIN CLI install path.

```bash
ALFRED_RTK_URL="<artifactory-url>" bash install/install.sh
```

If `rtk` is already on `PATH`, the installer only runs:
```bash
rtk init -g
```

If the URL is removed or RTK cannot be downloaded, Alfred then follows
`rules/common/terminal-token-policy.md`: prefer bounded native commands and
load `core/hooks/rtk.md` only as guidance.

## npm tools (optional)
The installer can install the approved npm packages used by optional connectors:

```bash
ALFRED_NPM_REGISTRY="<artifactory-npm-registry>" \
ALFRED_CCUSAGE_PACKAGE="ccusage" \
bash install/install.sh
```

If npm is already configured with the corporate registry, omit the registry env
var. If a package cannot be installed, Alfred records the degraded state and
keeps working through `rg`, bounded file reads, and manual cost input.

## Versions
Releases are git tags `vMAJOR.MINOR.PATCH` (source of truth: `VERSION` + `CHANGELOG.md`).
- **Latest stable** (default): the installer tracks the default branch (`main`).
- **Pinned** (reproducible): pass a tag to freeze the framework version.
```bash
ALFRED_VERSION=v0.2.0 bash install/install.sh
```
Re-running with a different `ALFRED_VERSION` switches `~/.alfred` to that tag;
re-running without it returns to the latest on the default branch. A pinned
version maps to the framework version a demand stamps in its `state`
(reproducibility — D26).

## Verify
```bash
devin skills list      # shows: /alfred [user] (...) - Load the Alfred framework ...
devin skills show alfred
```
Then, inside a repo, type `/alfred` in the DEVIN CLI.

## Update and rollback
Alfred installs the **latest** version and keeps up to date automatically: on
each `/alfred` invocation it fast-forwards `~/.alfred` to the latest release —
**unless a demand is in progress**, in which case the demand stays on its
stamped (frozen) version and you are only told an update is available
(`docs/version-adoption.md`).

Manual controls:
| Action | Command |
|---|---|
| Update to latest now | re-run `bash install/install.sh` |
| List available versions | `bash install/install.sh list` |
| Roll back one version | `bash install/install.sh rollback` |
| Pin a specific version | `ALFRED_VERSION=v0.1.0 bash install/install.sh` |

`rollback` moves `~/.alfred` to the previous release tag (use it if a new
version breaks something). Re-running the installer without it returns to the
latest. A demand records the version it ran on (D26), so you know which tag to
roll back to.

## Refresh copied host entries
Host entry files are copied into native locations during setup. After pulling a
new Alfred version, refresh the copied entry so the host does not keep old boot
instructions:

```bash
python ~/.alfred/scripts/workflow/sync-host-shims.py -Host devin-cli
```

For Claude Code use `-Host claude-code`; for Codex use `-Host codex`. Missing
targets are skipped unless `-Create` is passed.

## Claude Code usage hook
Claude Code can collect request tokens from its transcript without asking the
agent to estimate usage. Install or refresh the hook explicitly:

```bash
python ~/.alfred/scripts/workflow/sync-host-shims.py -Host claude-code -Create -InstallHooks
```

To write only sanitized technical telemetry outside a demand, set
`AI_OBS_RAW_LOG` and optionally `AI_OBS_MODE=raw`. To write Alfred decision
events, set `ALFRED_STATE_PATH` or `ALFRED_OBS_LOG`; `AI_OBS_MODE=both` writes
both. `ccusage` can still update `001-state.md` and the toolbar with the total
session cost, but that total is not appended to interaction JSONL.

## Uninstall
- Delete the skill folder (`~/.config/devin/skills/alfred` on POSIX, `%APPDATA%\devin\skills\alfred` on Windows); optionally remove `~/.alfred`.

## How it works
The DEVIN CLI loads skills from `SKILL.md` files under its user/project skill
directories (`devin skills paths`). The `/alfred` skill is a thin entry point:
on invocation it reads `~/.alfred/core/boot.md` and follows Alfred's boot
sequence (detect HUB/APP, JIT context load, Risk Mode, butler persona,
anti-overconfidence). The framework itself is plain markdown — the skill only
points the agent at it.
