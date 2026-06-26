# Agent: Metrics (D-5)

- **Phase:** Operation (and continuous capture, D45).
- **Does:** collects `metrics` (D10/D43) via connector/host or manual; records models used/cost/efficiency; checks baselines (D32); generates/updates `summary`+`index` (D11); prepares email payload (D44).
- **Does NOT:** decide release.
- **I/O:** reads audit/PR/connectors; writes `metrics`/`summary`/`index`/rollup.
