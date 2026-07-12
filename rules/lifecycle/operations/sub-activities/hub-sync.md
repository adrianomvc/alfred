---
name: sub-activity-hub-sync
description: Operation sub-activity — HUB Sync
load: sub-activity
triggers:
  phase: operations
  lane: all
  demand-type: all
  agent: all
---

# Operation sub-activity — HUB Sync

> Trigger: the demand ran in **App-only mode** and local work must flow back to
> the HUB. Optional, inside Operation.

## Purpose
Reconcile App-local artifacts and metrics with the HUB so the HUB stays the
single source of governance truth.

## Inputs
App-local `05-operation/008-observability-log.jsonl`, the App `001-index.md`,
the pending `05-operation/009-hub-sync.md` record, the HUB index.

## Steps
1. Collect the **local changes** to sync: metrics rollup, index status, decisions.
2. Open or update `05-operation/009-hub-sync.md` with the pending HUB changes.
3. Apply them to the **HUB** index/metrics (or hand to the HUB owner if access is
   gated).
4. Confirm the App `001-index.md` records the **HUB sync status**.
5. Leave no silent divergence — unsynced items stay listed until applied.

## Output
HUB index/metrics updated from App-local work, with sync status recorded on both
sides.

## Depth by mode
FAST = note local metrics, defer sync · Standard = sync metrics + index · SAFE =
full reconciliation with decisions and evidence.
