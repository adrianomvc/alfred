#!/usr/bin/env python3
"""Validate the Alfred skills registry.

Python mirror of ``scripts/powershell/validate-skills-registry.ps1``.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_lines, read_text  # noqa: E402

REQUIRED_SECTIONS = [
    "name",
    "purpose",
    "trigger",
    "inputs",
    "expected output",
    "link",
    "sections to load",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    registry = root / "skills" / "skills.md"
    if not registry.exists():
        raise SystemExit(f"Missing skills registry: {registry}")

    skills = []
    row = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|")
    for line in read_lines(registry):
        match = row.match(line)
        if match:
            skills.append((match.group(1), match.group(2)))

    if not skills:
        raise SystemExit("No skills found in registry table.")

    for name, link in skills:
        skill_path = root / link
        if not skill_path.exists():
            raise SystemExit(f"Missing registered skill {name}: {link}")
        content = read_text(skill_path)
        for section in REQUIRED_SECTIONS:
            pattern = r"(?im)^##\s+" + re.escape(section) + r"\s*$"
            if not re.search(pattern, content):
                raise SystemExit(f"Skill {name} is missing required section: {section}")
        print(f"OK skill {name}")

    print("Skills registry validation completed.")


if __name__ == "__main__":
    main()
