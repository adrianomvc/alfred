# Roadmap

## Now
- Framework Layer 1 is operational and ready to apply to real HUB/App repos.
- HUB/App templates are in place.
- Agent contracts are in place.
- Connector and metrics contracts are in place.
- SQ9 pilot examples are accepted as reference examples under `examples/`.
- Implementation coverage is tracked in `docs/implementation-status.md`.
- Units, escalation triggers, execution plan, and validation evidence are now materialized.
- Layer 1 closure is tracked in `docs/layer-1-framework-closure.md`.
- SQ9 real HUB/App adoption has been exercised with strict validation.
- External environment parameters are now tracked with a reusable HUB template.
- Framework version adoption/freeze rules are documented for HUB/App consumers.
- Framework release governance and changelog are documented.
- Host adapter implementation states and template are documented.
- Connector contract and adapter-shape validation are automated.
- Model-policy validation is automated for lane floors and transparency rules.
- Release `0.1.0` is prepared in `VERSION` and `CHANGELOG.md`.

## Next
- Commit and optionally tag the human-approved `0.1.0` release.
- Complete integrated validation for one real SQ9 demand after required environment parameters are provided.
- Use `04-validate/014-environment-parameters.md` when real accounts, secrets, endpoints, buckets, schemas, or host access are missing.
- Sync app-local work back to the HUB using `05-operation/009-hub-sync.md` when running App-only.
- Validate one Standard or SAFE real demand end to end, including Operation summary and metrics rollup.

## Later
- Add host/connector implementations where a target host and credentials exist.
- Optional telemetry API.
- Optional dashboard over JSONL metrics.
- Model-policy insights ratified by humans.
