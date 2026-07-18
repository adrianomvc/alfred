# Requirements — <id-demanda>

> Framework template — generate content in pt-BR. Canonical path (HUB):
> `<id-iniciativa>/<id-demanda>/01-inception/003-requirements.md`.
> This is the single place for the demand's question list (D18).

Sigla: <sigla> · Iniciativa: <id-iniciativa> · Modo proposto: <FAST | Standard | SAFE>
Progresso: <respondidas>/<total> respondidas · <n> bloqueiam o avanço para Design
Como responder: edite a linha `[Resposta]:` de cada pergunta neste arquivo. Depois de salvar, avise no chat com `pronto` ou `terminei` para eu continuar.

## Requisitos funcionais
- <...>

## Requisitos não funcionais
- <...>

## Perguntas
Regras: uma decisão por pergunta · quantidade de opções conforme a dúvida real · escolha única usa letras por padrão e segue AI-DLC · múltipla seleção é extensão Alfred: usa `[ ]`/`[x]` sem letras e deve dizer `selecione uma ou mais` · `(Recomendada)` **apenas orienta**, nunca preenche a resposta · não inventar opção (na dúvida, use "Outra / A confirmar").
Status por pergunta: `◻ aberta` · `✓ respondida` · `⚠ contradição`.

### 🔴 Bloqueiam o avanço

#### Q1 — <pergunta clara e específica?>            ◻ aberta
Por quê: <o que esta resposta destrava — ex.: blast radius / Risk Mode>.
- A) <opção> (Recomendada)
- B) <opção alternativa>
- C) Outra / A confirmar

[Resposta]:

### 🟡 Podem responder depois (não bloqueiam)

#### Q2 — <pergunta?>                                ◻ aberta
Por quê: <impacto>.
- A) <opção>
- B) Outra / A confirmar

[Resposta]:

## Gate
Não avanço para Design enquanto as perguntas 🔴 não forem respondidas e validadas.
Ao ler as respostas, detectar contradição/ambiguidade e gerar pergunta de follow-up.

## Contradições / pendências
- <nenhuma | descrição do conflito detectado>

> Piso (D3): sem emoji, `🔴/🟡` viram `[!]/[.]` e `◻/✓/⚠` viram `[ ]/[x]/(!)`; mesmo conteúdo.
