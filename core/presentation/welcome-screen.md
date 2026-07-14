# Welcome screen (rendered block)

The visual welcome shown once per session. **Load this file only when rendering
the welcome** — the persona/voice lives in `core/welcome.md` and is all a session
needs otherwise (token economy, JIT). Keep it to ~1 screen; clarity above character.

The open-demands table is filled by boot from the real `state`/`index` — **never
invent** (the rows below are illustrative; with no open demands, show only the
"iniciar nova" row). The block below is the **rich** rendering (Unicode box +
emoji; the rich-cli profile adds ANSI color). It **degrades** per `## Degradação`
for hosts without Unicode/emoji/color.

```text
  ╭────────────────────────────────────────────────────────────────╮
  │   🎩  A L F R E D   ·   seu mordomo de demandas                  │
  ╰────────────────────────────────────────────────────────────────╯
   Às ordens. Eu preparo o terreno, proponho e registro
   tudo — e conduzo cada demanda no nível certo de processo.
   Você decide; eu nunca decido no seu lugar.

   O ciclo, da intenção à entrega:
  ┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
  │ 1 Inception │ 2 Design    │ 3 Execution │ 4 Validate  │ 5 Operation │
  │    O quê    │    Como     │    Fazer    │   Validar   │   Operar    │
  └─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘

   O rigor eu proponho pelo risco — você confirma:
  ┌────┬──────────┬───────┬──────────────────────────────────────────┐
  │    │ Modo     │ Risco │ O que muda                                 │
  ├────┼──────────┼───────┼──────────────────────────────────────────┤
  │ 🟢 │ FAST     │ baixo │ enxuto, autonomia, poucos checkpoints      │
  │ 🟡 │ Standard │ médio │ spec + critérios de aceite + revisão       │
  │ 🔴 │ SAFE     │ alto  │ governança forte, rollback, aprovações     │
  └────┴──────────┴───────┴──────────────────────────────────────────┘
   🚨 emergência (incidente/hotfix) não é modo, é caminho: estabilizo
      já e formalizo Inception/Design depois (post-mortem).

  ╭────────────────────────────────────────────────────────────────╮
  │  🛡️  Você decide.  Eu nunca invento — na dúvida, pergunto.        │
  ╰────────────────────────────────────────────────────────────────╯

   Em aberto nesta sigla — responda com o número para retomar:
  ┌───┬──────────────────────────────┬───────────┬──────────┬───────────┐
  │ # │ Demanda                      │ Fase      │ Modo     │ Situação  │
  ├───┼──────────────────────────────┼───────────┼──────────┼───────────┤
  │ 1 │ #142 novo split de pagamento │ Design    │ Standard │ em espera │
  │ 2 │ #097 ajuste na fila de envio │ Execution │ FAST     │ em espera │
  │ 3 │ ✦ iniciar uma nova demanda   │ —         │ —        │ —         │
  └───┴──────────────────────────────┴───────────┴──────────┴───────────┘
   ↳ responda com o número, ou descreva uma nova demanda.
```

The welcome never marks a current phase. Phase status belongs only to the
demand toolbar rendered from `001-state.md`.

## Degradação (D3 — piso portável)
Nothing here may be required. The rich block degrades by rules, not by a second copy:
- **Markdown host (fence rule — do this first):** when the reply is rendered as markdown (Devin, web/chat UIs, IDE panels — most hosts today), paste the whole block **inside a fenced code block** (```). Without the fence, markdown collapses repeated spaces and soft-wraps long lines, so every border and column breaks. This is orthogonal to the character-set rules below (`core/presentation/README.md` → *Markdown-safe rendering*): fence first, then apply the Unicode/emoji/color degradation.
- **No color (ANSI):** the rich-cli profile adds color; without it the same text reads fine (the mode names carry the meaning). Color never affects alignment (ANSI has zero display width).
- **No emoji / narrow terminal:** drop the icon column of the modes table; replace `🎩`→`[Alfred]`, the mode dots → the `FAST/Standard/SAFE` text already in the row, callout box → a `>` line.
- **No Unicode box-drawing:** swap `┌─┐│` for ASCII `+-|`. Alignment holds because every in-border glyph is width 1.
- **Alignment rule (so tables never break):** never place an emoji inside a bordered cell except in a dedicated single-emoji column padded for double width; everything else stays width-1 ASCII + accents.

Then the boot sequence continues (`core/boot.md`): detect HUB/APP → pull → JIT load.
