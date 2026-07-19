"""Argument parser and dispatch for the canonical Alfred CLI."""

import argparse
import os
from pathlib import Path
import sys

import shared.cli.demand as demand
from shared.cli.git_service import status as framework_status, update as framework_update
from shared.cli.operations import doctor, run_command, sync_host, usage_import, validate
from shared.cli.requirements import resolve_path, status as requirements_status
from shared.cli.result import CommandResult, render
from shared.cli.workspace import detect, init_hub


def _parser():
    parser = argparse.ArgumentParser(prog="alfred")
    sub = parser.add_subparsers(dest="group", required=True)
    sub.add_parser("doctor")
    framework = sub.add_parser("framework").add_subparsers(dest="action", required=True)
    framework.add_parser("status")
    update = framework.add_parser("update"); update.add_argument("--state", default="")
    workspace = sub.add_parser("workspace").add_subparsers(dest="action", required=True)
    workspace.add_parser("detect").add_argument("--path", default=".")
    sigla = sub.add_parser("sigla").add_subparsers(dest="action", required=True)
    init = sigla.add_parser("init"); init.add_argument("--root", default="."); init.add_argument("--role", choices=["hub"], default="hub"); init.add_argument("--sigla", default="")
    demand_group = sub.add_parser("demand").add_subparsers(dest="action", required=True)
    draft = demand_group.add_parser("draft"); draft.add_argument("--hub", default="alfred-docs-hub"); draft.add_argument("--title", required=True); draft.add_argument("--draft-id", default="")
    start = demand_group.add_parser("start"); start.add_argument("--draft", required=True)
    dstatus = demand_group.add_parser("status"); dstatus.add_argument("--state", required=True)
    dvalidate = demand_group.add_parser("validate"); dvalidate.add_argument("--state", required=True); dvalidate.add_argument("--app", default=""); dvalidate.add_argument("--strict", action="store_true")
    close = demand_group.add_parser("close"); close.add_argument("--state", required=True)
    requirements = sub.add_parser("requirements").add_subparsers(dest="action", required=True)
    req_status = requirements.add_parser("status"); req_status.add_argument("--draft", default=""); req_status.add_argument("--state", default="")
    checkpoint = sub.add_parser("checkpoint"); checkpoint.add_argument("--state", required=True); checkpoint.add_argument("--phase", default=""); checkpoint.add_argument("--step", default=""); checkpoint.add_argument("--next", default=""); checkpoint.add_argument("--status", default=""); checkpoint.add_argument("--model", default=""); checkpoint.add_argument("--question", default=""); checkpoint.add_argument("--field", default=""); checkpoint.add_argument("--option", action="append", default=[]); checkpoint.add_argument("--recommended", default=""); checkpoint.add_argument("--multiple", action="store_true")
    usage = sub.add_parser("usage").add_subparsers(dest="action", required=True)
    imp = usage.add_parser("import"); imp.add_argument("--host", required=True); imp.add_argument("--state", required=True); imp.add_argument("--input", required=True); imp.add_argument("--rate-card", default="")
    host = sub.add_parser("host").add_subparsers(dest="action", required=True)
    sync = host.add_parser("sync"); sync.add_argument("--host", required=True); sync.add_argument("--install-hooks", action="store_true")
    return parser


def _extract_globals(argv):
    argv = list(argv)
    as_json = "--json" in argv
    dry_run = "--dry-run" in argv
    argv = [item for item in argv if item not in ("--json", "--dry-run")]
    root = os.environ.get("ALFRED_HOME", str(Path.home() / ".alfred"))
    if "--alfred-home" in argv:
        index = argv.index("--alfred-home")
        try:
            root = argv[index + 1]
            del argv[index:index + 2]
        except IndexError:
            pass
    return argv, Path(root).expanduser().resolve(), as_json, dry_run


def dispatch(args, root, dry_run):
    key = (args.group, getattr(args, "action", ""))
    if args.group == "doctor": return doctor(root)
    if key == ("framework", "status"): return framework_status(root)
    if key == ("framework", "update"): return framework_update(root, state_path=args.state, dry_run=dry_run)
    if key == ("workspace", "detect"): return detect(args.path)
    if key == ("sigla", "init"): return init_hub(args.root, root, args.sigla, dry_run)
    if key == ("demand", "draft"): return demand.draft(args.hub, root, args.title, args.draft_id, dry_run)
    if key == ("demand", "start"): return demand.start(args.draft, root, dry_run)
    if key == ("demand", "status"): return demand.demand_status(args.state)
    if key == ("demand", "validate"): return validate(root, args.state, args.app, args.strict)
    if key == ("demand", "close"):
        readiness, acceptance = demand.close_readiness(args.state, root, dry_run)
        if readiness.status != "ok":
            return readiness
        if not dry_run:
            gate = validate(root, args.state, strict=True)
            if gate.status != "ok":
                gate.command = "demand close"
                gate.message = "Fechamento bloqueado pela validacao estrita.\n" + gate.message
                return gate
        return demand.close(args.state, root, acceptance, dry_run)
    if key == ("requirements", "status"):
        try: return requirements_status(resolve_path(draft=args.draft, state=args.state))
        except ValueError as error: return CommandResult("requirements status", "blocked", message=str(error))
    if args.group == "checkpoint":
        adoption = framework_update(root, state_path=args.state, dry_run=dry_run)
        if adoption.status != "ok":
            adoption.command = "checkpoint"
            adoption.message = "Checkpoint bloqueado: " + adoption.message
            return adoption
        updates = {key: value for key, value in {"current phase": args.phase, "current step": args.step, "next step": args.next, "status": args.status, "model": args.model}.items() if value}
        result = demand.checkpoint(args.state, root, updates, args.question, args.field, args.option, args.recommended, args.multiple, dry_run)
        if result.status == "ok" and not dry_run:
            budget = run_command("budget status", [sys.executable, str(root / "scripts/metrics/budget-monitor.py"), "--state-path", args.state, "--json"], cwd=root, json_output=True)
            measured = budget.data.get("result", {})
            result.data["budget"] = measured
            if measured.get("status") == "near":
                result.warnings.append("Orcamento proximo do limite; proponha acelerar apenas subatividades opcionais.")
            elif measured.get("status") == "exceeded":
                result.status = "blocked"
                result.message += " Orcamento excedido; entregue versus orcado deve ser relatado antes de continuar."
        return result
    if key == ("usage", "import"): return usage_import(root, args.host, args.state, args.input, args.rate_card, dry_run)
    if key == ("host", "sync"): return sync_host(root, args.host, args.install_hooks, dry_run)
    return CommandResult("unknown", "error", message="Comando nao implementado.")


def run(argv=None):
    argv, root, as_json, dry_run = _extract_globals(sys.argv[1:] if argv is None else argv)
    try:
        args = _parser().parse_args(argv)
        result = dispatch(args, root, dry_run)
    except (OSError, ValueError) as error:
        result = CommandResult("alfred", "error", message=str(error))
    print(render(result, as_json))
    return result.exit_code
