# 003-requirements - 006-simulado-adocao-v2

> Perguntas trabalhadas no arquivo (question-format): responda em `[Resposta]:`.

## Perguntas

### Bloqueiam o avanco

#### Q1 — Demandas ativas da sigla migram para 2.0.0?
- Por que: define upgrade in-flight vs congelamento (version-adoption).
- A) Nao; permanecem congeladas na versao carimbada (Recomendado)
- B) Sim, migrar todas agora
- C) A confirmar

[Resposta]: A — permanecem congeladas; so demandas novas carimbam 2.0.0.
- status: respondida

### Podem responder depois

#### Q2 — Registrar ja um catalogo externo (ex.: Context7) na allowlist da sigla?
- Por que: a descoberta sob demanda exige allowlist previa + confirmacao humana.
- A) Adiar ate a primeira necessidade real (Recomendado)
- B) Registrar agora

[Resposta]: A — adiar; registrar quando houver demanda que precise.
- status: respondida

## Requisitos consolidados
- novas demandas da sigla carimbam `framework version: 2.0.0`;
- demandas ativas permanecem congeladas na versao carimbada;
- registro de skills da sigla criado a partir do template do framework;
- ciclo validado com validate-sdd-gate e validate-demand estrito.
