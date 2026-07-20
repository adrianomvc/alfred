# 003-requirements - demand draft

> Generated content should be written in pt-BR. This draft becomes the demand's
> `01-inception/003-requirements.md` on `demand start` — from then on it is the
> single source of requirement questions and answers (D18).
> Preencha cada `[Resposta]:` e, depois, informe `pronto` ao Alfred.
> A sigla e derivada automaticamente do nome do repositorio (nunca perguntada).

## Identification

### Qual e o ID da iniciativa? <!-- field: initiative_id; required: true -->
[Alternativas]:
- A) {{initiative_proposal}} (Recomendada)
- B) Outro ID
[Resposta]:

### Qual e o ID definitivo da demanda? <!-- field: demand_id; required: true -->
[Alternativas]:
- A) {{demand_proposal}} (Recomendada)
- B) Outro ID
[Resposta]:

### Quem e a pessoa responsavel (owner) pela demanda? <!-- field: owner; required: true -->
[Resposta]:

## Scope

### Qual problema e resultado esperado? <!-- field: scope; required: true -->
[Alternativas]:
- A) {{scope_proposal}} (Recomendada)
- B) Outro escopo a detalhar
[Resposta]:

### O que esta explicitamente fora do escopo? <!-- field: out_of_scope; required: true -->
[Alternativas]:
- A) Mudancas que nao contribuam diretamente para o resultado descrito. (Recomendada)
- B) Outros limites a detalhar
[Resposta]:

### Qual e o caminho do repositorio App afetado? Responda com o caminho, ou `nenhum` quando a demanda for apenas HUB. <!-- field: target_app; required: true -->
[Resposta]:

## Stream and urgency

### Qual e o tipo da demanda? <!-- field: demand_type; required: true -->
[Alternativas]:
- A) product - funcionalidade ou valor de negocio
- B) operational - incidente, correcao ou operacao
- C) engineering - divida tecnica, migracao ou plataforma
[Resposta]:

### Qual e a urgencia? <!-- field: urgency; required: true -->
[Alternativas]:
- A) normal (Recomendada)
- B) urgente - incidente ou emergencia em andamento
[Resposta]:

## Risk criteria (0/1/2 - core/risk-mode.md)

### Reversibilidade da mudanca? <!-- field: risk_reversibility; required: true -->
[Alternativas]:
- A) 0 - reversivel em minutos
- B) 1 - reversivel com algum esforco
- C) 2 - dificil ou irreversivel
[Resposta]:

### Raio de impacto (blast radius)? <!-- field: risk_blast_radius; required: true -->
[Alternativas]:
- A) 0 - um componente isolado
- B) 1 - alguns componentes ou um sistema
- C) 2 - varios sistemas ou clientes
[Resposta]:

### Dados sensiveis ou regulados? <!-- field: risk_sensitive_data; required: true -->
[Alternativas]:
- A) 0 - nenhum dado sensivel
- B) 1 - contato indireto ou limitado
- C) 2 - dados sensiveis/regulados diretamente
[Resposta]:

### Impacto no cliente? <!-- field: risk_customer_impact; required: true -->
[Alternativas]:
- A) 0 - nenhum impacto direto
- B) 1 - impacto limitado ou interno
- C) 2 - impacto direto no cliente
[Resposta]:

### Risco financeiro ou de custo? <!-- field: risk_cost; required: true -->
[Alternativas]:
- A) 0 - irrelevante
- B) 1 - moderado
- C) 2 - alto ou dificil de estimar
[Resposta]:

## Complexity criteria (0/1/2 - core/risk-mode.md)

### Quantos componentes sao afetados? <!-- field: cx_components; required: true -->
[Alternativas]:
- A) 0 - um componente
- B) 1 - alguns componentes
- C) 2 - muitos componentes ou sistemas
[Resposta]:

### Qual o grau de novidade tecnica? <!-- field: cx_novelty; required: true -->
[Alternativas]:
- A) 0 - padrao conhecido
- B) 1 - parcialmente novo
- C) 2 - abordagem inedita para o time
[Resposta]:

### Qual a ambiguidade dos requisitos? <!-- field: cx_ambiguity; required: true -->
[Alternativas]:
- A) 0 - requisitos claros
- B) 1 - pontos em aberto
- C) 2 - requisitos vagos ou em disputa
[Resposta]:

### Quantas integracoes estao envolvidas? <!-- field: cx_integrations; required: true -->
[Alternativas]:
- A) 0 - nenhuma
- B) 1 - uma ou duas
- C) 2 - varias ou criticas
[Resposta]:

### Qual o esforco estimado? <!-- field: cx_effort; required: true -->
[Alternativas]:
- A) 0 - horas
- B) 1 - dias
- C) 2 - semanas ou mais
[Resposta]:

### Ha gatilhos de override? Combine letras quando houver mais de um (ex.: B,C). <!-- field: hard_overrides; required: true -->
[Alternativas]:
- A) nenhum (Recomendada)
- B) mudanca arquitetural
- C) multi-squad
[Resposta]:

## Governance

### Quais artefatos adicionais sao necessarios? Use `nenhum` quando a lane for suficiente. <!-- field: artifact_set; required: true -->
[Alternativas]:
- A) Apenas os artefatos obrigatorios da lane. (Recomendada)
- B) Acrescentar artefatos especificos listados na resposta.
[Resposta]:

## Perguntas adicionais

<!-- O Alfred acrescenta aqui novas perguntas materiais. Nenhuma resposta deve existir apenas no chat. -->
