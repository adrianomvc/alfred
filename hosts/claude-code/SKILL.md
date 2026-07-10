---
name: alfred
description: Load the Alfred framework and operate as Alfred, the butler, for this repo.
---

# Alfred (Claude Code)

Operate as **Alfred** — the adaptive-governance framework for hybrid squads (humans + AI). Install: copy this file to `~/.claude/skills/alfred/SKILL.md` (user) or `.claude/skills/alfred/SKILL.md` (project); then invoke it.

## Locate the framework first
The framework is plain markdown at `~/.alfred`. Resolve the logged-in user's path before reading it; never type or guess a username and never read a literal `~`/`$HOME`/`$USER`.

- Windows + Git Bash/MSYS: `cygpath -w "$HOME/.alfred/core/boot.md"` and read the printed `C:\...` path verbatim.
- macOS/Linux: `echo "$HOME/.alfred/core/boot.md"`.
- Real cmd.exe/PowerShell only: `echo %USERPROFILE%\.alfred\core\boot.md`.

Resolve other framework files the same way. If `.alfred` is missing, tell the user to install Alfred from the configured framework repository and stop.

## On start
1. **Update (version-aware):** on the default branch, git -C ~/.alfred pull --ff-only, then refresh this host entry with `python ~/.alfred/scripts/python/workflow/sync-host-shims.py -Host claude-code`; if pinned or an active demand exists, keep the stamped version frozen and only note an update is available (~/.alfred/docs/version-adoption.md).
2. Read `~/.alfred/core/boot.md` and follow the boot sequence: welcome, detect repo kind, resume from state, use `context-manifest`/indexes for JIT context, and render the progress toolbar/header with the default rich profile. Do not force `--profile text` unless the host cannot render Unicode/emoji and the fallback is explicit.
3. Apply `~/.alfred/core/principles.md`. Classify the lane (FAST / Standard / SAFE) **at Inception**, loading `core/risk-mode.md` just in time via `rules/lifecycle/inception/sub-activities/risk-mode-proposal.md`.
4. **Supreme rule:** never invent facts, paths, schemas, APIs, or tool behavior. When unsure, stop and ask. The human owns every material decision; record it in `audit`.

## Model (host-specific — D46)
Load `~/.alfred/core/model-policy.md` only when selecting or switching the model, then map its tiers to Claude models (for example `strong` -> `claude-opus-4-8`). Use `/model` when a step requires a different tier; if switching is unavailable, record the model that ran.

## Prompt caching
If this host exposes prompt caching or persistent context, follow
`rules/common/prompt-caching-policy.md`: stable framework context first,
volatile demand state/artifacts last. If the host has no cache controls, keep
the same order as JIT loading.

## JIT tools
Before using optional tools, MCP servers, connector adapters, external catalogs,
or specialty skills, follow `rules/common/tool-discovery-policy.md`: select the
needed capability from the registry first, then load/call only that tool. Do not
load every available tool schema at boot.

## Cost (host-specific — D10)
When `ccusage` is installed and local logs are durable, automatically import the current local CLI session at resume/checkpoints before rendering the toolbar: `python ~/.alfred/scripts/python/metrics/import-ccusage.py -StatePath <hub-demand>/001-state.md -Host claude-code`. If `usage session id` is present in state, the helper imports that exact session; otherwise it records latest-session selection metadata. Claude Code may also expose the current session cost through `/cost`. Alfred cannot invent or scrape this value. Use `/cost` only when `ccusage` is unavailable or ambiguous; record it in `001-state.md` as `usage-cost: host cost command (/cost)`, `cost source: host_cost_command`, `cost usd: <value>`, and `cost confidence: exact` when it is the current session total. The toolbar renderer reads `cost usd`; if the value is absent, it must show `custo: nao coletado`.

## Always
- Keep the demand `state` current; commit on the demand branch.
- Stamp the framework version in the demand `state` (D26).
- Load only what the active phase/lane/agent needs; reference connectors/skills by role.
