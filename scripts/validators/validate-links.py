#!/usr/bin/env python3
"""Validate internal Markdown references in the Alfred framework.

Optional helper (D3): Alfred still works manually through Markdown if it cannot run. It catches
broken cross-references after files are moved or renamed.

It checks two reference styles used across the framework:
- Markdown links ``[text](target)`` — resolved relative to the file, then root.
- Inline code paths ``` `top-dir/...` ``` (start with a framework top folder) —
  resolved relative to root, then the file.

URLs, ``mailto:``, pure ``#anchor`` links, and glob patterns (``*``) are skipped.
"""

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _common import read_text  # noqa: E402

# Folders whose Markdown is part of the framework source (not generated artifacts).
SCAN_DIRS = [
    "core", "rules", "skills", "connectors", "metrics",
    "knowledge", "templates", "docs", "install", "hosts",
    "scripts", "examples",
]
# CHANGELOG.md is intentionally excluded: it is a historical ledger where path
# references are point-in-time (a past entry may name a file that has since
# moved), so it must not be "corrected" to match the current tree.
# docs/plan/alfred-conceptual-plan.md is excluded for the same reason: it is the
# versioned original design document (D1-D47) whose paths reflect the plan as
# written, not the as-built tree.
# docs/plan/context-optimization-progress.md is excluded likewise: its approved
# plan names phase deliverables that only exist once their phase lands.
ROOT_FILES = ["README.md", "AGENTS.md"]
EXCLUDE_FILES = {
    "docs/plan/alfred-conceptual-plan.md",
    "docs/plan/context-optimization-progress.md",
}

TOP_DIRS = (
    "core", "rules", "skills", "connectors", "metrics", "knowledge",
    "templates", "docs", "scripts", "examples", "install",
)

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
INLINE = re.compile(r"`([^`]+)`")
INLINE_PATH = re.compile(r"^(?:" + "|".join(TOP_DIRS) + r")/[\w./-]+$")


def strip_anchor(target):
    return target.split("#", 1)[0].strip()


def heading_anchors(text):
    """GitHub-style anchor slugs for every heading in a Markdown text."""
    anchors = set()
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.*)$", line)
        if match:
            slug = match.group(1).strip().lower()
            slug = re.sub(r"[`*_\[\]():.,!?/·]", "", slug)
            slug = re.sub(r"\s+", "-", slug.strip())
            anchors.add(slug)
    return anchors


def is_external(target):
    return "://" in target or target.startswith("mailto:")


def resolves(candidates):
    for cand in candidates:
        try:
            if cand.exists():
                return True
        except OSError:
            continue
    return False


def collect_refs(text):
    """Return a list of (kind, target) references worth checking."""
    refs = []
    for match in MD_LINK.finditer(text):
        target = match.group(1).split()[0] if match.group(1).split() else ""
        target = strip_anchor(target)
        if not target or is_external(target) or "*" in target:
            continue
        refs.append(("link", target))
    for match in INLINE.finditer(text):
        token = match.group(1).strip()
        if "*" in token or " " in token or not INLINE_PATH.match(token):
            continue
        refs.append(("inline", token))
    return refs


def iter_markdown(root):
    for rel in ROOT_FILES:
        path = root / rel
        if path.exists():
            yield path
    for folder in SCAN_DIRS:
        base = root / folder
        if base.exists():
            for path in sorted(base.rglob("*.md")):
                rel = path.relative_to(root).as_posix()
                if rel in EXCLUDE_FILES:
                    continue
                yield path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    files = 0
    checked = 0
    broken = 0
    anchor_warnings = 0
    for md in iter_markdown(root):
        files += 1
        text = read_text(md)
        for kind, target in collect_refs(text):
            checked += 1
            if kind == "link":
                candidates = [md.parent / target, root / target]
            else:
                candidates = [root / target, md.parent / target]
            if not resolves(candidates):
                broken += 1
                rel = md.relative_to(root)
                print(f"BROKEN {rel} -> {target} ({kind})")
        # Anchor targets are advisory (warning only): a wrong `#section` link
        # misleads readers but does not break file resolution.
        for match in MD_LINK.finditer(text):
            raw = match.group(1).split()[0] if match.group(1).split() else ""
            if not raw or is_external(raw) or "#" not in raw or "*" in raw:
                continue
            path_part, anchor = raw.split("#", 1)
            anchor = anchor.strip().lower()
            if not anchor:
                continue
            target_file = md if not path_part else next(
                (cand for cand in (md.parent / path_part, root / path_part) if cand.is_file()), None)
            if target_file is None:
                continue  # file breakage already reported above
            if anchor not in heading_anchors(read_text(target_file)):
                anchor_warnings += 1
                rel = md.relative_to(root)
                print(f"WARN {rel} -> #{anchor} not found in {path_part or 'same file'} (anchor)")

    print(f"Link validation completed. files={files} refs={checked} broken={broken} anchor_warnings={anchor_warnings}")
    if broken:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
