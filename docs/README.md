# Docs

## Adoption path
1. Reference this framework repo from the HUB/app process.
2. Create one HUB artifact root: `alfred-docs-hub`.
3. Create `.alfred-docs-app/` in one app repo.
4. Run reverse-engineering for the app.
5. Run a real pilot demand through the 5 phases.

## Acceptance for pilot
- One state in `alfred-docs-hub/<id-iniciativa>/<id-demanda>/` links all app artifacts in `.alfred-docs-app/<id-iniciativa>/<id-demanda>/`.
- Resume works by reading state only.
- FAST does not require formal spec.
- SAFE has decisions and complete audit.
- Metrics are derived from `05-operation/011-observability-log.jsonl`.
- App-only work records local events in `.alfred-docs-app/<id-iniciativa>/<id-demanda>/05-operation/008-observability-log.jsonl` and syncs them to the HUB later.
- Real environment blockers are recorded in `04-validate/014-environment-parameters.md` when external values are missing.

## After pilot
Use [`quickstart-real-demand.md`](quickstart-real-demand.md) to create the first real demand.

## Operational docs
- [`implementation-status.md`](implementation-status.md) tracks coverage against the original planning prompt.
- [`layer-1-framework-closure.md`](layer-1-framework-closure.md) records Layer 1 closure, optional helpers, and external dependencies.
- [`onboarding-sigla.md`](onboarding-sigla.md) describes adoption for a new sigla.
- [`framework-validation.md`](framework-validation.md) validates changes to Alfred itself.
- [`skills-activation.md`](skills-activation.md) explains JIT skill activation and precedence.
- [`host-adapter-readiness.md`](host-adapter-readiness.md) defines what is needed before implementing a concrete host adapter.
- [`adapter-implementation.md`](adapter-implementation.md) defines adapter states and activation rules.
- [`version-adoption.md`](version-adoption.md) defines how HUB/App repos reference, freeze, and upgrade Alfred versions.
- [`release-governance.md`](release-governance.md) defines how framework versions are prepared, validated, and documented.
