# Generated Metrics Rollup

Generated from observability JSONL under `examples` = `D:\Projetos\alfred\examples`.

## Summary
- events: 16
- demands: 6
- tokens input: 0
- tokens output: 0
- cost usd: 0

## By Demand
| Demand | Initiative | Lane | Events | Last phase | Last status | Source |
|---|---|---|---:|---|---|---|
| 001-implantacao-alfred | iniciativa-001-piloto | standard | 4 | operation | closed | `sq9-pilot\alfred-docs-hub\iniciativa-001-piloto\001-implantacao-alfred\05-operation\011-observability-log.jsonl` |
| 001-preparar-alfred | iniciativa-001-onboarding-alfred | standard | 1 | inception | completed | `fresh-sigla-onboarding\alfred-docs-hub\iniciativa-001-onboarding-alfred\001-preparar-alfred\05-operation\011-observability-log.jsonl` |
| 002-simulado-fast | iniciativa-001-piloto | fast | 3 | operation | closed | `sq9-pilot\alfred-docs-hub\iniciativa-001-piloto\002-simulado-fast\05-operation\011-observability-log.jsonl` |
| 003-simulado-safe | iniciativa-001-piloto | safe | 4 | operation | closed | `sq9-pilot\alfred-docs-hub\iniciativa-001-piloto\003-simulado-safe\05-operation\011-observability-log.jsonl` |
| 004-execution-first | iniciativa-001-piloto | safe | 3 | operation | closed | `sq9-pilot\alfred-docs-hub\iniciativa-001-piloto\004-execution-first\05-operation\011-observability-log.jsonl` |
| 005-parallel-units | iniciativa-001-piloto | standard | 1 | design | completed | `sq9-pilot\alfred-docs-hub\iniciativa-001-piloto\005-parallel-units\05-operation\011-observability-log.jsonl` |

## By Lane
| Lane | Events |
|---|---:|
| fast | 3 |
| safe | 7 |
| standard | 6 |

## By Phase
| Phase | Events |
|---|---:|
| design | 3 |
| execution | 1 |
| execution-first | 1 |
| inception | 3 |
| operation | 4 |
| validate | 3 |
| validate-posterior | 1 |

## Gaps
- tokens are not automatically collected in these events
- cost is not automatically collected in these events
- events without model: 14
