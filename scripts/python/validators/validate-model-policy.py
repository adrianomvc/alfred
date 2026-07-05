#!/usr/bin/env python3
"""Validate the Alfred model policy.

Python mirror of ``scripts/powershell/validators/validate-model-policy.ps1``.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_text  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    policy_path = root / "core" / "model-policy.md"
    if not policy_path.exists():
        raise SystemExit(f"Missing model policy: {policy_path}")

    content = read_text(policy_path)

    def assert_heading(text):
        pattern = r"(?im)^##\s+.*" + re.escape(text) + r".*$"
        if not re.search(pattern, content):
            raise SystemExit(
                f"Model policy is missing required heading containing: {text}"
            )
        print(f"OK heading {text}")

    def assert_pattern(pattern, label):
        if not re.search(pattern, content):
            raise SystemExit(f"Model policy is missing or changed: {label}")
        print(f"OK policy {label}")

    assert_heading("Selection rule")
    assert_heading("Floor per lane")
    assert_heading("Adjustment per step")
    assert_heading("Tier")
    assert_heading("real model")
    assert_heading("Mechanism")
    assert_heading("User override")
    assert_heading("In the toolbar")

    required_floors = {"FAST": "cheap", "Standard": "medium", "SAFE": "strong"}
    for lane, tier in required_floors.items():
        assert_pattern(
            r"(?im)^\|\s*" + lane + r"\s*\|\s*" + tier + r"\s*\|",
            f"{lane} floor = {tier}",
        )

    for tier in ("cheap", "medium", "strong"):
        assert_pattern(r"(?im)^\|\s*" + tier + r"\s*\|", f"tier map includes {tier}")

    assert_pattern(r"(?im)Design.*spec-design.*\+1 tier", "Design/spec-design can rise above floor")
    assert_pattern(r"(?im)Execution.*boilerplate.*keep floor", "Execution boilerplate keeps floor")
    assert_pattern(r"(?im)Validate.*reviewer.*keep / \+1 if risk", "Validate reviewer adjustment is explicit")
    assert_pattern(r"(?im)Decisions / architecture \(SAFE\).*\|\s*strongest\s*\|", "SAFE architecture decisions use strongest")
    assert_pattern(r"(?im)below the risk floor.*warns? the trade-off", "override below floor warns human")
    assert_pattern(r"(?im)record[s]? it in `state`/`audit`", "override is recorded")
    assert_pattern(r"(?im)toolbar shows the \*\*current model\*\*", "toolbar declares current model")

    print("Model policy validation completed.")


if __name__ == "__main__":
    main()
