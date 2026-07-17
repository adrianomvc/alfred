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
    appdata = os.environ.get("APPDATA")

    # DEVIN CLI global skills path (docs.devin.ai/cli/extensibility/skills):
    # Windows -> %APPDATA%\devin\skills; POSIX -> ~/.config/devin/skills.
    # This is the only documented global skills location. ~/.agents/skills is NOT
    # a Devin skills path: read_config_from.agents_standard imports rules from
    # AGENTS.md/AGENT.md/.windsurfrules in the workspace root, not global skills.
    if appdata:
        devin_targets = [Path(appdata) / "devin" / "skills" / "alfred" / "SKILL.md"]
    else:
        devin_targets = [home / ".config" / "devin" / "skills" / "alfred" / "SKILL.md"]

    targets = {
        "claude-code": [home / ".claude" / "skills" / "alfred" / "SKILL.md"],
        "devin-cli": devin_targets,
        "codex": [home / ".codex" / "AGENTS.md"],
        "github-copilot": [],
    }
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

    if target.exists() and _same_bytes(source, target):
        # Fast-path: nothing changed since the last sync, so skip the rewrite.
        # Keeps re-running the installer on every boot cheap.
        print(f"OK {host}: already up to date: {target}")
        return 0

    if dry_run:
        print(f"DRY-RUN {host}: {source} -> {target}")
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"SYNC {host}: {source} -> {target}")
    return 1


def _same_bytes(source, target):
    try:
        return source.read_bytes() == target.read_bytes()
    except OSError:
        return False


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


def prune_usage_hook_entries(settings, hook_filename, keep_command):
    """Remove hook entries that reference ``hook_filename`` but are not ``keep_command``.

    Matching by the script filename (not the exact command string) makes re-runs
    self-healing: a stale entry left by an earlier layout (e.g. an old
    ``scripts/python/metrics/`` path) is dropped instead of coexisting with the
    current one. Returns True if ``keep_command`` is already present afterwards.
    """
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return False
    present = False
    for group_name, entries in list(hooks.items()):
        if not isinstance(entries, list):
            continue
        kept_entries = []
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("hooks"), list):
                kept_entries.append(entry)
                continue
            kept_hooks = []
            for hook in entry["hooks"]:
                command = hook.get("command") if isinstance(hook, dict) else None
                if isinstance(command, str) and hook_filename in command:
                    if command == keep_command and not present:
                        present = True
                        kept_hooks.append(hook)
                    # stale path, or a duplicate of keep_command -> drop it
                    continue
                kept_hooks.append(hook)
            if kept_hooks:
                entry["hooks"] = kept_hooks
                kept_entries.append(entry)
            # entry with no surviving hooks -> drop it
        hooks[group_name] = kept_entries
    return present


def install_claude_code_usage_hook(alfred_home, settings_path, dry_run):
    settings_path = settings_path or (Path.home() / ".claude" / "settings.json")
    hook_script = alfred_home / "scripts" / "metrics" / "claude-code-usage-hook.py"
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

    before = json.dumps(settings, sort_keys=True)
    already_present = prune_usage_hook_entries(settings, hook_script.name, command)
    if not already_present:
        hooks = settings.setdefault("hooks", {})
        stop_hooks = hooks.setdefault("Stop", [])
        stop_hooks.append({"hooks": [{"type": "command", "command": command}]})
    after = json.dumps(settings, sort_keys=True)

    if before == after:
        print(f"OK claude-code hook: already installed in {settings_path}")
        return 0

    if dry_run:
        action = "reconcile" if already_present else "add"
        print(f"DRY-RUN claude-code hook: would {action} Stop hook in {settings_path}")
        return 1

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    action = "reconciled" if already_present else "installed"
    print(f"SYNC claude-code hook: {action} Stop hook in {settings_path}")
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
