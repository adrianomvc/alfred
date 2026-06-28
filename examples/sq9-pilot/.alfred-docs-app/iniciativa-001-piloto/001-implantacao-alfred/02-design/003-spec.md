# Spec tecnica - 001-implantacao-alfred

## Link da demanda
`examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/001-implantacao-alfred/001-state.md`

## Solucao tecnica
Usar `examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/001-implantacao-alfred/001-state.md` como fonte de verdade da demanda e `examples/sq9-pilot/.alfred-docs-app/iniciativa-001-piloto/001-implantacao-alfred/` como raiz dos artefatos tecnicos da implantacao.

## Arquivos/componentes afetados
- `alfred-docs-hub/001-index.md`
- `examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/001-initiative.md`
- `examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/001-implantacao-alfred/*`
- `.alfred-docs-app/001-index.md`
- `examples/sq9-pilot/.alfred-docs-app/iniciativa-001-piloto/001-implantacao-alfred/*`
- Regras/templates do framework que mencionam HUB/App/iniciativa.

## Criterios de aceite
- `001-state.md` aponta para todos os artefatos essenciais.
- HUB e App usam as raizes corretas.
- Iniciativa segue `iniciativa-<sequencia>-<iniciativa>`.
- Demanda segue `001-implantacao-alfred`.
- Busca por convencoes antigas nao encontra exemplos obsoletos como convencao vigente.

## Plano de testes
- Rodar busca textual por referencias antigas.
- Listar arquivos em `alfred-docs-hub` e `.alfred-docs-app`.
- Confirmar checklist do `001-state.md`.
