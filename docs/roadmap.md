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
- SQ9 simulated HUB/App adoption has been exercised with strict validation.
- External environment parameters are now tracked with a reusable HUB template.
- Framework version adoption/freeze rules are documented for HUB/App consumers.
- Framework release governance and changelog are documented.
- Host adapter implementation states and template are documented.
- Connector contract and adapter-shape validation are automated.
- Model-policy validation is automated for lane floors and transparency rules.
- Releases `0.1.0` through `0.4.0` are shipped (`VERSION`, `CHANGELOG.md`); the v0.2 line added Python helpers, the DEVIN installer, per-type playbooks, the knowledge subsystem, presentation profiles, AI-DLC Design sub-activities, and the `property-based-testing` opt-in skill exercised by dogfooding. `0.3.0` added full lifecycle sub-activity parity, the markdown-SOLID directory pass, the `validate-links` reference checker, and sandbox connector simulators. `0.4.0` added the `hosts/` per-host entry points (DEVIN CLI, Claude Code, Copilot, Codex).

## Next
- Execute `docs/plan/implementation-plan-2.0.0.md` wave by wave; all of it lands under version `2.0.0` (no bumps per wave).
- Complete integrated validation for one real SQ9 demand after required environment parameters are provided.
- Use `04-validate/014-environment-parameters.md` when real accounts, secrets, endpoints, buckets, schemas, or host access are missing.
- Sync app-local work back to the HUB using `05-operation/009-hub-sync.md` when running App-only.
- Validate one Standard or SAFE real demand end to end, including Operation summary and metrics rollup.

## Later
- Add host/connector implementations where a target host and credentials exist.
- Optional telemetry API.
- Optional dashboard over JSONL metrics.
- Model-policy insights ratified by humans.
