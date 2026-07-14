#!/usr/bin/env python3
"""Version-aware framework update check with a TTL.

Boot should not hit the network every session. Within the TTL window this reports
the cached commit and does nothing; past it (or with -Force) it runs a
fast-forward pull and stamps the check time in ``~/.alfred/runtime``. Never
blocks: any git/network failure degrades to "not verified" and boot continues.
Version freezing for an active demand is handled by the boot sequence, not here.
"""

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_TTL_HOURS = 6.0


def default_stamp_path():
    return Path.home() / ".alfred" / "runtime" / "last-update-check.json"


def load_stamp(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def git(args, cwd):
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True, text=True, timeout=15, check=False,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except (OSError, subprocess.SubprocessError) as error:
        return 1, "", str(error)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alfred-home", "-AlfredHome", dest="alfred_home", default="")
    parser.add_argument("--ttl-hours", "-TtlHours", dest="ttl_hours", type=float, default=DEFAULT_TTL_HOURS)
    parser.add_argument("--force", "-Force", dest="force", action="store_true")
    parser.add_argument("--stamp-path", "-StampPath", dest="stamp_path", default="")
    args = parser.parse_args()

    home = Path(args.alfred_home).expanduser() if args.alfred_home else Path.home() / ".alfred"
    stamp = Path(args.stamp_path).expanduser() if args.stamp_path else default_stamp_path()
    data = load_stamp(stamp)
    now = time.time()
    last = float(data.get("checked_at_epoch", 0) or 0)

    if not args.force and (now - last) < args.ttl_hours * 3600:
        age_min = int((now - last) / 60)
        print(f"update-check: skipped (checked {age_min} min ago, TTL {args.ttl_hours:g}h); "
              f"current {data.get('commit', 'unknown')}")
        return

    code, out, err = git(["pull", "--ff-only"], home)
    _rc, commit, _ = git(["rev-parse", "--short", "HEAD"], home)
    if code == 0:
        changed = bool(out) and "up to date" not in out.lower() and "up-to-date" not in out.lower()
        print(f"update-check: {'updated' if changed else 'already current'} at {commit or 'unknown'}")
    else:
        print(f"update-check: not verified ({err or 'git unavailable'}); staying on {commit or 'unknown'}")

    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(json.dumps({
        "checked_at_epoch": now,
        "checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "commit": commit,
    }), encoding="utf-8")


if __name__ == "__main__":
    main()
