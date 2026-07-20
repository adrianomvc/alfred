"""Argument parser and dispatch for the canonical Alfred CLI."""

import argparse
import os
from pathlib import Path
import sys

import shared.cli.demand as demand
from shared.cli.git_service import status as framework_status, update as framework_update, update_check_advice
from shared.cli.operations import doctor, run_command, sync_host, usage_import, validate
from shared.cli.requirements import resolve_path, status as requirements_status
from shared.cli.result import CommandResult, render
from shared.cli.workspace import detect, init_hub
from shared.common import read_state_fields


def _globals_parser():
    # SUPPRESS keeps a subparser from clobbering a value the root parser
    # already set (argparse re-applies subparser defaults onto the namespace);
    # run() resolves the fallbacks with getattr.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", dest="as_json", default=argparse.SUPPRESS)
    common.add_argument("--dry-run", action="store_true", dest="dry_run", default=argparse.SUPPRESS)
    common.add_argument("--alfred-home", dest="alfred_home", default=argparse.SUPPRESS)
    return common


def _parser():
    common = _globals_parser()
    parser = argparse.ArgumentParser(prog="alfred", parents=[common])
    sub = parser.add_subparsers(dest="group", required=True)
    sub.add_parser("doctor", parents=[common])
    framework = sub.add_parser("framework").add_subparsers(dest="action", required=True)
    framework.add_parser("status", parents=[common])
    update = framework.add_parser("update", parents=[common]); update.add_argument("--state", default="")
    workspace = sub.add_parser("workspace").add_subparsers(dest="action", required=True)
    workspace.add_parser("detect", parents=[common]).add_argument("--path", default=".")
    sigla = sub.add_parser("sigla").add_subparsers(dest="action", required=True)
    init = sigla.add_parser("init", parents=[common]); init.add_argument("--root", default="."); init.add_argument("--role", choices=["hub"], default="hub"); init.add_argument("--sigla", default="")
    demand_group = sub.add_parser("demand").add_subparsers(dest="action", required=True)
    draft = demand_group.add_parser("draft", parents=[common]); draft.add_argument("--hub", default="alfred-docs-hub"); draft.add_argument("--title", required=True); draft.add_argument("--draft-id", default="")
    start = demand_group.add_parser("start", parents=[common]); start.add_argument("--draft", required=True); start.add_argument("--confirmed-by", default="")
    dstatus = demand_group.add_parser("status", parents=[common]); dstatus.add_argument("--state", required=True)
    dvalidate = demand_group.add_parser("validate", parents=[common]); dvalidate.add_argument("--state", required=True); dvalidate.add_argument("--app", default=""); dvalidate.add_argument("--strict", action="store_true")
    close = demand_group.add_parser("close", parents=[common]); close.add_argument("--state", required=True)
    requirements = sub.add_parser("requirements").add_subparsers(dest="action", required=True)
    req_status = requirements.add_parser("status", parents=[common]); req_status.add_argument("--draft", default=""); req_status.add_argument("--state", default="")
    checkpoint = sub.add_parser("checkpoint", parents=[common]); checkpoint.add_argument("--state", required=True); checkpoint.add_argument("--phase", default=""); checkpoint.add_argument("--step", default=""); checkpoint.add_argument("--next", default=""); checkpoint.add_argument("--status", default=""); checkpoint.add_argument("--model", default=""); checkpoint.add_argument("--complete", default=""); checkpoint.add_argument("--force", default="", metavar="JUSTIFICATIVA"); checkpoint.add_argument("--question", default=""); checkpoint.add_argument("--field", default=""); checkpoint.add_argument("--option", action="append", default=[]); checkpoint.add_argument("--recommended", default=""); checkpoint.add_argument("--multiple", action="store_true")
    usage = sub.add_parser("usage").add_subparsers(dest="action", required=True)
    imp = usage.add_parser("import", parents=[common]); imp.add_argument("--host", required=True); imp.add_argument("--state", required=True); imp.add_argument("--input", required=True); imp.add_argument("--rate-card", default="")
    host = sub.add_parser("host").add_subparsers(dest="action", required=True)
    sync = host.add_parser("sync", parents=[common]); sync.add_argument("--host", required=True); sync.add_argument("--install-hooks", action="store_true")
    return parser


def _app_demand_path(state_path):
    """Resolve the App demand folder recorded in the state, when it exists."""
    state = Path(state_path).resolve()
    fields = read_state_fields(state)
    app_value = fields.get("target app/source", "").strip()
    if not app_value or app_value.lower() in demand.NO_APP:
        return ""
    app_repo = Path(app_value).expanduser()
    if not app_repo.is_absolute():
        app_repo = (state.parent.parent.parent.parent / app_value).resolve()
    app_demand = app_repo / ".alfred-docs-app" / fields.get("initiative id", "") / fields.get("id", "")
    return str(app_demand) if app_demand.exists() else ""


