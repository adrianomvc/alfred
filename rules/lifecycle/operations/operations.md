# Lifecycle - Operation ("Did it land?")

Close the demand after release/merge with traceability, metrics, and a resumable summary. Owner agent: **Metrics**.

## Steps
1. Confirm release/merge state and link PR/release note.
2. Collect metrics from `05-operation/011-observability-log.jsonl`: elapsed time, phase time, interactions, model/tokens/cost if available, retries, defects, blockers, and acceptance result.
   - In App-only mode, collect local metrics from `05-operation/008-observability-log.jsonl` and leave HUB rollup changes in `05-operation/009-hub-sync.md`.
3. Check baselines and flag drift: too much SAFE, excessive cost, repeated rework, missing post-mortem.
4. Write `summary` and refresh `index` so future sessions load the result without re-reading all artifacts.
   - HUB: update `alfred-docs-hub/index.md` open/closed demand rows, metrics/insights links, and follow-ups.
   - App: update `.alfred-docs-app/<id-iniciativa>/<id-demanda>/001-index.md` reverse-eng status, evidence links, and HUB sync status.
   - Summary: include a short resume note that explains the outcome and where future work should start.
5. If Execution-first was used, complete post-mortem before closure.
6. Send or remind the strategic notification configured in `knowledge/notification.md`; record the action in `audit`.
7. Close `state`; convert follow-ups/debts into new demands.

## Outputs
metrics, summary, updated index, notification record, final state.

## Depth by mode
FAST = short close note and lean metrics. Standard = summary + baseline check. SAFE = complete evidence, post-release watch, and explicit follow-ups.
