# Question format — operational prompt (D18)

Clarifying questions go IN A FILE (`requirements.md` for Inception, or the relevant artifact), not only in chat. Questions in pt-BR (D47).

## Format
```
## Q1 <pergunta clara>
A) <opção>
B) <opção>
C) <opção>
X) Outro (descreva após [Answer]:)

[Answer]:
```
Rules: 2+ meaningful options + "Outro" as the LAST; options mutually exclusive; one topic per question.

## Gate behavior
- After writing questions, STOP. Tell the person: "Registrei N perguntas em <arquivo>. Pode responder nos [Answer]: e me avisar?".
- Do NOT advance until all `[Answer]:` are filled and validated.
- Read answers; if empty/invalid → ask again for those.

## Contradiction/ambiguity detection
After answers, scan for inconsistencies (e.g., "bug" + "afeta todo o sistema"; "baixo risco" + "breaking change"). If found, create follow-up questions referencing the conflicting answers; resolve before proceeding.

## Depth by lane
FAST: few/none (inline). Standard: a focused set. SAFE: comprehensive, multiple rounds if needed.
