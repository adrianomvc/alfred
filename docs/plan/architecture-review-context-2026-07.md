# Revisão de arquitetura — otimização de contexto/tokens (2026-07)

## Resumo executivo
A revisão confirmou que a estratégia JIT do Alfred estava correta, mas o custo
fixo de sessão ainda carregava conteúdo estável, apresentação e políticas cedo
demais. A solução aplicada preserva D3 (markdown puro, sem dependência de host)
e troca duplicação por metadados, registries gerados, manifestos mínimos e shims
de host gerados por template.

Resultado arquitetural esperado:

| Carga | Antes | Depois alvo |
|---|---:|---:|
| Início de sessão | ~8.230 tk | ~3.300 tk (-60%) |
| Adicional por demanda | ~2.630 tk | ~2.100 tk |
| Demanda de 5 sessões | ~43,8k tk | ~20,5k tk (-53%) |

Esses números são baseline de planejamento, não medição exata de tokenizer de
host. A linha viva está em [`metrics/baselines.md`](../../metrics/baselines.md).

## Diagnóstico
O custo vinha de quatro fontes:

- boot carregando apresentação e políticas que só são usadas em eventos raros;
- regras e contratos repetidos em vários arquivos;
- `rules/` e `knowledge/` sem metadados computáveis para seleção mínima;
- shims de host quase iguais, mantidos manualmente.

Principais observações:
- `welcome.md` misturava persona com tela rica;
- `risk-mode.md` só precisa entrar na Inception;
- `model-policy.md` só precisa entrar na escolha/troca de modelo;
- lei suprema, layout de artefatos, gates de catálogo e terminologia tinham fontes duplicadas;
- os quatro shims de host carregavam o mesmo núcleo com pequenas diferenças.

## Estratégia aplicada
O trabalho foi dividido em fases pequenas, cada uma validada nos dois runtimes:

| Fase | Entrega |
|---|---|
| 0 | Higiene de worktrees/cache local e log de handoff |
| 1 | Single-sourcing de lei suprema, layout, terminologia, gates e README de rules |
| 2 | Dieta do kernel: welcome split, risk/model JIT, toolbar quick |
| 3 | Frontmatter em rules, registry de knowledge, skills enxutas, registries gerados |
| 4 | `context-manifest` nos dois runtimes com fixtures |
| 5 | Shims de host gerados por template, com drift-check |
| 6 | Ordem cache-friendly e baselines em metrics |

## Estratégias rejeitadas
- **RAG obrigatório:** aumentaria dependência operacional e quebraria a degradação
  para markdown puro. Alfred precisa funcionar sem índice externo.
- **Grafo obrigatório:** útil como evolução, mas pesado para o problema atual; os
  metadados em frontmatter resolvem a seleção mínima sem runtime novo.
- **Sumarização por LLM:** reduziria tokens, mas introduziria variação e risco de
  perda de regra. O framework precisa ser reproduzível.
- **Mega-prompt:** simplifica o boot, mas concentra custo fixo e piora cache.
- **Orquestração adaptativa complexa:** prematura sem métricas reais suficientes;
  o `context-manifest` entrega a seleção mínima com fallback manual.

## Arquitetura recomendada
O caminho recomendado é manter JIT como contrato principal:

1. Kernel estável primeiro: princípios, boot, índices.
2. Manifestos e registries para escolher arquivos, não para substituir markdown.
3. Regras por evento: phase/lane/demand type/agent/sub-activity.
4. Skills carregadas por frontmatter e ativação observada.
5. Estado e artefatos voláteis por último.

Essa ordem melhora cache quando o host oferece caching e continua legível quando
o host não oferece nada especial.

## Fluxo em níveis 0–7
| Nível | Contexto | Quando carregar |
|---|---|---|
| 0 | `core/principles.md` e `core/boot.md` | início da sessão |
| 1 | índices (`README.md`, `rules/rules-index.md`, `skills/skills.md`) | seleção JIT |
| 2 | `state` da demanda | retomada ou nova demanda |
| 3 | lane + demand type | início/classificação da demanda |
| 4 | fase atual | entrada de fase |
| 5 | sub-atividade | trabalho específico |
| 6 | skills ativas | quando gatilho observado existe |
| 7 | políticas/eventos raros (`risk-mode`, `model-policy`, knowledge) | só no evento |

## Riscos e trade-offs
- Frontmatter adiciona metadado a muitos arquivos, mas evita carregar pastas
  inteiras e permite drift-check.
- Registries gerados exigem disciplina: editar fonte, regenerar e validar.
- Shims de host ficam menores, mas mudanças host-specific devem passar pelo delta
  em `hosts/_template/hosts.json`.
- A medição atual é baseline arquitetural; medições reais dependem de exports dos
  hosts e continuam em `metrics/`.

## Evidência de validação
Cada fase foi validada com:

- `python scripts/python/validators/validate-framework.py -Root .`
- `python scripts/python/validators/validate-framework.py -Root .`

O fechamento também preserva:
- link validation limpo dentro de `validate-framework`;
- fixtures do `context-manifest` nos dois runtimes;
- drift-check de registries e shims gerados.

## Roadmap
Próximos passos fora deste pacote:

- coletar medições reais de hosts quando exportáveis;
- promover adapter de e-mail de `dry-run` para `active` quando houver SMTP e dono;
- fechar demanda real integrada da Wave 4;
- evoluir métricas/insights a partir de dados reais, não de baseline planejado.

## Recomendação final
Considerar o pacote de otimização de contexto fechado. A arquitetura agora reduz
o custo fixo sem criar dependência de host, preserva markdown como fonte de
verdade e deixa os pontos variáveis atrás de metadados e helpers opcionais.
