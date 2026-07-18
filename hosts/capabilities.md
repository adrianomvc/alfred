# Host capability matrix

What each host actually offers Alfred as **deterministic** enforcement/observability,
so rules and shims stop guessing. Alfred degrades to advisory markdown on every
host (D3); this table only says where a host *can* make a gate deterministic.

Keep every claim honest by evidence level:
- **product** — documented host feature (cite the doc).
- **config** — must be enabled/configured in the host (off by default).
- **observed** — confirmed in a real session on this machine/org.

Do not upgrade a claim's level without evidence. A `product`-level capability
that has never been run here is not `observed`.

Documentation evidence was last checked on 2026-07-18. Re-check unstable host
claims before changing a contract: Devin CLI configuration, permissions, hooks,
models, and subagents are documented under `https://docs.devin.ai/cli/`; Devin
Enterprise environments under `https://docs.devin.ai/enterprise/environment-management/`.

## Matrix
| Capability | Claude Code | DEVIN CLI | Codex | Copilot | Evidence |
|---|---|---|---|---|---|
| Reads `.claude/` config by default | native | yes (`read_config_from.claude=true`) | no | no | product |
| Shell tool name (hook matcher target) | `Bash` | `exec` | n/a | n/a | product |
| `PreToolUse` hook (+ transparent rewrite) | yes | yes (`hookSpecificOutput.updatedInput`) | no | no | product |
| `PostToolUse` hook | yes | yes | no | no | product |
| `Stop` hook | yes | yes | no | no | product |
| `SessionStart` hook (+ `additionalContext`) | yes | yes | no | no | product |
| `PostCompaction` hook (+ `additionalContext`) | no | yes | no | no | product |
| Force compaction command | no | `/compact` | no | no | product |
| Context-window usage command | no | `/context` | no | no | product |
| Usage/cost command | `/cost` | `/usage` (ACU/credit, estimated) | no | no | product |
| Durable transcript export | session JSONL | `--export` (ATIF) | no | no | product |
| Permission scopes (`Exec/Read/Write/Fetch`) | settings | `.devin/config.json` | no | no | product |
| OS sandbox (blocks scripts outside workspace) | no | `--sandbox` (Linux/macOS) | no | no | product |
| Mid-session model switch | `/model` | `/model` (`opus｜sonnet｜codex｜adaptive`) | varies | no | product |
| Prompt caching | yes | yes (Adaptive keeps model to preserve cache) | varies | n/a | product |
| RTK auto-rewrite fires out of the box | yes (`Bash` preset) | **no** (preset matches `Bash`, tool is `exec`) | no | no | product |

## Load-bearing consequences
- **RTK on DEVIN CLI:** the `PreToolUse` hook exists and `.claude/` is imported,
  but the stock RTK preset targets `Bash`; Devin's tool is `exec`, so the rewrite
  loads and never fires. Explicit `rtk` calls save tokens until a hook entry with
  an `exec` matcher is installed. See `core/hooks/rtk.md`,
  `rules/common/terminal-token-policy.md`.
- **Alfred helpers under sandbox:** `~/.alfred/scripts/**` is outside the project
  workspace. With `--sandbox` enabled (opt-in, but admins can force it org-wide),
  those scripts are blocked unless granted. See `docs/devin-cli-permissions.md`.
- **Duplicate `alfred` skill:** because DEVIN CLI imports `.claude/skills/**`, a
  machine with both host shims installed exposes two `name: alfred` skills. The
  Devin project config sets `read_config_from.claude=false` to avoid loading the
  Claude-Code copy with wrong host instructions.
- **Toolbar rendering:** the DEVIN CLI exposes `unicode_mode` (`auto｜unicode｜
  ascii`) and `theme_mode` (incl. `nocolor`), and does not support cmd.exe
  (conhost). Follow the host's `unicode_mode` instead of guessing: keep the rich
  toolbar profile when it renders Unicode, and only use `render-toolbar.py
  --profile text` when `unicode_mode` is `ascii` or the terminal cannot render it.

## Anti-regression
Do not reintroduce the false claim that the DEVIN CLI has no `PreToolUse` hook or
cannot rewrite transparently. `scripts/validators/validate-token-economy-policy.py`
asserts that claim never reappears in the generated shims or `core/hooks/rtk.md`.
