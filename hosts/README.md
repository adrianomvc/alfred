# Hosts — running Alfred inside a coding agent

A **host integration** binds Alfred (plain markdown) to one coding host through
that host's *native* instruction mechanism. It is a thin entry point: it points
the host at `core/boot.md` and tells it to operate as Alfred. The framework
itself never changes per host (D3, agnostic markdown).

> Not to be confused with **connector adapters** in `connectors/`, which give
> Alfred *access to external systems* (vcs, tracker, notification…). A host
> integration is about *who runs Alfred*; a connector is about *what Alfred reaches*.

> **Sources vs installation:** this folder holds the versioned *sources* of each
> entry point. Installation copies them into each host's **native location**
> (`~/.claude/skills/`; for the DEVIN CLI, the documented global skills path —
> `%APPDATA%\devin\skills\` on Windows or `~/.config/devin/skills/` on
> Linux/macOS; a project's `.devin/config.local.json`; a repo's
> `.github/copilot-instructions.md`). Dot-locations are live, per-machine/project,
> and may hold secrets — they are never the source of truth.

## Common bind (every host)
1. Clone the framework once as a single referenced source (D15), using the
   configured Alfred repository URL from `install/README.md`:
   `git clone <alfred-framework-repo-url> ~/.alfred`
2. Register the host's entry file below so it reads `~/.alfred/core/boot.md`.
3. The entry point then follows Alfred's own rules: boot sequence, `core/principles.md`
   (supreme law: never invent), butler persona. `core/risk-mode.md` (FAST/Standard/SAFE)
   and `core/model-policy.md` load JIT — at Inception and at model selection, not at boot.

### Path resolution (read this)
The install location is the **logged-in user's** home at `.alfred`. Hosts must
**never type or guess a username** and never read a literal `~`/`$HOME`/`$USER`.
Resolve the path by running a command and using its **exact output**:

- **Windows + Git Bash/MSYS (usual case):** `cygpath -w "$HOME/.alfred/core/boot.md"` → `C:\Users\<live-user>\.alfred\core\boot.md` (native readers reject the shell's `/c/Users/...`; `cygpath -w` produces the accepted `C:\...` form).
- **macOS/Linux:** `echo "$HOME/.alfred/..."`.
- **Only in a real cmd.exe/PowerShell:** `echo %USERPROFILE%\.alfred\...`. Do **not** use `%USERPROFILE%`/`%APPDATA%` in Git Bash — `%VAR%` stays literal there; use `$HOME`/`$USERPROFILE` + `cygpath`.

The username is whatever the command prints — taken from the live session, never assumed or typed.

## Hosts
| Host | Native entry mechanism | Entry file | Install |
|---|---|---|---|
| DEVIN CLI | user skill (`/alfred`) | `devin-cli/SKILL.md` | turn-key — see `install/` |
| Claude Code | skill / slash command | `claude-code/SKILL.md` | copy to `~/.claude/skills/alfred/SKILL.md` |
| GitHub Copilot | repo custom instructions | `github-copilot/copilot-instructions.md` | copy to `.github/copilot-instructions.md` |
| Codex | `AGENTS.md` | `codex/AGENTS.md` | copy to repo root or `~/.codex/AGENTS.md` |

## Generated shims
The entry files above are committed for simple copy/install flows, but they are
generated from `hosts/_template/shim.md` plus host deltas in
`hosts/_template/hosts.json`. Edit the template or the delta, then run
`scripts/workflow/generate-host-shims.py`; `validate-framework` checks drift.

## Syncing installed host entries
Updating `~/.alfred` is not enough when a host reads a copied native entry file.
`alfred framework update` refreshes host entries automatically; after a manual
framework pull, refresh with the canonical CLI:

```bash
python ~/.alfred/scripts/alfred.py host sync --host claude-code --install-hooks
```

Use `--host devin-cli` or `--host codex` for those hosts. Missing targets are
skipped by default; the underlying helper is
`scripts/workflow/sync-host-shims.py` (pass `-Create` only during installation
or explicit setup).

## Cache-friendly loading
Hosts that expose prompt caching or persistent context should keep Alfred's
stable kernel before volatile demand state: framework principles/boot/indexes
first, generated registries/manifests next, active rules/skills after that, and
the current demand `state` plus working artifacts last. Hosts without cache
controls still follow the same order as a plain JIT discipline. The portable
rule is `rules/common/prompt-caching-policy.md`; no feature may require
host-specific caching (D3).

## The one host-specific setting: model (D46/D14)
The model policy uses abstract tiers (`cheap`/`medium`/`strong`). Each host exposes
different concrete model names, so the **tier → concrete-model map in
`core/model-policy.md`** is the only per-host configuration. If a host cannot
switch models, Alfred uses the default and records which model ran (degrades, D3).

## Optional deterministic enforcement (hooks)
Alfred's rules are **advisory** — the host model follows them, but nothing forces it.
Hosts that support hooks can make the critical gates **deterministic** by wiring the
existing validators to hook points (optional layer; everything still works without it, D3):
- run `validate-demand` (or `validate-sdd-gate`) as a *stop/finish* hook so a session
  cannot end with a broken demand state;
- block writes outside the active unit's declared write scope with a *pre-write* hook;
- initialize RTK for DEVIN CLI terminal sessions so large command output is filtered
  before it enters model context (`core/hooks/rtk.md`);
- run `validate-framework` before commits that touch the framework repo.
Advisory rule vs deterministic hook: instructions can be missed under long context;
a hook always executes. Configure per host (e.g. Claude Code `.claude/settings.json`
hooks); record in the demand `audit` which hooks were active.

Which hooks/commands each host actually offers is tracked in
[`capabilities.md`](capabilities.md) — the single source for per-host deterministic
claims, so rules and shims never guess a host's features.

## Degradation
No installer for a host? The integration still works manually: clone the
framework and paste/point the entry file's instructions into the host's
instruction mechanism. The entry files here are short on purpose — the real
content lives once in `core/`.
