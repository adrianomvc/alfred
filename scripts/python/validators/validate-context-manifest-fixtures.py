#!/usr/bin/env python3
"""Check context-manifest output against saved fixtures."""

import argparse
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_text  # noqa: E402

CASES = [
    (
        "standard-product-design",
        {
            "phase": "Design",
            "lane": "Standard",
            "demand_type": "product",
            "agent": "spec-design",
            "sub_activity": "functional-design",
        },
        "examples/context-manifest-fixtures/standard-product-design.txt",
    ),
    (
        "fast-operational-execution",
        {
            "phase": "Execution",
            "lane": "FAST",
            "demand_type": "operational",
            "agent": "orchestrator",
            "sub_activity": "workflow-planning",
        },
        "examples/context-manifest-fixtures/fast-operational-execution.txt",
    ),
    (
        "safe-engineering-inception",
        {
            "phase": "Inception",
            "lane": "SAFE",
            "demand_type": "engineering",
            "agent": "discovery",
            "sub_activity": "risk-mode-proposal",
        },
        "examples/context-manifest-fixtures/safe-engineering-inception.txt",
    ),
]


def load_manifest():
    script = Path(__file__).resolve().parent.parent / "workflow" / "context-manifest.py"
    spec = importlib.util.spec_from_file_location("context_manifest", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    build_manifest = load_manifest()

    for name, params, fixture_rel in CASES:
        fixture_path = root / fixture_rel
        if not fixture_path.exists():
            raise SystemExit(f"Missing context-manifest fixture for {name}: {fixture_path}")

        actual = "\n".join(build_manifest(root, **params))
        expected = read_text(fixture_path)
        if actual.replace("\r\n", "\n").rstrip() != expected.replace("\r\n", "\n").rstrip():
            raise SystemExit(
                f"Context manifest fixture drift: {name}. "
                "Regenerate or update expected output intentionally."
            )
        print(f"OK context manifest fixture {name}")

    print("Context manifest fixture validation completed.")


if __name__ == "__main__":
    main()
