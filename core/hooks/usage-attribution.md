# Usage Attribution Hook

Optional Claude Code hook that stamps exact request token usage into a raw
technical log, an Alfred demand observability log, or both. It supports the
usage-cost connector; it is not a source of truth by itself and not a framework
dependency.

## Why a hook (the layered design)
Per-event `tokens`/`cost` are `null` on hosts that do not expose per-interaction
usage in-band (`metrics/metrics.md` → Event hygiene). Usage is recovered in
layers, each more faithful and less in-band:

- **Layer 1 — window attribution.** `scripts/python/metrics/attribute-usage-transcript.py --granularity window` sums transcript requests into windows bounded by consecutive Alfred event timestamps. Needs real, distinct event `ts` (Layer 0).
- **Layer 2 — request attribution.** `--granularity request` emits one event per transcript request, id `usage-request-<requestId>`, tagged with the enclosing Alfred event. Legacy `--granularity turn` remains an alias for request, not proof of one human turn.
- **Layer 3 — interaction aggregation.** `--emit-interactions` derives `interaction_completed` from request events when the transcript exposes `promptId` or a user boundary.
- **Layer 4 — this hook.** The layer that owns the usage object stamps it, not the in-band agent. Claude Code Stop/SubagentStop hooks pass `transcript_path`; the transcript holds exact usage per request. The hook runs request attribution incrementally.

Tokens are exact (de-duplicated by `requestId` — a request may span transcript
lines that repeat the same usage). Human interaction ids are exact only when the
host exposes `promptId`; otherwise they are derived from user boundaries or left
unavailable with `interaction_confidence` and `correlation_method`. Cost is not
in the transcript: it stays `null` unless a separate interaction-level cost
source or approved `usage-rate-card` is applied. A ccusage or `/cost` session
total belongs in `001-state.md` for toolbar display, not in the interaction JSONL log.

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

Optional raw technical log:
- `AI_OBS_RAW_LOG` — JSONL outside the demand, for example
  `/var/log/ai-agent-observability/claude-code.jsonl` or a local path.
- `AI_OBS_CURSOR_DIR` — cursor directory; default `~/.alfred/runtime/cursors`.
- `AI_OBS_MODE=raw|alfred|both` — default is `both` when both raw and Alfred
  destinations exist, otherwise the configured destination.
- `AI_OBS_PROVIDER=claude-code`, `AI_OBS_PROJECT`, `AI_OBS_TEAM`,
  `AI_OBS_ENVIRONMENT` — optional metadata.

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
- Incremental: stores per-transcript cursors with `last_byte_offset` and resets
  safely on corruption, truncation, or rotation.
- Privacy-preserving: raw logs contain metadata, ids, token counts, tool names,
  redacted paths, hashes, and counters; not prompt/response/file contents.
- Policy snapshot: when an Alfred destination is available, the hook appends one
  idempotent session-scoped `artifact_accessed` event with version/commit and
  hashes for the core model/usage/context policies. It records references and
  hashes only, never policy content.
- Non-blocking: exits `0` on every path. A missing target or any error is written
  to stderr and ignored — the session is never blocked.
- Current installer wires the supported `Stop` hook. `SessionEnd` is not added
  until the host configuration support is confirmed; run the transcript helper
  manually at close as the flush fallback.

## Degradation
The transcript is written asynchronously and may lag the current turn, so the
final turn is captured on the next Stop or at close. If the hook cannot resolve a
target, nothing is written; run
`scripts/python/metrics/attribute-usage-transcript.py` manually at close, and
keep the ccusage session import (`connectors/usage-cost.md`) as the session-total
toolbar backstop. Apply `scripts/python/metrics/apply-usage-rate-card.py` only
when an approved rate card prices exact interaction usage; it appends
`usage_cost_attributed` events instead of editing the token event. Record the
limitation only when it affects validation, evidence, or a human decision.
