#!/usr/bin/env python3
"""Sync generated Alfred host entry files into native host locations."""

import argparse
import json
import os
import shutil
from pathlib import Path


HOST_SOURCES = {
    "claude-code": "hosts/claude-code/SKILL.md",
    "devin-cli": "hosts/devin-cli/SKILL.md",
    "codex": "hosts/codex/AGENTS.md",
    "github-copilot": "hosts/github-copilot/copilot-instructions.md",
}


def default_targets(host):
    home = Path.home()
    targets = {
        "claude-code": [home / ".claude" / "skills" / "alfred" / "SKILL.md"],
        "devin-cli": [
            home / ".agents" / "skills" / "alfred" / "SKILL.md",
        ],
        "codex": [home / ".codex" / "AGENTS.md"],
        "github-copilot": [],
    }
    appdata = os.environ.get("APPDATA")
    if appdata:
        targets["devin-cli"].insert(0, Path(appdata) / "devin" / "skills" / "alfred" / "SKILL.md")
    return targets[host]


def should_skip_to_protect_user_file(host, target, force):
    if force or not target.exists():
        return False
    if host != "codex":
        return False
    content = target.read_text(encoding="utf-8-sig", errors="replace")
    return "Operate as **Alfred**" not in content and "Load the Alfred framework" not in content


def sync_one(host, alfred_home, target, create, force, dry_run):
    source = alfred_home / HOST_SOURCES[host]
    if not source.exists():
        raise SystemExit(f"Source not found for {host}: {source}")

    if not target.exists() and not create:
        print(f"SKIP {host}: target does not exist: {target}")
        return 0

    if should_skip_to_protect_user_file(host, target, force):
        print(f"SKIP {host}: target exists but is not an Alfred entry file: {target}")
        return 0

    if dry_run:
        print(f"DRY-RUN {host}: {source} -> {target}")
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"SYNC {host}: {source} -> {target}")
    return 1


def command_exists_in_hooks(settings, command):
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return False
    for entries in hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            for hook in entry.get("hooks", []) if isinstance(entry, dict) else []:
                if isinstance(hook, dict) and hook.get("command") == command:
                    return True
    return False


def install_claude_code_usage_hook(alfred_home, settings_path, dry_run):
    settings_path = settings_path or (Path.home() / ".claude" / "settings.json")
    hook_script = alfred_home / "scripts" / "python" / "metrics" / "claude-code-usage-hook.py"
    if not hook_script.exists():
        raise SystemExit(f"Claude Code usage hook script not found: {hook_script}")

    command = f'python "{hook_script}"'
    if not settings_path.exists():
        settings = {}
    else:
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as error:
            raise SystemExit(f"Invalid Claude Code settings JSON at {settings_path}: {error}") from error

    if command_exists_in_hooks(settings, command):
        print(f"OK claude-code hook: already installed in {settings_path}")
        return 0

    hooks = settings.setdefault("hooks", {})
    stop_hooks = hooks.setdefault("Stop", [])
    stop_hooks.append({"hooks": [{"type": "command", "command": command}]})

    if dry_run:
        print(f"DRY-RUN claude-code hook: would add Stop hook to {settings_path}")
        return 1

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    print(f"SYNC claude-code hook: installed Stop hook in {settings_path}")
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", "-Host", dest="host", choices=sorted(HOST_SOURCES), default="")
    parser.add_argument("--all", "-All", dest="all_hosts", action="store_true")
    parser.add_argument("--alfred-home", "-AlfredHome", dest="alfred_home", default=os.environ.get("ALFRED_HOME", ""))
    parser.add_argument("--target", "-Target", dest="targets", action="append", default=[])
    parser.add_argument("--create", "-Create", dest="create", action="store_true")
    parser.add_argument("--force", "-Force", dest="force", action="store_true")
    parser.add_argument("--dry-run", "-DryRun", dest="dry_run", action="store_true")
    parser.add_argument("--install-hooks", "-InstallHooks", dest="install_hooks", action="store_true",
                        help="also install host runtime hooks when supported")
    parser.add_argument("--claude-settings-path", "-ClaudeSettingsPath", dest="claude_settings_path", default="",
                        help="override Claude Code settings path (useful for validation/dry-run)")
    args = parser.parse_args()

    if not args.host and not args.all_hosts:
        raise SystemExit("Provide -Host <host> or -All.")

    alfred_home = Path(args.alfred_home).expanduser() if args.alfred_home else Path.home() / ".alfred"
    hosts = sorted(HOST_SOURCES) if args.all_hosts else [args.host]
    synced = 0

    for host in hosts:
        targets = [Path(item).expanduser() for item in args.targets] if args.targets else default_targets(host)
        if not targets:
            print(f"SKIP {host}: no default native target; pass -Target explicitly.")
        else:
            for target in targets:
                synced += sync_one(host, alfred_home, target, args.create, args.force, args.dry_run)
        if args.install_hooks and host == "claude-code":
            settings_path = Path(args.claude_settings_path).expanduser() if args.claude_settings_path else None
            synced += install_claude_code_usage_hook(alfred_home, settings_path, args.dry_run)
        elif args.install_hooks:
            print(f"SKIP {host} hooks: no runtime hook installer.")

    print(f"Host shim sync completed. synced={synced}")


if __name__ == "__main__":
    main()
