# Install — Alfred for the DEVIN CLI

These installers set up Alfred for use inside the [DEVIN CLI](https://devin.ai):

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

The framework stays a **single referenced source** (D15): the skill points at
`~/.alfred`; nothing is copied into your project repos.

> **Other hosts (Claude Code, GitHub Copilot, Codex):** this installer is the
> turn-key path for the DEVIN CLI. The per-host entry points live in `hosts/`
> (see `hosts/README.md`) — clone the framework, then register that host's entry
> file. The DEVIN skill source itself now lives at `hosts/devin-cli/SKILL.md`.

## Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File install/install.ps1
```
One-liner (after the installer is on the default branch):
```powershell
irm https://raw.githubusercontent.com/adrianomvc/alfred/main/install/install.ps1 | iex
```
Installs the skill to `%APPDATA%\devin\skills\alfred\SKILL.md`.

## macOS / Linux (bash)
```bash
bash install/install.sh
```
One-liner:
```bash
curl -fsSL https://raw.githubusercontent.com/adrianomvc/alfred/main/install/install.sh | bash
```
Installs the skill to `~/.agents/skills/alfred/SKILL.md` (a user skill path the
DEVIN CLI reads on every platform).

## Corporate Machine Setup
When preparing this installer for a company computer, there are only two links
you normally need to replace:

1. **Alfred framework repo**
   - PowerShell: edit the `-FrameworkUrl` default in the `COMPANY SETTINGS`
     block at the top of `install/install.ps1`.
   - bash: edit `DEFAULT_FRAMEWORK_URL` in the `COMPANY SETTINGS` block at the
     top of `install/install.sh`.
   - Temporary alternative:
     ```powershell
     powershell -ExecutionPolicy Bypass -File install/install.ps1 -FrameworkUrl "<internal-alfred-git-url>"
     ```
     ```bash
     ALFRED_FRAMEWORK_URL="<internal-alfred-git-url>" bash install/install.sh
     ```

2. **RTK download URL**
   - PowerShell: edit the `-RtkUrl` default in the same `COMPANY SETTINGS`
     block at the top of `install/install.ps1`.
   - bash: edit `DEFAULT_RTK_URL` in the `COMPANY SETTINGS` block at the top of
     `install/install.sh`.
   - The default RTK URL is intentionally the public Windows zip placeholder
     because the primary company path is Windows/Git Bash and the Artifactory
     package will also be a zip. Replace it with the internal Artifactory zip
     when available.
   - Temporary alternative:
     ```powershell
     powershell -ExecutionPolicy Bypass -File install/install.ps1 -RtkUrl "<artifactory-rtk-url>"
     ```
     ```bash
     ALFRED_RTK_URL="<artifactory-rtk-url>" bash install/install.sh
     ```

If the one-line install command is used inside the company network, replace the
`raw.githubusercontent.com/.../install/install.ps1` or `install/install.sh` URL
with the internal raw-file URL from the company mirror.

## Options
| Setting | PowerShell flag | bash env var | Default |
|---|---|---|---|
| Framework repo | `-FrameworkUrl` | `ALFRED_FRAMEWORK_URL` | `https://github.com/adrianomvc/alfred.git` |
| Install dir | `-InstallDir` | `ALFRED_INSTALL_DIR` | `~/.alfred` |
| Version (tag) | `-Version` | `ALFRED_VERSION` | latest on default branch |
| Branch | `-Branch` | `ALFRED_BRANCH` | repo default |
| Skills dir | `-SkillsDir` | `ALFRED_SKILLS_DIR` | `%APPDATA%\devin\skills` / `~/.agents/skills` |
| Notification e-mail | `-Email` | `ALFRED_EMAIL` | interactive prompt (skipped when non-interactive) |
| Skip e-mail/MCP setup | `-SkipEmail` | `ALFRED_SKIP_EMAIL=1` | setup runs |
| RTK package URL | `-RtkUrl` | `ALFRED_RTK_URL` | public Windows zip placeholder |
| Skip RTK setup | `-SkipRtk` | `ALFRED_SKIP_RTK=1` | setup runs if URL or `rtk` exists |

## RTK terminal hook (DEVIN CLI only)
RTK setup is optional and currently scoped to the DEVIN CLI install path.

PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File install/install.ps1 -RtkUrl "<artifactory-url>"
```

bash:
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

## Versions
Releases are git tags `vMAJOR.MINOR.PATCH` (source of truth: `VERSION` + `CHANGELOG.md`).
- **Latest stable** (default): the installer tracks the default branch (`main`).
- **Pinned** (reproducible): pass a tag to freeze the framework version.
```powershell
powershell -ExecutionPolicy Bypass -File install/install.ps1 -Version v0.2.0
```
```bash
ALFRED_VERSION=v0.2.0 bash install/install.sh
```
Re-running with a different `-Version` switches `~/.alfred` to that tag; re-running
without it returns to the latest on the default branch. A pinned version maps to
the framework version a demand stamps in its `state` (reproducibility — D26).

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
| Action | PowerShell | bash |
|---|---|---|
| Update to latest now | re-run `install.ps1` | re-run `install.sh` |
| List available versions | `install.ps1 -List` | `bash install.sh list` |
| Roll back one version | `install.ps1 -Rollback` | `bash install.sh rollback` |
| Pin a specific version | `install.ps1 -Version v0.1.0` | `ALFRED_VERSION=v0.1.0 bash install.sh` |

`-Rollback` moves `~/.alfred` to the previous release tag (use it if a new
version breaks something). Re-running the installer without `-Rollback` returns
to the latest. A demand records the version it ran on (D26), so you know which
tag to roll back to.

## Uninstall
- Delete the skill folder (`%APPDATA%\devin\skills\alfred` or `~/.agents/skills/alfred`); optionally remove `~/.alfred`.

## How it works
The DEVIN CLI loads skills from `SKILL.md` files under its user/project skill
directories (`devin skills paths`). The `/alfred` skill is a thin entry point:
on invocation it reads `~/.alfred/core/boot.md` and follows Alfred's boot
sequence (detect HUB/APP, JIT context load, Risk Mode, butler persona,
anti-overconfidence). The framework itself is plain markdown — the skill only
points the agent at it.
