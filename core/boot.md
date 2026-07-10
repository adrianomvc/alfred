# Boot — session start

Every session begins with a fixed sequence before any work. The host runs it once per session. Inherits the spirit of `workspace-detection` + `session-continuity` from AI-DLC. The boot **never loads everything** — only index + state + what is needed; the rest is on demand.

## Sequence
1. **Welcome** — short opening message in the butler's voice (`welcome.md` = persona/tone), shown once per session. To render the visual welcome block, load `presentation/welcome-screen.md` **only at that moment** (JIT; the persona file alone is enough for the rest of the session).
2. **Detect repo** — identify which repo we are in, to know which artifacts to read and how:
   - **HUB** if it finds `alfred-docs-hub/` + `<iniciativa-id>/<demanda-id>/` (initiative artifacts). The HUB is the sigla workspace: it holds the demand truth (`state`), problem/scope, decisions, audit, metrics, summary, knowledge, and links to the apps touched.
   - **APP** if it finds `.alfred-docs-app/` + application code (technical artifacts). The APP is a product/application repository: it holds the source code plus app-local Alfred artifacts such as reverse engineering, technical spec, evidence, local audit/metrics, and HUB sync notes.
   - **APP-only** if it finds `.alfred-docs-app/` but no writable HUB path. In this mode, write only app-local artifacts and create/update `05-operation/009-hub-sync.md` for later HUB import.
   - **Framework** if it finds `core/principles.md` / `rules/agents/` (editing Alfred itself).
   - Not identified → ask the human before writing anything. Repository names
     such as `*-hub` are only hints; they do not prove the repo is a HUB.
     Before asking, explain the difference in the human interaction language
     (pt-BR by default for squads): **HUB = governance/source of truth for a
     sigla and demand; APP = code repo with technical evidence for one
     application**. Then ask whether the current workspace should be treated as
     HUB, APP, both, or neither, and whether a missing path should be
     mounted/provided.
   - **Sigla (auto-label):** derive the sigla from the repo name — pattern `itau-<sigla>-<...>` → the segment right after `itau-` (from the app repo a demand targets, or the current repo). Fallback: the repo/folder name; else `unknown`. It is a **display label only** — no logic depends on it, so **never ask the human** for it. The pattern is configurable per org.
   - **Confirmed empty/new HUB → provision, don't interrogate:** after the repo
     is already identified as a HUB (by existing marker or explicit human
     confirmation), create the `alfred-docs-hub/` skeleton with defaults per
     `docs/onboarding-sigla.md`; write owner/apps/tracker as `pending`, read
     notification from `knowledge/notification.md`, and **never present a scope
     menu** — then offer one next step in a line.
3. **Update local framework (if CLI)** — pull the framework repo to ensure the latest version; if it changed, announce in one line what changed. No CLI/access → record "not verified."
   - **Safeguard (active demand):** if there is an update **and** an active demand, Alfred **warns and asks** — apply now or only on the next demand. The demand records the framework version used and keeps it frozen until it closes, unless a human decides otherwise.
4. **JIT context load (anti-hypercontext):**
   - read the `index` of the detected repo;
   - **list the sigla's open demands** (in progress / on hold / blocked) with last activity, and ask which to resume; otherwise treat as a **new demand**;
   - on resume → **rebuild from the `state`** (show the toolbar — formats in `presentation/toolbar-quick.md` — + "what's left");
   - optionally run `scripts/*/workflow/context-manifest` with the active phase/lane/demand type/agent to list the minimal rule files; no helper → follow `rules/README.md` + `rules/rules-index.md` manually;
   - open only the current theme's links + active skills.
   - if using RAG, compressed summaries, or codebase-memory output to select
     context, load `rules/common/context-compression-policy.md` first.
   - before opening large multi-file context, load
     `rules/common/token-budget-policy.md` and write a short context budget.
5. **Confirm with the human** the starting point (continue / new / review) before acting.

## Opening framing checkpoint
For a **new demand**, Alfred must stop before any mutating action and present one
concise framing proposal for explicit human confirmation. This checkpoint comes
before cloning/fetching an app repo, choosing or stamping initiative/demand ids,
creating HUB/App demand artifacts, writing `state`, or classifying a lane as
accepted.

The proposal includes: target app source/path, workspace placement, initiative
id, demand id, initial scope, proposed lane, and which artifacts will be created.
Only deterministic labels may be inferred without asking (for example the sigla
auto-label from the repo name). Material decisions are never implied by "start a
demand" or by "act first, ask later".

## App-only resume
When running inside an app repo without HUB access, Alfred resumes from `.alfred-docs-app/<id-iniciativa>/<id-demanda>/001-index.md` plus the app-local artifacts. If the HUB `001-state.md` cannot be read, Alfred treats the demand state as **local pending sync**, records that limitation in `05-operation/009-hub-sync.md`, and asks the human for the missing demand/initiative identifiers only if they cannot be inferred from the path or branch.

## Stamp the framework version
On boot, stamp the framework version/commit into the demand `state` (frozen until the demand closes — traceability). Three coherent stamps exist: **framework** (in `state`), **app** (commit in `reverse-eng`/PR), **demand** (`id` + branch). Result: you can reconstruct "this demand ran with Alfred vX, over the app at commit Y."

## Version adoption
Follow `docs/version-adoption.md` when the local framework differs from the version stamped in an active demand.

Active demands keep their stamped framework version frozen. If a newer framework is available, Alfred warns the human and records the choice: keep the frozen version or upgrade in-flight. An in-flight upgrade requires an audit event, a JSONL event, and updated state/metrics version fields.

## Resume from state (resilience)
The `state` always carries phase, mode, progress, next step, and links — enough for boot to reconstruct context without re-reading everything. If a session drops, resume from the last saved `state`: at most the in-flight step is lost, never the demand. Acceptance criterion: *resume after losing context by reading only the `state`.*

## Cache-friendly order
When the host preserves prompt/cache segments, load the most stable framework
context first and the volatile demand context last: kernel (`core/principles.md`,
`core/boot.md`, indexes) → generated registries/manifests → phase/lane/type
rules → active skills → demand `state` and current artifacts. This is advisory:
if the host has no cache controls, the same order still keeps the JIT path clear.
Load `rules/common/prompt-caching-policy.md` when assembling multi-file context
or when a host exposes prompt caching/persistent context.

## Token budget preflight
Before loading large source sets, logs, diffs, external catalogs, or multi-repo
context, Alfred loads `rules/common/token-budget-policy.md`, records the purpose
and scope, then uses indexes/search/compression to choose which original sources
to open. This reduces token spend without dropping acceptance criteria or lane
guardrails.

## Welcome back (open demands)
Alfred never declares abandonment by inactivity. On boot it **lists the open demands** of the sigla with their last activity — the butler's welcome-back: *"There are 2 demands on hold: #142 (Design) and #097 (Execution). Resume one?"*. Who decides to cancel/resume is the human.
