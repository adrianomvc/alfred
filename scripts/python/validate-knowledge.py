#!/usr/bin/env python3
"""Validate Alfred knowledge files, the policy template, and example policies.

Python mirror of ``scripts/powershell/validate-knowledge.ps1``.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_text  # noqa: E402

POLICY_SECTIONS = [
    "identity",
    "applies to",
    "rule",
    "rationale",
    "enforcement",
    "exceptions",
    "audit evidence",
    "related artifacts",
]


def assert_path(path, label):
    if not path.exists():
        raise SystemExit(f"Missing knowledge path: {label}")
    print(f"OK path {label}")


def assert_section(content, section, label):
    if not re.search(r"(?im)^##\s+" + re.escape(section) + r"\s*$", content):
        raise SystemExit(f"{label} is missing required section: {section}")
    print(f"OK section {label} / {section}")


def validate_policy(path, root, require_concrete_status=False):
    content = read_text(path)
    label = str(path.relative_to(root))
    for section in POLICY_SECTIONS:
        assert_section(content, section, label)
    if require_concrete_status and not re.search(
        r"(?im)^\s*-\s+status:\s*(draft|active|deprecated)\s*$", content
    ):
        raise SystemExit(f"{label} must define a concrete policy status")
    print(f"OK policy {label}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    for label in (
        "knowledge/README.md",
        "knowledge/notification.md",
        "knowledge/policy-template.md",
        "docs/knowledge-governance.md",
    ):
        assert_path(root / label, label)

    readme = read_text(root / "knowledge/README.md")
    assert_section(readme, "Scopes", "knowledge/README.md")
    assert_section(readme, "Rule", "knowledge/README.md")

    notification = read_text(root / "knowledge/notification.md")
    assert_section(notification, "destination", "knowledge/notification.md")
    assert_section(notification, "default triggers", "knowledge/notification.md")
    assert_section(notification, "guardrails", "knowledge/notification.md")

    template_path = root / "knowledge/policy-template.md"
    template = read_text(template_path)
    validate_policy(template_path, root)
    if not re.search(r"(?im)status:\s*.*draft.*active.*deprecated", template):
        raise SystemExit("knowledge/policy-template.md must define policy status values")

    examples_root = root / "examples"
    if examples_root.exists():
        for path in sorted(examples_root.rglob("*.md")):
            if "knowledge" in path.parts and path.name != "README.md":
                validate_policy(path, root, require_concrete_status=True)

    print("Knowledge validation completed.")


if __name__ == "__main__":
    main()
