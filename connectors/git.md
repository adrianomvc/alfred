# Connector - VCS (Git)

## type
`vcs`

## activation
Available when the host can run git commands in the current repo.

## operations
- `create_branch(id)` creates or checks out `alfred/<id>`.
- `commit(message)` commits scoped artifact/code changes for the demand.
- `open_pr(base, head)` opens a PR through the configured host when available.

## branch model (promotion)
Promotion path is fixed and the AI never crosses a protected boundary:
1. **Demand branch** `alfred/<id>` (or `alfred/<person>/<id>`) — the only branch the AI commits to. Small commits per step/unit, each message references the `id-demanda`.
2. **`develop`** — reached only by a **PR from the demand branch**. This merge **is the Validate acceptance** (the protected branch forces human approval — D23/D7). The AI opens the PR; a human reviews and merges.
3. **`main`** — reached only by **promoting `develop`** as a release step in Operation, following the repo's existing release flow. This is human-owned and outside the demand cycle; the AI never merges into `develop` or `main`.

Both `develop` and `main` are protected. If the repo uses a different stable-branch naming (e.g., `master`, `release/*`), the same two gates apply: demand branch → integration branch (acceptance) → release branch (release).

## HUB vs App protection
The HUB and the App repos use the **same branch-per-demand + PR-merge flow** (Liskov: same VCS role). Protection level differs by blast radius:
- **App repos** — full protection on `develop`/`main`; every merge requires PR + human approval (production code).
- **HUB repo** — protection on the default branch is **recommended but may be lighter**, because the HUB holds markdown artifacts, not production code. Minimum guarantee: merges that touch **shared files** (`001-index.md`, `001-initiative.md`, `skills.md`, knowledge policies) require human review; demand-isolated folders may merge with lighter review. Concurrency on shared files is resolved **in the PR, by a human** (the Orchestrator pulls fresh before writing — D23).

The Framework repo is read-only for demands (pull/clone); it never enters a demand's merge flow.

## degradation
If commands are unavailable, Alfred records the required action and asks the human to run it.

## audit fields
demand id, branch, commit hash, PR link, human approval/merge reference.

