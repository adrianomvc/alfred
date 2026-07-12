# Generated Metrics Rollup

Generated from observability JSONL under `examples` = `D:\Projetos\alfred\examples`.

## Summary
- events: 15 effective / 15 raw
- demands: 3
- interactions observed: 7
- requests observed: 1
- usage events: 1
- cost events: 1
- tokens input: 18000
- tokens cache creation: 4000
- tokens cache read: 22000
- tokens output: 1200
- tokens processed: 45200
- cache reuse ratio: 50.0%
- cost usd: US$ 0.0842

## By Demand
| Demand | Events | Usage events | Cost events | Cost | Input | Cache created | Cache reused | Output | Cache reuse |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 001-preparar-alfred | 2 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |
| 006-simulado-adocao-v2 | 6 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |
| example-demand | 7 | 1 | 1 | US$ 0.0842 | 18000 | 4000 | 22000 | 1200 | 50.0% |

## By Phase
| Phase | Events | Usage events | Cost events | Cost | Input | Cache created | Cache reused | Output | Cache reuse |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| design | 6 | 1 | 1 | US$ 0.0842 | 18000 | 4000 | 22000 | 1200 | 50.0% |
| execution | 1 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |
| inception | 2 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |
| operation | 4 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |
| validate | 2 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |

## By Lane
| Lane | Events | Usage events | Cost events | Cost | Input | Cache created | Cache reused | Output | Cache reuse |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Standard | 7 | 1 | 1 | US$ 0.0842 | 18000 | 4000 | 22000 | 1200 | 50.0% |
| standard | 8 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |

## By Model
| Model | Events | Usage events | Cost events | Cost | Input | Cache created | Cache reused | Output | Cache reuse |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-5 | 1 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |
| claude-example | 2 | 1 | 1 | US$ 0.0842 | 18000 | 4000 | 22000 | 1200 | 50.0% |
| claude-fable-5 | 6 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |
| unknown | 6 | 0 | 0 | US$ 0.0000 | 0 | 0 | 0 | 0 | n/a |

## By Artifact
| Artifact | Type | Interactions | Reads | Repeated unchanged reads | Avg size | Phases | Models | Avg interaction cost |
|---|---|---:|---:|---:|---:|---|---|---:|
| `001-index.md` | documentation | 1 | 1 | 0 | n/a | operation | claude-fable-5 | n/a |
| `001-state.md` | state | 2 | 0 | 0 | n/a | execution, inception | GPT-5, claude-fable-5 | n/a |
| `01-inception/002-problem.md` | problem | 1 | 0 | 0 | n/a | inception | claude-fable-5 | n/a |
| `01-inception/002-reverse-eng.md` | documentation | 1 | 0 | 0 | n/a | operation | claude-fable-5 | n/a |
| `01-inception/003-requirements.md` | requirements | 1 | 0 | 0 | n/a | inception | claude-fable-5 | n/a |
| `01-inception/004-risk.md` | risk | 1 | 0 | 0 | n/a | inception | claude-fable-5 | n/a |
| `01-inception/005-tech-inception.md` | documentation | 1 | 0 | 0 | n/a | inception | claude-fable-5 | n/a |
| `02-design/006-decisions.md` | decisions | 1 | 0 | 0 | n/a | design | claude-fable-5 | n/a |
| `03-execution/012-execution-plan.md` | execution_plan | 1 | 0 | 0 | n/a | design | claude-fable-5 | n/a |
| `04-validate/013-validation-evidence.md` | validation_evidence | 1 | 0 | 0 | n/a | validate | claude-fable-5 | n/a |
| `05-operation/005-audit.md` | documentation | 1 | 0 | 0 | n/a | operation | claude-fable-5 | n/a |
| `05-operation/006-metrics.md` | documentation | 1 | 0 | 0 | n/a | operation | claude-fable-5 | n/a |
| `05-operation/008-metrics.md` | metrics | 1 | 0 | 0 | n/a | operation | claude-fable-5 | n/a |
| `05-operation/009-summary.md` | summary | 1 | 0 | 0 | n/a | operation | claude-fable-5 | n/a |
| `docs/onboarding-sigla.md` | documentation | 1 | 1 | 0 | n/a | inception | GPT-5 | n/a |
| `sha256:2200e24eea7afd7174706a6d1b8a7a98ddc3a2d04bf0e3940fd22adaa1fd3f28` | framework_policy | 1 | 2 | 1 | 4280 | design | claude-example | US$ 0.0842 |

## Data Quality
- events with session id: 14 / 15 (93.3%)
- events with interaction id: 13 / 15 (86.7%)
- events with model: 9 / 15 (60.0%)
- usage events with exact tokens: 1 / 1 (100.0%)
- cost events with cost: 1 / 1 (100.0%)
- events with artifact metadata: 10 / 15 (66.7%)
- events with outcome: 1 / 15 (6.7%)

## Gaps
- events without model: 6