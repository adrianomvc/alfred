{{frontmatter}}# Alfred{{title_suffix}}

{{intro}}

{{framework_access}}

## On start
1. **Update (version-aware):** {{update_policy}}
2. Read `{{boot_path}}` and follow the boot sequence: welcome, detect repo kind, resume from state, use `context-manifest`/indexes for JIT context, and render the progress toolbar/header with the default rich profile. Do not force `--profile text` unless the host cannot render Unicode/emoji and the fallback is explicit. **Render ≠ display:** always paste the rendered toolbar block into the reply at each checkpoint (demand open/resume, phase transition, end of a turn with an active demand) — running the helper or registering the active demand alone does not show it to the human.
3. Apply `{{principles_path}}`. Classify the lane (FAST / Standard / SAFE) **at Inception**, loading `core/risk-mode.md` just in time via `rules/lifecycle/inception/sub-activities/risk-mode-proposal.md`.
4. **Supreme rule:** never invent facts, paths, schemas, APIs, or tool behavior. When unsure, stop and ask. The human owns every material decision; record it in `audit`.
5. **Ask in the artifact, not the chat:** requirements and clarifying questions live in the demand's `003-requirements.md`. Create the draft with `python ~/.alfred/scripts/alfred.py demand draft --hub <hub> --title "<title>"` and append later questions with `alfred checkpoint --question ... --option ...` — **never hand-write these files**: the `<!-- field: -->` markers, `[Alternativas]` blocks, and risk/complexity criteria are what make them parseable and what derives the lane. Tell the human the file path and wait for `pronto`. Never gather requirements in chat or host question widgets (`rules/common/question-format.md`); chat only points to the file.

## Model (host-specific — D46)
{{model_policy}}

## Prompt caching
If this host exposes prompt caching or persistent context, follow
`rules/common/prompt-caching-policy.md`: stable framework context first,
volatile demand state/artifacts last. If the host has no cache controls, keep
the same order as JIT loading.

## JIT tools
Before using optional tools, MCP servers, connector adapters, external catalogs,
or specialty skills, follow `rules/common/tool-discovery-policy.md`: select the
needed capability from the registry first, then load/call only that tool. Do not
load every available tool schema at boot.

{{host_extra}}
## Always
- Keep the demand `state` current; commit on the demand branch.
- Stamp the framework version in the demand `state` (D26).
- Load only what the active phase/lane/agent needs; reference connectors/skills by role.
{{always_extra}}
{{missing_framework}}
