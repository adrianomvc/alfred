# Knowledge Policy Template

Mold for an always-on guardrail policy. Copy a block into the org `knowledge/`
or the sigla/squad HUB `knowledge/`. Keep framework labels in English; write the
policy content in pt-BR (HUB artifacts are pt-BR). One policy per block; keep
each block short and reference it from the index (split when it grows).

A policy is a **hard constraint that is always in force** in its scope. It is
not a skill (an opt-in capability) — it is a rule the agents must respect. The
agent never bypasses a policy: it follows it, or it stops and asks (anti-overconfidence).

## Policy: <short title>
- **scope:** `org` | `sigla` | `squad`
- **rule:** <the constraint, in pt-BR — e.g. "criar repositório apenas via ISSUE no tracker">
- **applies to:** <demand types / lanes / phases / repos where it bites, or "todos">
- **rationale:** <why it exists, in pt-BR>
- **precedence:** org sets the floor; sigla/squad may be **stricter, never weaker**. A conflict goes to a human (governance).
- **enforcement:** what the agent does to comply — e.g. "abrir ISSUE via connector `tracker` em vez de criar o repo direto"; if it cannot comply, **stop and ask** — never invent a path around it.
- **exception:** only a human may record an explicit exception, in `decisions`/`audit`, with who approved and why. No silent relaxation.

## Notes
- Precedence is the same as the guardrail rule: org is mandatory; sigla/squad add or harden, never relax.
- Policies are loaded by theme when relevant (JIT through the index), but the scope's policies are **always in force** — they are not opt-in.
- If a policy needs an external system (tracker, VCS, access request), reference the connector by **role**, not by a concrete tool name.
