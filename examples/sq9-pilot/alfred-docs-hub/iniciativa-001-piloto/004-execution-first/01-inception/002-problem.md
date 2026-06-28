# Problema - 004-execution-first

## Contexto
Simulado operacional para validar o fluxo Execution-first do Alfred. O caso representa um incidente/hotfix com urgencia alta, onde estabilizar vem antes da documentacao completa.

## Problema
Um erro simulado impede a retomada por `001-state.md` em um app critico. O risco operacional exige estabilizacao imediata e registro posterior completo.

## Objetivo
Validar que o Alfred consegue:
- autorizar estabilizacao minima;
- executar primeiro;
- registrar audit durante a urgencia;
- completar Inception, Design, Validate e post-mortem depois.

## Escopo
- Criar artefatos de incidente `004-execution-first`.
- Registrar investigacao tecnica.
- Registrar decisoes e audit completo.
- Fechar com post-mortem.

## Fora de escopo
- Conectar em observabilidade real.
- Alterar codigo de app real.
- Enviar notificacao externa real.

## Riscos / duvidas
- Sem conector de logs real, a evidencia e simulada/manual.
- O fluxo de emergencia nao pode virar atalho para pular post-mortem.

