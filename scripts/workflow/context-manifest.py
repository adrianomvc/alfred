#!/usr/bin/env python3
"""Print minimal Alfred context in stable-to-volatile order."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.context_manifest import ContextManifestError, build_manifest  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    parser.add_argument("--phase", "-Phase", required=True)
    parser.add_argument("--lane", "-Lane", required=True)
    parser.add_argument("--demand-type", "-DemandType", dest="demand_type", required=True)
    parser.add_argument("--agent", "-Agent", required=True)
    parser.add_argument("--sub-activity", "-SubActivity", dest="sub_activity", default="")
    parser.add_argument("--playbook", "-Playbook", dest="playbook", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    try:
        for path in build_manifest(
            root, args.phase, args.lane, args.demand_type, args.agent,
            args.sub_activity, args.playbook
        ):
            print(path)
    except ContextManifestError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
