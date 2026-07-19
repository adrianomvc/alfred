#!/usr/bin/env python3
"""Compatibility driver for the canonical always-main updater."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.cli.git_service import update  # noqa: E402
from shared.cli.result import render  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alfred-home", "-AlfredHome", dest="alfred_home", default="")
    parser.add_argument("--state-path", "-StatePath", dest="state_path", default="")
    parser.add_argument("--force", "-Force", dest="force", action="store_true")
    parser.add_argument("--ttl-hours", "-TtlHours", dest="ttl_hours", type=float, default=0.0,
                        help="deprecated; checked at every safe boundary")
    parser.add_argument("--stamp-path", "-StampPath", dest="stamp_path", default="",
                        help="deprecated compatibility option")
    parser.add_argument("--dry-run", "-DryRun", dest="dry_run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    home = Path(args.alfred_home).expanduser() if args.alfred_home else Path.home() / ".alfred"
    result = update(home, state_path=args.state_path, dry_run=args.dry_run)
    print(render(result, args.as_json))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