def _budget_gate(root, state_path):
    """Budget check before any checkpoint mutation. Fail loud, never silent."""
    fields = read_state_fields(Path(state_path))
    on_limit = fields.get("budget on limit", "pause-and-ask").strip().lower() or "pause-and-ask"
    budget = run_command("budget status", [sys.executable, str(root / "scripts/metrics/budget-monitor.py"),
                                          "--state-path", str(state_path), "--json"],
                         cwd=root, json_output=True)
    measured = budget.data.get("result", {})
    if budget.status != "ok" and not measured:
        detail = budget.message.splitlines()[0] if budget.message else "sem detalhe"
        return measured, [f"Monitor de orcamento falhou; orcamento nao verificado neste checkpoint: {detail}"], None
    warnings = []
    if measured.get("status") == "near":
        warnings.append("Orcamento proximo do limite; proponha acelerar apenas subatividades opcionais.")
    elif measured.get("status") == "exceeded":
        if on_limit == "warn":
            warnings.append("Orcamento excedido (budget on limit: warn); registre entregue versus orcado e siga com aval humano.")
        else:
            blocked = CommandResult("checkpoint", "blocked",
                                    message="Orcamento excedido; entregue versus orcado deve ser relatado antes de continuar.",
                                    data={"budget": measured})
            return measured, warnings, blocked
    return measured, warnings, None


def dispatch(args, root, dry_run):
    key = (args.group, getattr(args, "action", ""))
    if args.group == "doctor": return doctor(root)
    if key == ("framework", "status"): return framework_status(root)
    if key == ("framework", "update"): return framework_update(root, state_path=args.state, dry_run=dry_run)
    if key == ("workspace", "detect"): return detect(args.path)
    if key == ("sigla", "init"): return init_hub(args.root, root, args.sigla, dry_run)
    if key == ("demand", "draft"): return demand.draft(args.hub, root, args.title, args.draft_id, dry_run)
    if key == ("demand", "start"): return demand.start(args.draft, root, args.confirmed_by, dry_run)
    if key == ("demand", "status"): return demand.demand_status(args.state)
    if key == ("demand", "validate"): return validate(root, args.state, args.app, args.strict)
    if key == ("demand", "close"):
        readiness, acceptance = demand.close_readiness(args.state, root, dry_run)
        if readiness.status != "ok":
            return readiness
        if not dry_run:
            gate = validate(root, args.state, app_path=_app_demand_path(args.state), strict=True)
            if gate.status != "ok":
                gate.command = "demand close"
                gate.message = "Fechamento bloqueado pela validacao estrita.\n" + gate.message
                return gate
        return demand.close(args.state, root, acceptance, dry_run)
    if key == ("requirements", "status"):
        try: return requirements_status(resolve_path(draft=args.draft, state=args.state))
        except ValueError as error: return CommandResult("requirements status", "blocked", message=str(error))
    if args.group == "checkpoint":
        updates = {field: value for field, value in {"current phase": args.phase, "current step": args.step, "next step": args.next, "status": args.status, "model": args.model}.items() if value}
        measured, budget_warnings, blocked = ({}, [], None)
        if not dry_run and not args.question:
            measured, budget_warnings, blocked = _budget_gate(root, args.state)
            if blocked is not None:
                return blocked
        result = demand.checkpoint(args.state, root, updates, args.question, args.field, args.option,
                                   args.recommended, args.multiple, complete=args.complete,
                                   force_reason=args.force, dry_run=dry_run)
        result.warnings.extend(budget_warnings)
        if measured:
            result.data["budget"] = measured
        if not dry_run:
            advice = update_check_advice(root)
            if advice:
                result.warnings.append(advice)
        return result
    if key == ("usage", "import"): return usage_import(root, args.host, args.state, args.input, args.rate_card, dry_run)
    if key == ("host", "sync"): return sync_host(root, args.host, args.install_hooks, dry_run)
    return CommandResult("unknown", "error", message="Comando nao implementado.")


def run(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    try:
        args = _parser().parse_args(argv)
        as_json = getattr(args, "as_json", False)
        dry_run = getattr(args, "dry_run", False)
        home = getattr(args, "alfred_home", "") or os.environ.get("ALFRED_HOME", str(Path.home() / ".alfred"))
        root = Path(home).expanduser().resolve()
        result = dispatch(args, root, dry_run)
    except SystemExit:
        raise
    except (OSError, ValueError) as error:
        as_json, result = False, CommandResult("alfred", "error", message=str(error))
    except Exception as error:  # never leak a raw traceback to the operator
        as_json, result = False, CommandResult("alfred", "error", message=f"{type(error).__name__}: {error}")
    print(render(result, as_json))
    return result.exit_code
