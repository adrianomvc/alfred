#!/usr/bin/env python3
"""Check that the toolbar renderer does not drift from saved fixtures."""

import argparse
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_text  # noqa: E402

CASES = [
    ("fast",
     "examples/toolbar-states/fast.md",
     "examples/toolbar-fixtures/fast.txt"),
    ("safe",
     "examples/toolbar-states/safe.md",
     "examples/toolbar-fixtures/safe.txt"),
    ("execution-first",
     "examples/toolbar-states/execution-first.md",
     "examples/toolbar-fixtures/execution-first.txt"),
    ("standard-parallel-units",
     "examples/toolbar-states/standard.md",
     "examples/toolbar-fixtures/standard-parallel-units.txt"),
]


def load_renderer():
    spec = importlib.util.spec_from_file_location(
        "render_toolbar", Path(__file__).resolve().parent.parent / "workflow" / "render-toolbar.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    render = load_renderer()

    for name, state_rel, expected_rel in CASES:
        state_path = root / state_rel
        expected_path = root / expected_rel
        if not state_path.exists():
            raise SystemExit(f"Missing toolbar fixture state for {name}: {state_path}")
        if not expected_path.exists():
            raise SystemExit(f"Missing toolbar fixture expected output for {name}: {expected_path}")

        actual = "\n".join(render(str(state_path), "GPT-5", "n/a", profile="text"))
        expected = read_text(expected_path)

        # Normalize line endings before comparing (fixtures use CRLF).
        if actual.replace("\r\n", "\n").rstrip() != expected.replace("\r\n", "\n").rstrip():
            raise SystemExit(
                f"Toolbar fixture drift: {name}. "
                "Regenerate or update expected output intentionally."
            )
        print(f"OK toolbar fixture {name}")

    print("Toolbar fixture validation completed.")


if __name__ == "__main__":
    main()
