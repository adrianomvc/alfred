# Install — Alfred for the DEVIN CLI

These installers set up Alfred for use inside the [DEVIN CLI](https://devin.ai):

1. Clone (or update) the Alfred framework into `~/.alfred`.
2. Install the `/alfred` skill into the DEVIN CLI user skills directory, so you
   can type `/alfred` in any repo to load the framework and operate as Alfred.

The framework stays a **single referenced source** (D15): the skill points at
`~/.alfred`; nothing is copied into your project repos.

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

## Options
| Setting | PowerShell flag | bash env var | Default |
|---|---|---|---|
| Framework repo | `-FrameworkUrl` | `ALFRED_FRAMEWORK_URL` | `https://github.com/adrianomvc/alfred.git` |
| Install dir | `-InstallDir` | `ALFRED_INSTALL_DIR` | `~/.alfred` |
| Branch | `-Branch` | `ALFRED_BRANCH` | repo default |
| Skills dir | `-SkillsDir` | `ALFRED_SKILLS_DIR` | `%APPDATA%\devin\skills` / `~/.agents/skills` |

## Verify
```bash
devin skills list      # shows: /alfred [user] (...) - Load the Alfred framework ...
devin skills show alfred
```
Then, inside a repo, type `/alfred` in the DEVIN CLI.

## Update / uninstall
- **Update:** re-run the installer; it pulls the latest framework into `~/.alfred`.
- **Uninstall:** delete the skill folder (`%APPDATA%\devin\skills\alfred` or
  `~/.agents/skills/alfred`); optionally remove `~/.alfred`.

## How it works
The DEVIN CLI loads skills from `SKILL.md` files under its user/project skill
directories (`devin skills paths`). The `/alfred` skill is a thin entry point:
on invocation it reads `~/.alfred/core/boot.md` and follows Alfred's boot
sequence (detect HUB/APP, JIT context load, Risk Mode, butler persona,
anti-overconfidence). The framework itself is plain markdown — the skill only
points the agent at it.
