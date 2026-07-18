"""Draft and demand lifecycle file operations."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil

from shared.cli.git_service import framework_stamp
from shared.cli.requirements import append_question, parse
from shared.cli.result import CommandResult
from shared.common import read_state_fields, write_state_fields
from shared.toolbar.service import render_toolbar

ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,79}$", re.I)
PHASES = ("Inception", "Design", "Execution", "Validate", "Operation")


def _slug(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:48] or "demanda"


def _copy(template_root, name, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(template_root) / name, target)


def draft(hub, framework_root, title, draft_id="", dry_run=False):
    hub = Path(hub).resolve()
    draft_id = draft_id or f"draft-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{_slug(title)}"
    if not ID.match(draft_id):
        return CommandResult("demand draft", "blocked", message="ID de rascunho invalido.")
    target = hub / "000-drafts" / draft_id
    state = target / "001-state.md"
    req = target / "01-inception" / "003-requirements.md"
    if state.exists() and req.exists():
        return CommandResult("demand draft", message=f"Rascunho ja existe: {target}", data={"draft": str(target)})
    if dry_run:
        return CommandResult("demand draft", message=f"Rascunho seria criado em {target}", data={"draft": str(target)})
    _copy(Path(framework_root) / "templates" / "hub", "state.md", state)
    _copy(Path(framework_root) / "templates" / "hub", "draft-requirements.md", req)
    sigla = _slug(hub.parent.name).replace("itau-", "")
    _replace_metadata(req, {
        "{{initiative_proposal}}": f"iniciativa-001-{_slug(title)}",
        "{{demand_proposal}}": f"001-{_slug(title)}",
        "{{sigla_proposal}}": sigla,
        "{{scope_proposal}}": title,
    })
    stamp = framework_stamp(framework_root)
    write_state_fields(state, {
        "id": draft_id, "title": title, "lane": "pending", "framework version": stamp["version"],
        "framework ref": stamp["ref"], "framework commit": stamp["commit"], "current phase": "Inception",
        "current step": "framing", "next step": "preencher 003-requirements.md", "status": "draft",
    }, section="Demand")
    return CommandResult("demand draft", changed=True, message=f"Rascunho criado: {target}", data={"draft": str(target), "requirements": str(req)}, next_steps=[f"Preencha {req} e informe `pronto`."])


def _replace_metadata(path, values):
    text = path.read_text(encoding="utf-8")
    for old, new in values.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def _add_table_row(path, heading, row):
    path = Path(path)
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip().lower() == f"## {heading}".lower()), -1)
    if start < 0 or row in lines:
        return
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    blank = next((i for i in range(start + 1, end) if re.fullmatch(r"\|(?:\s*\|)+", lines[i])), -1)
    if blank >= 0:
        lines[blank] = row
    else:
        lines.insert(end, row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _close_index_row(index, demand_id, initiative, summary):
    index = Path(index)
    if not index.exists():
        return
    lines = index.read_text(encoding="utf-8-sig").splitlines()
    lines = [line for line in lines if not (line.startswith(f"| {demand_id} | {initiative} |") and "001-state.md" in line)]
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _add_table_row(index, "Closed demands",
                   f"| {demand_id} | {initiative} | {datetime.now(timezone.utc).date()} | {summary} | nenhum |")


def start(draft_path, framework_root, dry_run=False):
    draft_path = Path(draft_path).resolve()
    req = draft_path / "01-inception" / "003-requirements.md"
    if not req.exists():
        return CommandResult("demand start", "blocked", message=f"Requirements do rascunho nao encontrado: {req}")
    values, _required, missing = parse(req)
    if missing:
        return CommandResult("demand start", "blocked", message=f"Requirements incompleto; faltam: {', '.join(missing)}", next_steps=[f"Preencha {req}"])
    lane = values["lane"].strip().split()[0].lower()
    lane_names = {"fast": "FAST", "standard": "Standard", "safe": "SAFE"}
    if lane not in lane_names:
        return CommandResult("demand start", "blocked", message="Lane deve ser FAST, Standard ou SAFE.")
    initiative, demand_id = values["initiative_id"], values["demand_id"]
    if not ID.match(initiative) or not ID.match(demand_id):
        return CommandResult("demand start", "blocked", message="IDs de iniciativa ou demanda invalidos.")
    hub = draft_path.parent.parent
    target = hub / initiative / demand_id
    if target.exists():
        return CommandResult("demand start", "blocked", message=f"Demanda ja existe: {target}")
    app_value = values["target_app"].strip()
    app_repo = None
    if app_value.lower() not in {"nenhum", "b", "apenas hub, sem app afetado."}:
        app_repo = Path(app_value).expanduser()
        if not app_repo.is_absolute():
            app_repo = (hub.parent / app_repo).resolve()
        if not app_repo.exists() or not app_repo.is_dir():
            return CommandResult("demand start", "blocked", message=f"Caminho App nao encontrado: {app_repo}")
    if dry_run:
        return CommandResult("demand start", message=f"Demanda seria criada em {target}", data={"demand": str(target), "lane": lane_names[lane]})
    templates = Path(framework_root) / "templates" / "hub"
    (target / "01-inception").mkdir(parents=True)
    (target / "02-design").mkdir()
    (target / "03-execution").mkdir()
    (target / "04-validate").mkdir()
    (target / "05-operation").mkdir()
    shutil.move(str(draft_path / "001-state.md"), target / "001-state.md")
    shutil.move(str(req), target / "01-inception" / "003-requirements.md")
    for template, relative in (
        ("problem.md", "01-inception/002-problem.md"), ("risk.md", "01-inception/004-risk.md"),
        ("audit.md", "05-operation/007-audit.md"), ("metrics.md", "05-operation/008-metrics.md"),
    ):
        _copy(templates, template, target / relative)
    if lane_names[lane] != "FAST":
        for template, relative in (
            ("tech-inception.md", "01-inception/005-tech-inception.md"),
            ("decisions.md", "02-design/006-decisions.md"),
            ("execution-plan.md", "03-execution/012-execution-plan.md"),
            ("validation-evidence.md", "04-validate/013-validation-evidence.md"),
        ):
            _copy(templates, template, target / relative)
    (target / "05-operation" / "011-observability-log.jsonl").write_text("", encoding="utf-8")
    stamp = framework_stamp(framework_root)
    state = target / "001-state.md"
    write_state_fields(state, {
        "id": demand_id, "sigla": values["sigla"], "initiative id": initiative,
        "lane": lane_names[lane], "framework version": stamp["version"], "framework ref": stamp["ref"],
        "framework commit": stamp["commit"], "target app/source": values["target_app"],
        "artifact set": values["artifact_set"], "framing status": "confirmed",
        "current phase": "Inception", "current step": "problema e risco", "next step": "completar Inception",
        "status": "active", "observability schema": "alfred.observability.v2",
    }, section="Demand")
    initiative_file = hub / initiative / "001-initiative.md"
    if not initiative_file.exists():
        _copy(templates, "initiative.md", initiative_file)
        _replace_metadata(initiative_file, {"`iniciativa-<sequencia>-<iniciativa>`": f"`{initiative}`"})
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    event = {"schema_version": "alfred.observability.v2", "timestamp": now, "event": "demand_started",
             "initiative_id": initiative, "demand_id": demand_id, "phase": "Inception", "lane": lane_names[lane],
             "alfred": stamp, "artifacts_used": ["01-inception/003-requirements.md"]}
    (target / "05-operation" / "011-observability-log.jsonl").write_text(json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8")
    relative_state = f"{initiative}/{demand_id}/001-state.md"
    _add_table_row(hub / "001-index.md", "Open demands",
                   f"| {demand_id} | {initiative} | {lane_names[lane]} | Inception | active | {relative_state} | {now} | completar Inception |")
    _add_table_row(initiative_file, "Demands", f"- [{demand_id}]({demand_id}/001-state.md) - active")
    if app_repo is not None:
        app_target = app_repo / ".alfred-docs-app" / initiative / demand_id
        app_templates = Path(framework_root) / "templates" / "app"
        for template, relative in (
            ("index.md", "001-index.md"), ("reverse-eng.md", "01-inception/002-reverse-eng.md"),
            ("audit.md", "05-operation/005-audit.md"), ("metrics.md", "05-operation/006-metrics.md"),
        ):
            _copy(app_templates, template, app_target / relative)
        (app_target / "05-operation").mkdir(parents=True, exist_ok=True)
        (app_target / "05-operation" / "008-observability-log.jsonl").write_text(json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8")
        if lane_names[lane] != "FAST":
            _copy(app_templates, "spec.md", app_target / "02-design" / "003-spec.md")
    shutil.rmtree(draft_path)
    return CommandResult("demand start", changed=True, message=f"Demanda iniciada: {target}", data={"demand": str(target), "state": str(state), "lane": lane_names[lane]})


def demand_status(state_path):
    state = Path(state_path)
    if not state.exists():
        return CommandResult("demand status", "blocked", message=f"State nao encontrado: {state}")
    fields = read_state_fields(state)
    return CommandResult("demand status", message=f"{fields.get('id', '?')} | {fields.get('lane', '?')} | {fields.get('current phase', '?')} | {fields.get('status', '?')}", data=fields)


def checkpoint(state_path, framework_root, updates, question="", field_name="", options=None, recommended="", multiple=False, dry_run=False):
    state = Path(state_path).resolve()
    if not state.exists():
        return CommandResult("checkpoint", "blocked", message=f"State nao encontrado: {state}")
    if question:
        if not options:
            return CommandResult("checkpoint", "blocked", message="Pergunta material requer alternativas propostas via --option.")
        req = state.parent / "01-inception" / "003-requirements.md"
        if dry_run:
            return CommandResult("checkpoint", "blocked", message=f"Pergunta seria registrada em {req}")
        changed = append_question(req, question, field_name or f"checkpoint_{int(datetime.now().timestamp())}", options, recommended, multiple)
        return CommandResult("checkpoint", "blocked", changed=changed, message=f"Decisao pendente registrada em {req}", next_steps=[f"Responda em {req}; nenhuma resposta deve ficar apenas no chat."])
    phase = updates.get("current phase")
    if phase and phase not in PHASES:
        return CommandResult("checkpoint", "blocked", message=f"Fase invalida: {phase}")
    if dry_run:
        return CommandResult("checkpoint", message="Checkpoint seria atualizado.", data=updates)
    write_state_fields(state, updates, section="Progress")
    fields = read_state_fields(state)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    audit = state.parent / "05-operation" / "007-audit.md"
    if audit.exists():
        with audit.open("a", encoding="utf-8") as handle:
            handle.write(f"| {now} | Alfred CLI | {fields.get('current phase', '')} | Checkpoint | {fields.get('model', 'n/a')} | Estado atualizado | humano responsavel |\n")
    event = {"schema_version": fields.get("observability schema", "alfred.observability.v2"), "timestamp": now,
             "event": "checkpoint", "initiative_id": fields.get("initiative id", ""), "demand_id": fields.get("id", ""),
             "phase": fields.get("current phase", ""), "lane": fields.get("lane", ""),
             "alfred": framework_stamp(framework_root), "artifacts_used": ["001-state.md"]}
    log = state.parent / "05-operation" / "011-observability-log.jsonl"
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    warnings = []
    data = dict(fields)
    try:
        data["toolbar"] = render_toolbar(state, framework_root=framework_root, profile="text")
    except (OSError, ValueError) as error:
        warnings.append(f"Toolbar indisponivel: {error}")
    return CommandResult("checkpoint", changed=True, message=f"Checkpoint registrado para {fields.get('id', '')}.", data=data, warnings=warnings)


def close_readiness(state_path, framework_root, dry_run=False):
    state = Path(state_path).resolve()
    if not state.exists():
        return CommandResult("demand close", "blocked", message=f"State nao encontrado: {state}"), ""
    req = state.parent / "01-inception" / "003-requirements.md"
    summary = state.parent / "05-operation" / "009-summary.md"
    values, _required, _missing = parse(req) if req.exists() else ({}, [], [])
    acceptance = values.get("final_acceptance", "")
    if not acceptance:
        if req.exists() and not dry_run:
            append_question(req, "Qual e a decisao final? Inclua responsavel e evidencia em [Resposta].",
                            "final_acceptance", ["Aceitar a entrega", "Rejeitar a entrega", "Solicitar ajustes"], "A")
        return CommandResult("demand close", "blocked", changed=not dry_run,
                             message=f"Aceite final deve ser respondido em {req}."), ""
    text = state.read_text(encoding="utf-8")
    incomplete = [phase for phase in PHASES[:-1] if re.search(rf"- \[ \] {re.escape(phase)}", text)]
    if incomplete:
        return CommandResult("demand close", "blocked", message="Fases ainda abertas: " + ", ".join(incomplete)), ""
    template = Path(framework_root) / "templates" / "hub" / "summary.md"
    if not summary.exists():
        if not dry_run:
            _copy(template.parent, template.name, summary)
        return CommandResult("demand close", "blocked", changed=not dry_run,
                             message=f"Resumo criado e precisa ser preenchido: {summary}"), ""
    if summary.read_text(encoding="utf-8-sig").strip() == template.read_text(encoding="utf-8-sig").strip():
        return CommandResult("demand close", "blocked", message=f"Resumo ainda esta vazio: {summary}"), ""
    return CommandResult("demand close", message="Fechamento pronto para validacao estrita."), acceptance


def close(state_path, framework_root, acceptance, dry_run=False):
    state = Path(state_path).resolve()
    if dry_run:
        return CommandResult("demand close", message="Demanda seria encerrada apos validacao estrita.")
    text = state.read_text(encoding="utf-8")
    text = re.sub(r"- \[ \] Operation", "- [x] Operation", text)
    state.write_text(text, encoding="utf-8")
    write_state_fields(state, {"current phase": "Operation", "current step": "fechamento",
                               "next step": "demanda concluida", "status": "concluida"}, section="Progress")
    fields = read_state_fields(state)
    metrics = state.parent / "05-operation" / "008-metrics.md"
    if metrics.exists():
        mtext = metrics.read_text(encoding="utf-8")
        mtext = re.sub(r"(?m)^- closed:.*$", f"- closed: {datetime.now(timezone.utc).isoformat()}", mtext)
        mtext = re.sub(r"(?m)^- acceptance:.*$", f"- acceptance: {acceptance}", mtext)
        metrics.write_text(mtext, encoding="utf-8")
    recorded = checkpoint(state, framework_root, {"checkpoint": "closed"})
    hub = state.parent.parent.parent
    _close_index_row(hub / "001-index.md", fields.get("id", ""), fields.get("initiative id", ""),
                     f"{fields.get('initiative id', '')}/{fields.get('id', '')}/05-operation/009-summary.md")
    recorded.command = "demand close"
    recorded.message = f"Demanda {fields.get('id', '')} encerrada com aceite registrado no requirements."
    return recorded
