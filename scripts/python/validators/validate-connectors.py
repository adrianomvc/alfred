#!/usr/bin/env python3
"""Validate Alfred connector contracts and adapter-shaped examples.

Python mirror of ``scripts/powershell/validators/validate-connectors.ps1``.
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_text  # noqa: E402

CONNECTOR_SECTIONS = ["type", "activation", "operations", "degradation", "audit fields"]
ADAPTER_SECTIONS = [
    "identity",
    "activation",
    "operations",
    "inputs",
    "outputs",
    "audit fields",
    "observability event",
    "degradation",
    "safety checks",
    "fixture",
]


def assert_section(content, section, label):
    pattern = r"(?im)^##\s+" + re.escape(section) + r"\s*$"
    if not re.search(pattern, content):
        raise SystemExit(f"{label} is missing required section: {section}")


def test_connector_contract(path):
    content = read_text(path)
    for section in CONNECTOR_SECTIONS:
        assert_section(content, section, path.name)
    print(f"OK connector {path.name}")


def test_adapter_shape(path, require_concrete_status=False):
    content = read_text(path)
    for section in ADAPTER_SECTIONS:
        assert_section(content, section, path.name)
    if require_concrete_status and not re.search(
        r"(?im)^\s*-\s+status:\s*(contract|handoff|dry-run|active|disabled)\s*$",
        content,
    ):
        raise SystemExit(f"{path.name} must declare a valid adapter status")
    print(f"OK adapter {path.name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    connectors_path = root / "connectors"
    examples_path = root / "examples" / "connectors"

    if not connectors_path.exists():
        raise SystemExit(f"Missing connectors directory: {connectors_path}")

    contract_files = [
        f
        for f in sorted(connectors_path.glob("*.md"))
        if f.name not in ("connectors.md", "adapter-template.md")
    ]
    if not contract_files:
        raise SystemExit("No connector contract files found.")

    for file in contract_files:
        test_connector_contract(file)

    test_adapter_shape(connectors_path / "adapter-template.md")

    if examples_path.exists():
        for file in sorted(examples_path.glob("*adapter*.md")):
            test_adapter_shape(file, require_concrete_status=True)

    print("Connector validation completed.")


if __name__ == "__main__":
    main()
