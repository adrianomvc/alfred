#!/usr/bin/env python3
"""Generate host shim files from the shared host template."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import read_text  # noqa: E402


def render(template, host):
    content = template
    for key, value in host.items():
        content = content.replace("{{" + key + "}}", str(value))
    if "{{" in content or "}}" in content:
        raise SystemExit(f"Unresolved template marker in host {host.get('id', 'unknown')}")
    while "\n\n\n" in content:
        content = content.replace("\n\n\n", "\n\n")
    return content.rstrip() + "\n"


def check_or_write(path, content, check):
    current = read_text(path) if path.exists() else ""
    if check:
        if current != content:
            raise SystemExit(f"Host shim drift: regenerate {path.as_posix()}")
        print(f"OK host shim {path.as_posix()}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {path.as_posix()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    parser.add_argument("--check", "-Check", action="store_true", dest="check")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    template = read_text(root / "hosts" / "_template" / "shim.md")
    config = json.loads(read_text(root / "hosts" / "_template" / "hosts.json"))

    for host in config["hosts"]:
        output = root / host["output"]
        check_or_write(output, render(template, host), args.check)

    print("Host shim generation completed.")


if __name__ == "__main__":
    main()
