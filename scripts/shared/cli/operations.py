"""Adapters around existing validators, usage parsers and host synchronizers."""

import json
from pathlib import Path
import shutil
import subprocess
import sys

from shared.cli.result import CommandResult


def doctor(framework_root):
    root = Path(framework_root).expanduser().resolve()
    checks = {
        "python": sys.version.split()[0],
        "git": shutil.which("git") or "",
        "framework": str(root) if root.exists() else "",
        "framework_git": (root / ".git").exists(),
        "validator": (root / "scripts/validators/validate-framework.py").exists(),
        "devin_skill": (root / "hosts/devin-cli/SKILL.md").exists(),
    }
    missing = [key for key in ("git", "framework", "validator") if not checks[key]]
    status = "blocked" if missing else "ok"
    return CommandResult("doctor", status, message="Ambiente Alfred pronto." if not missing else f"Ambiente incompleto: {', '.join(missing)}", data=checks)


def run_command(command, args, *, cwd=None, json_output=False, changes_files=False):
    process = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=False)
    output = ((process.stdout or "") + (process.stderr or "")).strip()
    status = "ok" if process.returncode == 0 else "blocked"
    data = {"output": output, "returncode": process.returncode}
    if json_output:
        try:
            data["result"] = json.loads(process.stdout or "")
        except json.JSONDecodeError:
            pass
    return CommandResult(command, status, changed=changes_files and process.returncode == 0,
                         message=output or f"{command}: {status}", data=data)


def validate(framework_root, state_path, app_path="", strict=False):
    script = Path(framework_root) / "scripts/validators/validate-demand.py"
    args = [sys.executable, str(script), "--hub-demand-path", str(Path(state_path).resolve().parent)]
    if app_path:
        args += ["--app-demand-path", app_path]
    if strict:
        args.append("--strict")
    return run_command("demand validate", args, cwd=framework_root)


def usage_import(framework_root, host, state_path, input_path, rate_card="", dry_run=False):
    if dry_run:
        return CommandResult("usage import", message=f"Uso de {host} seria importado em {state_path}.")
    if host == "claude-code":
        if input_path == "-":
            return CommandResult("usage import", "blocked", message="Claude Code requer um arquivo JSON do ccusage.")
        script = Path(framework_root) / "scripts/metrics/import-ccusage.py"
        args = [sys.executable, str(script), "--state-path", state_path, "--input-path", input_path,
                "--host", host, "--emit-json", "--no-append"]
        return run_command("usage import", args, cwd=framework_root, json_output=True, changes_files=True)
    if host != "devin":
        return CommandResult("usage import", "blocked", message=f"Host {host} nao possui fonte de uso aprovada.")
    text = Path(input_path).read_text(encoding="utf-8-sig") if input_path != "-" else sys.stdin.read()
    script = Path(framework_root) / "scripts/metrics/session-cost.py"
    args = [sys.executable, str(script), "--state-path", state_path, "--usage-text", text, "--json"]
    if rate_card:
        args += ["--rate-card", rate_card]
    return run_command("usage import", args, cwd=framework_root, json_output=True, changes_files=True)


def sync_host(framework_root, host, install_hooks=False, dry_run=False):
    script = Path(framework_root) / "scripts/workflow/sync-host-shims.py"
    args = [sys.executable, str(script), "--host", host, "--alfred-home", str(framework_root), "--create"]
    if install_hooks:
        args.append("--install-hooks")
    if dry_run:
        args.append("--dry-run")
    return run_command("host sync", args, cwd=framework_root, changes_files=not dry_run)
