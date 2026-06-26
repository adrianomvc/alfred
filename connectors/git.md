# Connector: vcs — git (D23)

- **Type:** vcs. **Status:** standard.
- **Operations:** `create_branch(alfred/<id>)` · `commit(msg)` · `open_pr(develop, branch)`.
- **Hard rule:** NEVER merge into protected branches (develop/main) — merge is human (= acceptance, D23).
- **Commit cadence:** each step/unit (D37); message references `<id-demanda>`.
