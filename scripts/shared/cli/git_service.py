"""Single-installation update service for ``~/.alfred``."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

from shared.cli.result import CommandResult
from shared.common import write_state_fields


def run_git(root, *args, timeout=60):
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return subprocess.CompletedProcess(args, 1, "", str(error))


def revision(root, ref="HEAD", short=False):
    args = ["rev-parse"] + (["--short"] if short else []) + [ref]
    result = run_git(root, *args)
    return result.stdout.strip() if result.returncode == 0 else ""


def framework_stamp(root):
    root = Path(root)
    version = (root / "VERSION").read_text(encoding="utf-8").strip() if (root / "VERSION").exists() else "unknown"
    return {"version": version, "ref": "origin/main", "commit": revision(root)}


@contextmanager
def update_lock(runtime, timeout=30):
    runtime.mkdir(parents=True, exist_ok=True)
    path = runtime / "framework-update.lock"
    started = time.monotonic()
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii"))
            os.close(fd)
            break
        except FileExistsError:
            if path.exists() and time.time() - path.stat().st_mtime > 600:
                path.unlink(missing_ok=True)
                continue
            if time.monotonic() - started >= timeout:
                raise TimeoutError("outra atualizacao do Alfred ainda esta em andamento")
            time.sleep(0.2)
    try:
        yield
    finally:
        path.unlink(missing_ok=True)


def status(root):
    root = Path(root).expanduser().resolve()
    if not root.exists():
        return CommandResult("framework status", "error", message=f"Framework nao encontrado: {root}")
    if not (root / ".git").exists():
        return CommandResult("framework status", message=f"Versao nao verificada: instalacao sem Git em {root}",
                             data={"verified": False}, warnings=["Nao foi possivel comparar com origin/main."])
    fetch = run_git(root, "fetch", "--quiet", "origin", "main")
    current = revision(root)
    remote = revision(root, "origin/main")
    dirty = bool(run_git(root, "status", "--porcelain").stdout.strip())
    data = {**framework_stamp(root), "current_commit": current, "remote_commit": remote, "dirty": dirty}
    data["branch"] = run_git(root, "branch", "--show-current").stdout.strip() or "detached"
    warnings = [] if fetch.returncode == 0 else [f"origin/main nao verificada: {fetch.stderr.strip() or 'rede indisponivel'}"]
    return CommandResult("framework status", message=f"Alfred {data['version']} em {current[:12] or 'desconhecido'}", data=data, warnings=warnings)


def _validate_candidate(root, candidate, state_path=""):
    python = shutil.which("python") or shutil.which("python3")
    if not python:
        return False, "Python nao encontrado para validar a atualizacao"
    added = run_git(root, "worktree", "add", "--quiet", "--detach", str(candidate), "origin/main", timeout=120)
    if added.returncode != 0:
        return False, added.stderr.strip() or "nao foi possivel criar o candidato"
    try:
        gate = subprocess.run(
            [python, str(candidate / "scripts" / "validators" / "validate-framework.py")],
            cwd=candidate, capture_output=True, text=True, timeout=180, check=False,
        )
        evidence = (gate.stdout + gate.stderr).strip()
        if gate.returncode != 0:
            return False, evidence
        migration = candidate / "scripts" / "workflow" / "migrate-state-v2.py"
        if state_path and Path(state_path).exists() and migration.exists():
            checked = subprocess.run(
                [python, str(migration), "--state-path", str(Path(state_path).resolve()), "--check", "--json"],
                cwd=candidate, capture_output=True, text=True, timeout=60, check=False,
            )
            evidence += "\n" + (checked.stdout + checked.stderr).strip()
            if checked.returncode != 0:
                return False, evidence
        return True, evidence
    finally:
        run_git(root, "worktree", "remove", "--force", str(candidate), timeout=60)


def _record_adoption(state_path, before, after, stamp):
    state = Path(state_path)
    if not state.exists():
        return
    write_state_fields(state, {
        "framework version": stamp["version"], "framework ref": stamp["ref"],
        "framework commit": after,
    }, section="Demand")
    audit = state.parent / "05-operation" / "007-audit.md"
    if audit.exists():
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        with audit.open("a", encoding="utf-8") as handle:
            handle.write(f"| {now} | Alfred CLI | Operation | Framework atualizado {before[:12]} -> {after[:12]} | n/a | Atualizacao adotada | humano responsavel |\n")
    metrics = state.parent / "05-operation" / "008-metrics.md"
    if metrics.exists():
        text = metrics.read_text(encoding="utf-8")
        for key, value in (("alfred version", stamp["version"]), ("alfred framework ref", stamp["ref"]),
                           ("alfred framework commit", after)):
            text = re.sub(rf"(?im)^- {re.escape(key)}:.*$", f"- {key}: {value}", text)
        metrics.write_text(text, encoding="utf-8")
    log = state.parent / "05-operation" / "011-observability-log.jsonl"
    if log.exists():
        fields = {}
        for line in state.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("- ") and ":" in line:
                key, value = line[2:].split(":", 1); fields[key.strip().lower()] = value.strip()
        event = {"schema_version": fields.get("observability schema", "alfred.observability.v2"),
                 "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                 "event": "framework_adopted", "initiative_id": fields.get("initiative id", ""),
                 "demand_id": fields.get("id", ""), "phase": fields.get("current phase", ""),
                 "lane": fields.get("lane", ""), "alfred": stamp,
                 "from_commit": before, "to_commit": after, "artifacts_used": ["001-state.md"]}
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def update(root, *, state_path="", dry_run=False, sync_hosts=True):
    root = Path(root).expanduser().resolve()
    if not root.exists():
        return CommandResult("framework update", "error", message=f"Framework nao encontrado: {root}")
    if not (root / ".git").exists():
        return CommandResult("framework update", message=f"Atualizacao nao verificada: instalacao sem Git em {root}",
                             data={"verified": False}, warnings=["Continuando com o framework Markdown local."])
    runtime = root / "runtime"
    try:
        with update_lock(runtime):
            dirty = run_git(root, "status", "--porcelain", "--untracked-files=no").stdout.strip()
            if dirty:
                return CommandResult("framework update", "blocked", message="A instalacao global possui alteracoes locais; atualizacao nao aplicada.")
            fetch = run_git(root, "fetch", "--quiet", "origin", "main", timeout=120)
            if fetch.returncode != 0:
                return CommandResult("framework update", message="Nao foi possivel verificar origin/main; versao atual mantida.",
                                     data={"verified": False, **framework_stamp(root)}, warnings=[fetch.stderr.strip()])
            before, after = revision(root), revision(root, "origin/main")
            if not after:
                return CommandResult("framework update", "error", message="origin/main nao possui um commit resolvivel.")
            if before == after:
                return CommandResult("framework update", message=f"Alfred ja esta atualizado em {before[:12]}", data=framework_stamp(root))
            if dry_run:
                return CommandResult("framework update", changed=False, message=f"Atualizacao disponivel: {before[:12]} -> {after[:12]}", data={"from": before, "to": after})
            candidate = Path(tempfile.mkdtemp(prefix="candidate-", dir=runtime))
            candidate.rmdir()
            try:
                valid, evidence = _validate_candidate(root, candidate, state_path)
            finally:
                shutil.rmtree(candidate, ignore_errors=True)
            if not valid:
                return CommandResult("framework update", "blocked", message="Candidato de origin/main falhou na validacao; versao atual preservada.", data={"evidence": evidence[-4000:]})
            checkout = run_git(root, "checkout", "--quiet", "main")
            if checkout.returncode != 0:
                return CommandResult("framework update", "blocked", message="A instalacao nao possui uma branch main local valida.", warnings=[checkout.stderr.strip()])
            promoted = run_git(root, "merge", "--ff-only", "origin/main", timeout=120)
            if promoted.returncode != 0:
                return CommandResult("framework update", "blocked", message="Nao foi possivel promover origin/main por fast-forward.", warnings=[promoted.stderr.strip()])
            stamp = framework_stamp(root)
            if state_path:
                _record_adoption(state_path, before, after, stamp)
            warnings = []
            sync_script = root / "scripts" / "workflow" / "sync-host-shims.py"
            if sync_hosts and sync_script.exists():
                synced = subprocess.run(
                    [sys.executable, str(sync_script), "--all", "--alfred-home", str(root), "--create"],
                    cwd=root, capture_output=True, text=True, timeout=60, check=False,
                )
                if synced.returncode != 0:
                    warnings.append("Framework atualizado, mas a sincronizacao dos hosts falhou: " +
                                    (synced.stderr.strip() or synced.stdout.strip()))
            runtime.mkdir(parents=True, exist_ok=True)
            (runtime / "last-update-check.json").write_text(json.dumps({
                "checked_at": datetime.now(timezone.utc).isoformat(), "commit": after,
            }), encoding="utf-8")
            return CommandResult("framework update", changed=True, message=f"Alfred atualizado {before[:12]} -> {after[:12]}", data=stamp, warnings=warnings)
    except TimeoutError as error:
        return CommandResult("framework update", "blocked", message=str(error))
