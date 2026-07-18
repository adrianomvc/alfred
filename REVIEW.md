# Review Governance

Framework changes use the same governance Alfred requires from consumers.

- FAST: author review plus green required checks.
- Standard: at least one fresh reviewer who did not author the material change.
- SAFE: an independent reviewer or a clean independent review session, with
  security/acceptance evidence retained in the pull request.
- Changes under `core/`, `rules/`, `scripts/shared/`, or schemas require owner
  review. CI is evidence, not a substitute for independent review.
- A stable tag additionally requires protected `main` and five recorded real
  pilots. Until then the version is a release candidate.
