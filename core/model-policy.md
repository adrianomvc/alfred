# Model Policy (D46)
# Effective model = max(risk floor by lane, stage adjustment).
# Declared source of truth; changes = human commit. Alfred SUGGESTS tuning from metrics (D43), never auto-applies.
# Each cell may be a TIER (cheap/medium/strong) OR a fixed model id (both forms).

## 1. Tier -> real model per host (D14)   <-- MAIN CUSTOMIZATION POINT
| Tier   | DEVIN           | Claude CLI         | GitHub Copilot  |
|--------|-----------------|--------------------|-----------------|
| cheap  | <model>         | claude-haiku-4-5   | <model>         |
| medium | <model>         | claude-sonnet-4-6  | <model>         |
| strong | <model>         | claude-opus-4-8    | <model>         |

## 2. Floor per lane (risk) — never go below
| Lane     | Min tier |
|----------|----------|
| FAST     | cheap    |
| Standard | medium   |
| SAFE     | strong   |

## 3. Stage adjustment (rises above floor, never below) — value = tier OR fixed model
| Phase/agent/type             | Value           | Kind          |
|------------------------------|-----------------|---------------|
| Design · spec-design         | +1 tier         | relative tier |
| Design · architecture · SAFE | claude-opus-4-8 | fixed model   |
| Execution · boilerplate      | cheap           | fixed tier    |
| Execution · complex logic    | +1 tier         | relative tier |
| Validation · reviewer        | medium          | fixed tier    |
| Operation · metrics          | claude-haiku-4-5| fixed model   |

## 4. Rules
# - Effective = max(lane floor, stage adjust). If a fixed model is below the floor -> warn trade-off (do not block, D7).
# - Model change between stages is ANNOUNCED to the person (toolbar, pt-BR) + audit event (D45).
# - User may choose/change the model anytime (one-off or pinned); recorded in state/audit.
# - Host lacking a tier -> use fallback (D3). Toolbar shows the current model.
