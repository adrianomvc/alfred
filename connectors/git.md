# Connector: vcs — git

- **Type:** vcs. **Status:** standard.
- **Operations:** `create_branch(alfred/<id>)` · `commit(msg)` · `open_pr(develop, branch)`.
- **Hard rule:** NEVER merge into protected branches (develop/main) — merge is human (= acceptance).
- **Commit cadence:** each step/unit ; message references `<id-demanda>`.
