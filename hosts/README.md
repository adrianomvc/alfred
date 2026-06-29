# Hosts — running Alfred inside a coding agent

A **host integration** binds Alfred (plain markdown) to one coding host through
that host's *native* instruction mechanism. It is a thin entry point: it points
the host at `core/boot.md` and tells it to operate as Alfred. The framework
itself never changes per host (D3, agnostic markdown).

> Not to be confused with **connector adapters** in `connectors/`, which give
> Alfred *access to external systems* (vcs, tracker, notification…). A host
> integration is about *who runs Alfred*; a connector is about *what Alfred reaches*.

## Common bind (every host)
1. Clone the framework once as a single referenced source (D15):
   `git clone https://github.com/adrianomvc/alfred.git ~/.alfred`
2. Register the host's entry file below so it reads `~/.alfred/core/boot.md`.
3. The entry point then follows Alfred's own rules: boot sequence, `core/principles.md`
   (supreme law: never invent), `core/risk-mode.md` (FAST/Standard/SAFE), butler persona.

## Hosts
| Host | Native entry mechanism | Entry file | Install |
|---|---|---|---|
| DEVIN CLI | user skill (`/alfred`) | `devin-cli/SKILL.md` | turn-key — see `install/` |
| Claude Code | skill / slash command | `claude-code/SKILL.md` | copy to `~/.claude/skills/alfred/SKILL.md` |
| GitHub Copilot | repo custom instructions | `github-copilot/copilot-instructions.md` | copy to `.github/copilot-instructions.md` |
| Codex | `AGENTS.md` | `codex/AGENTS.md` | copy to repo root or `~/.codex/AGENTS.md` |

## The one host-specific setting: model (D46/D14)
The model policy uses abstract tiers (`cheap`/`medium`/`strong`). Each host exposes
different concrete model names, so the **tier → concrete-model map in
`core/model-policy.md`** is the only per-host configuration. If a host cannot
switch models, Alfred uses the default and records which model ran (degrades, D3).

## Degradation
No installer for a host? The integration still works manually: clone the
framework and paste/point the entry file's instructions into the host's
instruction mechanism. The entry files here are short on purpose — the real
content lives once in `core/`.
