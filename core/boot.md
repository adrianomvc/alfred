# Boot sequence (D16)

Run once at session start, before any work. Never load everything — index + state + what's needed (D11).

1. **Welcome** — show `welcome.md` (butler voice, pt-BR), once per session.
2. **Detect repo:**
   - HUB → has `context.md` + `<iniciativa>/`.
   - App → has `.alfred/` + application code.
   - Framework → has `core/`/`rules/` (Alfred self-edit mode).
   - None → ask the human.
3. **Update framework (if CLI):** pull the framework repo; if changed, announce in 1 line what changed (D15).
   - Safeguard: if a demand is in progress, ask whether to apply now or on next demand; the demand records the framework version used (D26).
4. **JIT load:**
   - read the `index`;
   - **list open demands** of the sigla (in-progress / on-hold / blocked) with last activity (D28) and ask which to resume; otherwise treat as a **new demand**;
   - on resume → load `state`, render the toolbar per `core/toolbar.md` (mode·model·cost·progress·what's left);
   - open only the current theme's links + active skills.
5. **Confirm start point** with the human (continue / new / review) before acting.

Language: interactions in pt-BR (D47).
