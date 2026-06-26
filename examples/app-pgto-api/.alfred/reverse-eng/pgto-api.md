# Reverse engineering — pgto-api (S1/D21)
- Commit analisado: a1b2c3d · data: 2026-06-20
- Negócio: processa pagamentos; expõe API REST.
- Arquitetura: camadas controller/service/repository (Java/Spring).
- Integração: ledger de conciliação via evento.
- Áreas de risco: arredondamento monetário.
