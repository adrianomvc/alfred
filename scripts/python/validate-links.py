#!/usr/bin/env python3
"""Validate internal Markdown references in the Alfred framework.

Python mirror of ``scripts/powershell/validate-links.ps1``. Optional helper
(D3): Alfred still works manually through Markdown if it cannot run. It catches
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
sys.path.insert(0, str(HERE))
from _common import read_text  # noqa: E402

# Folders whose Markdown is part of the framework source (not generated artifacts).
SCAN_DIRS = [
    "core", "rules", "skills", "connectors", "metrics",
    "knowledge", "templates", "docs", "install", "hosts",
]
# CHANGELOG.md is intentionally excluded: it is a historical ledger where path
# references are point-in-time (a past entry may name a file that has since
# moved), so it must not be "corrected" to match the current tree.
ROOT_FILES = ["README.md"]

TOP_DIRS = (
    "core", "rules", "skills", "connectors", "metrics", "knowledge",
    "templates", "docs", "scripts", "examples", "install",
)

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
INLINE = re.compile(r"`([^`]+)`")
INLINE_PATH = re.compile(r"^(?:" + "|".join(TOP_DIRS) + r")/[\w./-]+$")


def strip_anchor(target):
    return target.split("#", 1)[0].strip()


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
            yield from sorted(base.rglob("*.md"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    files = 0
    checked = 0
    broken = 0
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

    print(f"Link validation completed. files={files} refs={checked} broken={broken}")
    if broken:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
