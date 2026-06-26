# Glossary (EN <-> pt-BR)

| Term | pt-BR | Meaning |
|---|---|---|
| sigla | sigla | system identifier; 1 HUB per sigla |
| iniciativa | iniciativa | a solution (may be multi-repo) within a sigla |
| demanda | demanda | unit of work; holds `state` + Risk Mode; id `<SIGLA>-<n>` |
| unit | unit | internal execution sub-item of a demand (D24) |
| lane | lane | Risk Mode level: FAST / Standard / SAFE |
| demand-type / stream | tipo de demanda | Produto / Operacional / Engineering |
| HUB | HUB | per-sigla repo with artifacts (source of truth) |
| state | estado | live source of truth of a demand (resume point) |
| connector | conector | access to an external system (contract-based) |
| skill | skill | pluggable capability/knowledge (opt-in, JIT) |
| knowledge | base de conhecimento | always-in-force policies/guardrails |
