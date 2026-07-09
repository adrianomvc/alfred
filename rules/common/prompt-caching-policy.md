---
name: common-prompt-caching-policy
description: Common rule - prompt caching and stable context order
load: event
triggers:
  phase: all
  lane: all
  demand-type: all
  agent: all
---

# Common rule - Prompt Caching Policy

## Trigger
Load this rule when a host exposes prompt caching or persistent context, or when
Alfred assembles a multi-file context bundle.

## Rule
Keep the most stable context first and the most volatile context last.

Recommended order:
1. framework kernel: `core/principles.md`, `core/boot.md`, folder indexes;
2. generated registries/manifests: `rules/rules-index.md`, `skills/skills.md`;
3. active phase/lane/type/agent rules;
4. active skills and relevant knowledge policies;
5. current demand `state`;
6. current working artifacts, terminal output, diffs, logs, and the human's
   latest request.

## Guardrails
- Do not require host-specific cache controls. This rule is advisory and
  degrades to plain JIT loading when the host has no cache feature.
- Do not duplicate stable framework text into HUB/App artifacts. Reference the
  framework source instead.
- Do not place volatile data before the stable framework prefix unless a host
  explicitly requires another order.
- Keep large logs, diffs, and command output bounded by
  `rules/common/terminal-token-policy.md` before they enter model context.

## Audit
When a host exposes cache controls and Alfred intentionally changes the loading
order, record the order or cache policy used in `audit` or the observability
event metadata.
