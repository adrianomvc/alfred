# Usage Attribution Hook

Optional Claude Code hook that stamps exact per-turn token usage into a demand's
observability log out-of-band. It supports the usage-cost connector; it is not a
source of truth by itself and not a framework dependency.

## Why a hook (the layered design)
Per-event `tokens`/`cost` are `null` on hosts that do not expose per-interaction
usage in-band (`metrics/metrics.md` → Event hygiene). Usage is recovered in
layers, each more faithful and less in-band:

- **Layer 1 — window attribution.** `scripts/python/metrics/attribute-usage-transcript.py --granularity window` sums transcript requests into windows bounded by consecutive Alfred event timestamps. Needs real, distinct event `ts` (Layer 0).
- **Layer 2 — per-turn attribution.** `--granularity turn` emits one event per transcript request, id `usage-turn-<requestId>`, tagged with the enclosing Alfred event.
- **Layer 3 — this hook.** The layer that owns the usage object stamps it, not the in-band agent. Claude Code Stop/SubagentStop hooks pass `transcript_path`; the transcript holds exact usage per request. The hook runs Layer 2 incrementally.

Tokens are exact (de-duplicated by `requestId` — a request spans several
transcript lines that repeat the same usage). Cost is not in the transcript: it
stays `null` unless a separate interaction-level cost source is approved. A
ccusage or `/cost` session total belongs in `001-state.md` for toolbar display,
not in the interaction JSONL log.

## Supported host
Claude Code. Other hosts without a durable transcript use the ccusage import or a
manual `/cost` value instead.

## Setup
Add to Claude Code `settings.json`. Resolve `~/.alfred` to an absolute path
first (never a literal `~`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python <abs>/.alfred/scripts/python/metrics/claude-code-usage-hook.py"
          }
        ]
      }
    ]
  }
}
```

Point the hook at the active demand log via environment:
- `ALFRED_STATE_PATH` — the demand `001-state.md` (log derived at `05-operation/011-observability-log.jsonl`), or
- `ALFRED_OBS_LOG` — an explicit observability JSONL path.
- Optional `ALFRED_RUN_ID=<id>`.

If the environment is not set, render the toolbar with `-RegisterActive` first:

```bash
python ~/.alfred/scripts/python/workflow/render-toolbar.py -StatePath <demand>/001-state.md -RegisterActive
```

That writes `~/.alfred/runtime/active-demand.json`, which the Stop hook reads as
the fallback target.

To install the hook while refreshing the Claude Code host entry:

```bash
python ~/.alfred/scripts/python/workflow/sync-host-shims.py -Host claude-code -Create -InstallHooks
```

## Behavior
- Idempotent: re-runs every Stop but skips `requestId`s already attributed, so no
  duplicates accumulate.
- Non-blocking: exits `0` on every path. A missing target or any error is written
  to stderr and ignored — the session is never blocked.

## Degradation
The transcript is written asynchronously and may lag the current turn, so the
final turn is captured on the next Stop or at close. If the hook cannot resolve a
target, nothing is written; run
`scripts/python/metrics/attribute-usage-transcript.py` manually at close, and
keep the ccusage session import (`connectors/usage-cost.md`) as the session-total
toolbar backstop. Record the limitation only when it affects validation,
evidence, or a human decision.
