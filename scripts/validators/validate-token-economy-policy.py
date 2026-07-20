#!/usr/bin/env python3
"""Validate token-budget and deferred-work policy wiring."""

import argparse
from pathlib import Path


def require_text(path, needle):
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        raise SystemExit(f"Missing text in {path}: {needle}")
    print(f"OK text {path} / {needle}")


def forbid_text(path, needle):
    """Anti-regression: a retired false claim must not reappear."""
    text = path.read_text(encoding="utf-8")
    if needle in text:
        raise SystemExit(f"Forbidden text present in {path}: {needle}")
    print(f"OK absent {path} / {needle}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    require_text(root / "rules/common/token-budget-policy.md", "Plan the token spend before loading context")
    require_text(root / "rules/common/token-budget-policy.md", "Do not reduce context by dropping acceptance criteria")
    require_text(root / "rules/common/token-budget-policy.md", "If the host has token counting")
    require_text(root / "rules/common/deferred-work-policy.md", "not on the human's critical path")
    require_text(root / "rules/common/deferred-work-policy.md", "Deferred outputs are drafts or inputs")
    require_text(root / "rules/common/deferred-work-policy.md", "batch, flex, background")

    require_text(root / "rules/common/context-compaction-policy.md", "Compaction safety = state")
    require_text(root / "rules/common/context-compaction-policy.md", "Forbidden points")
    require_text(root / "core/boot.md", "context-compaction-policy.md")
    require_text(root / "rules/common/session-continuity.md", "context-compaction-policy.md")

    require_text(root / "core/boot.md", "token-budget-policy.md")
    require_text(root / "core/model-policy.md", "Deferred work")
    require_text(root / "rules/README.md", "token-budget-policy")
    require_text(root / "rules/README.md", "deferred-work-policy")
    require_text(root / "rules/lifecycle/execution/execution.md", "token-budget-policy.md")
    require_text(root / "rules/lifecycle/execution/sub-activities/workflow-planning.md", "context budget per unit")
    require_text(root / "rules/lifecycle/operations/operations.md", "deferred-work-policy.md")
    require_text(root / "rules/lifecycle/operations/sub-activities/metrics-collection.md", "deferred-work-policy.md")
    require_text(root / "docs/framework-validation.md", "validate-token-economy-policy")

    # Host capability matrix (single source of deterministic host claims).
    require_text(root / "hosts/capabilities.md", "Host capability matrix")
    require_text(root / "hosts/capabilities.md", "preset targets `Bash`")

    # Anti-regression: the DEVIN CLI *does* have a PreToolUse hook and imports
    # `.claude/`; RTK's stock preset just matches `Bash` not `exec`. Keep the
    # retired false claim from creeping back into source or generated shims.
    for rel in ("hosts/_template/hosts.json", "hosts/devin-cli/SKILL.md", "core/hooks/rtk.md"):
        forbid_text(root / rel, "does not run Claude Code's auto-rewrite")
        forbid_text(root / rel, "do not assume Devin executes that hook")
    require_text(root / "core/hooks/rtk.md", "loads yet never fires")
    require_text(root / "install/install.sh", "if command -v claude >/dev/null 2>&1; then")
    require_text(root / "install/install.sh", "RTK global initialization skipped: Claude Code CLI not found")

    print("Token economy policy validation completed.")


if __name__ == "__main__":
    main()
