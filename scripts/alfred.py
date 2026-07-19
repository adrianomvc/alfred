#!/usr/bin/env python3
"""Canonical Alfred CLI entrypoint."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared.cli import run  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run())
