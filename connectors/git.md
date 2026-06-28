# Connector - VCS (Git)

## type
`vcs`

## activation
Available when the host can run git commands in the current repo.

## operations
- `create_branch(id)` creates or checks out `alfred/<id>`.
- `commit(message)` commits scoped artifact/code changes for the demand.
- `open_pr(base, head)` opens a PR through the configured host when available.

## degradation
If commands are unavailable, Alfred records the required action and asks the human to run it.

## audit fields
demand id, branch, commit hash, PR link, human approval/merge reference.

