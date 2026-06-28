# Version Adoption

Use this policy when a HUB or App repo adopts, updates, or freezes an Alfred framework version.

For producing a new framework version, use `docs/release-governance.md`.

## Goals
- Keep the framework as a single source of truth.
- Avoid copying framework files into HUB or App repos.
- Make every demand reproducible by recording the Alfred version, ref, and commit used.
- Prevent silent framework changes in the middle of an active demand.

## Reference Modes
Alfred is markdown-first and host-agnostic, so the reference mechanism is chosen by the adopting context:

| Mode | Use when | Required record |
|---|---|---|
| tag pin | the sigla wants stable releases | `framework version`, `framework ref`, `framework commit` |
| commit pin | the sigla needs exact reproducibility | `framework version`, `framework ref`, `framework commit` |
| branch tracking | the sigla accepts frequent updates | `framework version`, `framework ref`, `framework commit`, update decision |
| manual path | the framework is mounted locally | absolute or relative path, `framework version`, `framework commit` if available |

The reference mode is an adoption detail. Lifecycle rules must not depend on a specific Git, CI, IDE, or host feature.

## Freeze Rule
When a demand starts, stamp the current framework version/ref/commit in:
- HUB `001-state.md`;
- HUB `05-operation/008-metrics.md`;
- HUB `05-operation/007-audit.md`;
- App `001-index.md` when App artifacts exist;
- App `05-operation/006-metrics.md` when App metrics exist;
- JSONL events under the `alfred` object.

That version remains frozen until the demand closes unless a human explicitly approves an in-flight upgrade.

## Upgrade Rule
During boot, if the local framework differs from the stamped demand version:
- with no active demand: use the current framework and record the version;
- with an active demand: warn the human and ask whether to keep the frozen version or upgrade now;
- if upgraded in-flight: append an audit event, append a JSONL event, update state/metrics, and record the reason.

Do not silently upgrade an active demand because it changes the governing rules after work has started.

## Compatibility Check
Before adopting a new framework version for an active or new demand, check:
- naming/layout changes for HUB and App artifacts;
- observability schema changes;
- required artifact changes for the active lane;
- new blocker rules or escalation triggers;
- changed skill or connector contract requirements.

If any item changes materially, record the adoption note in the HUB index or demand audit before continuing.

## Degradation
If Git metadata is unavailable, record:
- `framework version`: value from `VERSION` if available, otherwise `unknown`;
- `framework ref`: local path or `not-git`;
- `framework commit`: `not-git` or `unknown`;
- audit note explaining why the exact reference could not be verified.

Unknown metadata is acceptable only when it is explicit. It must not be hidden or guessed.
