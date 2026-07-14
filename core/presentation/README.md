# Presentation profiles

How Alfred renders the same content at different visual richness, without ever
splitting the source of truth or bloating the model's context.

## One source, many renderers
The source of truth is the **`state`** (and the welcome/knowledge content) — small
and text-first. A **renderer** turns it into output. There are never two parallel
versions to keep in sync (anti-redundancy); only one source and several renderers.

## Token economy (the rule that matters)
**The model never produces the rich visual — deterministic helpers do.** The model
reasons only over the compact `state` fields. A helper (script) transforms those
fields into the chosen profile. Rich output therefore costs ~zero model tokens and
never enters the context window. If no helper can run, the model first loads
`toolbar-quick.md` and emits the documented text floor from the same fields. Keep
every rendered view compact: the toolbar is one line in FAST, a small block
otherwise.

## Profiles (richest the host supports wins; always degrade to text)
| Profile | Host | Output |
|---|---|---|
| `text` (floor, always) | any terminal/host | plain ASCII/markdown — the spec |
| `rich` (preferred) | capable terminals/chat | Unicode box-drawing + compact icons, visually aligned with `welcome-screen.md` |
| `web` (optional) | graphical hosts | HTML card / SVG, rendered out-of-band by a helper |

## Selection
The Orchestrator picks the highest profile the host declares it can render and
**degrades to `text`** otherwise (Liskov: consumers ask for "the toolbar", not a
format). The host's capability is a hint recorded in `state`/host adapters, not a
hard dependency — nothing in the framework requires a non-text profile (D3).

## Files here (all JIT — load only when rendering that thing)
- `toolbar-quick.md` — the day-to-day cheat-sheet: exact toolbar shapes + markers.
- `toolbar.md` — full toolbar spec (layers, profiles, rules); for edge cases and renderer changes.
- `welcome-screen.md` — the rendered welcome block + degradation rules (persona stays in `core/welcome.md`).

## Markdown-safe rendering (fence rule — applies to every profile)
Most hosts today render Alfred's reply as **markdown** (Devin, web/chat UIs, IDE
panels), not as a raw terminal. Outside a fenced code block, markdown **collapses
repeated spaces** and **soft-wraps long lines**, so every bordered/aligned block
(welcome, toolbar) breaks. Therefore: emit any bordered or column-aligned block
**inside a fenced code block** (```). This is about the *transport* (markdown vs
raw terminal), not the character set — it is required for both `text` and `rich`,
and is orthogonal to the Unicode/emoji/color degradation. Only skip the fence on a
host proven to render the reply as raw monospace text.

## Rules
- `rich` is the preferred human-facing profile; `text` is the portable fallback.
- `text`, `rich`, and `web` must never
  become the source of truth.
- A renderer is pure: same `state` in → same output out; no hidden state.
- Keep views compact; richness is color/shape, not more words.
- Do not hand-draw rich toolbar blocks. Rich/profile output comes from the
  renderer; manual fallback is the documented `text` profile only.
