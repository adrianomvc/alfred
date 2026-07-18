# Connector - Codebase Memory

## type
`codebase-memory`

## activation
Optional connector for hosts that can run a local or remote MCP/indexer that
answers structural codebase questions. This is a contract only until a specific
company-approved implementation, package source, and install path are selected.

The installer does **not** install it by default — the download path is blocked
by the corporate proxy; the verified reason and the opt-in condition are
recorded in `install/install.sh` (header comment). To opt in once an approved
download path exists, set `ALFRED_CODEBASE_MEMORY_PACKAGE` (with
`ALFRED_NPM_REGISTRY` for a corporate mirror).
MCP registration remains host-specific until the approved package's command and
tool schema are confirmed.

Use it for brownfield, incident, or multi-repo work where Alfred needs symbol,
reference, call graph, impact, or related-test discovery before reading files.

## operations
- `find_symbol(name, filters)` returns likely definitions with file, line, and
  symbol kind.
- `find_references(symbol_or_path, depth)` returns callers/usages/imports.
- `call_graph(symbol, depth)` returns direct or bounded transitive call paths.
- `impact_analysis(files_or_symbols)` returns likely affected modules, APIs, and
  data contracts.
- `related_tests(symbol_or_file)` returns likely test files or suites.
- `summarize_module(path)` returns a short structural summary of a module.
- `search_symbols(query, path)` returns ranked definitions with signatures and
  estimated retrieval cost.
- `outline_file(path)` returns the current structural outline without bodies.
- `read_symbol(path, symbol)` returns the complete current symbol body.
- `estimate_retrieval_cost(operation)` reports an approximate token cost.
- `freshness(repo_commit, index_commit)` reports `fresh|stale|unknown`.

An implementation remains experimental until 15 benchmark cases show at least
30% median token reduction, 95% target recall, and no correctness/completeness
regression versus `rg` plus bounded reads. Use
`scripts/metrics/evaluate-context-benchmark.py` for the decision.

## degradation
If the connector is unavailable, stale, or not approved for the machine, Alfred
falls back to `rg`, bounded file reads, existing tests, and human-provided
architecture context. The fallback must record that no structural index was
available.

MCP output is evidence, not authority. Before editing, Alfred opens the relevant
source files directly and validates with tests or review evidence.

## audit fields
adapter name, adapter state, index timestamp/version, repo root, query, result
count, files/symbols returned, stale-index warning, fallback used, validation
evidence path.
