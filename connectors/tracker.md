# Connector: tracker (D20/D42)

- **Type:** tracker. **Status:** A DEFINIR (Jira/other).
- **Operations:** `get_demand(id) -> {title,desc,type}` · `open_issue(...)`.
- **Use:** source of `id-demanda` (`<SIGLA>-<n>`); enforce "repo via ISSUE" policy (D42) by opening issues instead of inventing paths (D41).
- **Degradation:** human provides the id / opens the issue.
