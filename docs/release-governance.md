# Release Governance

Use this checklist when preparing a new Alfred framework version.

## Version Source
- `VERSION` is the local framework version stamp.
- Release notes live in `CHANGELOG.md`.
- A stable release requires an immutable `vMAJOR.MINOR.PATCH` Git tag. Before
  that tag exists, pilots may pin an reviewed commit and must label it pre-release.
- Do not change HUB/App demand artifacts to create a framework release.

## Version Semantics
Use SemVer-style intent even if the repository is not tagged yet:

| Change type | Bump intent | Examples |
|---|---|---|
| patch | compatible clarification or validation fix | docs wording, stricter fixture validation, non-breaking helper fix |
| minor | compatible new capability | new optional helper, new skill, new template, new connector contract |
| major | breaking framework behavior | artifact path changes, required field changes, observability schema break, lane DoD break |

Pre-1.0 versions may still change quickly. Record compatibility notes explicitly so adopting siglas can decide whether to pin or upgrade.

## Release Checklist
Before a version is announced or tagged:
- update `VERSION` when the version changes;
- update `CHANGELOG.md`;
- run `python scripts/validators/validate-framework.py`;
- confirm docs mention any changed artifact path, required field, lane rule, connector contract, or observability schema;
- record migration notes when existing HUB/App artifacts need manual adjustment;
- keep generated example artifacts parseable and aligned with current validators.
- confirm the required CI check is green and branch protection requires it on
  the release branch; repository administrators record this evidence.

## Human Governance
Only a human decides:
- whether to create a Git tag;
- which branch or commit a sigla adopts;
- whether active demands may upgrade in-flight;
- whether a breaking change is acceptable.

Alfred may propose the release note and compatibility assessment, but it does not publish or force adoption by itself.
Consequently, missing tag or branch-protection evidence keeps the release
candidate open even when local validation is green.

## Release Note Format
Each release note should include:
- version and date;
- summary;
- added;
- changed;
- fixed;
- compatibility notes;
- migration notes;
- validation evidence.

## Adoption Link
After a version is released, consuming HUB/App repos apply `docs/version-adoption.md`.
