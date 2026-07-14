#!/usr/bin/env python3
"""Validate the minimum SDD clarity gate before Execution."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.sdd_gate import run  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hub-demand-path", "-HubDemandPath", dest="hub_demand_path", required=True)
    parser.add_argument("--app-demand-path", "-AppDemandPath", dest="app_demand_path", default="")
    parser.add_argument("--strict", "-Strict", dest="strict", action="store_true")
    args = parser.parse_args()

    output, errors, warnings, failed = run(
        args.hub_demand_path, args.app_demand_path, args.strict
    )
    for line in output:
        print(line)
    if failed:
        sys.exit(
            f"SDD gate failed. errors={len(errors)}, warnings={len(warnings)}, strict={args.strict}"
        )


if __name__ == "__main__":
    main()
