"""Draft and demand lifecycle file operations."""

from datetime import datetime, timezone
import os
from pathlib import Path
import re
import shutil

from shared.cli.git_service import framework_stamp, run_git
from shared.cli.requirements import append_question, parse
from shared.cli.result import CommandResult
from shared.common import (OBSERVABILITY_SCHEMA, append_event, lifecycle_event,
                           read_state_fields, write_state_fields)
from shared.risk import LANES, propose
from shared.sdd_gate import run as run_sdd_gate
from shared.toolbar.service import render_toolbar

ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,79}$", re.I)
PHASES = ("Inception", "Design", "Execution", "Validate", "Operation")
NO_APP = {"nenhum", "b", "apenas hub, sem app afetado."}
RISK_FIELDS = {"risk_reversibility": "reversibility", "risk_blast_radius": "blast_radius",
               "risk_sensitive_data": "sensitive_data", "risk_customer_impact": "customer_impact",
               "risk_cost": "cost"}
CX_FIELDS = {"cx_components": "components", "cx_novelty": "novelty", "cx_ambiguity": "ambiguity",
             "cx_integrations": "integrations", "cx_effort": "effort"}
CLOSE_EVIDENCE = {
    "Standard": [
        ("close_pr_url", "Qual e o link do PR desta demanda?"),
        ("close_merge_state", "O PR foi mesclado na branch protegida? Informe o estado e o commit."),
        ("close_reviewer", "Quem revisou tecnicamente a entrega?"),
    ],
    "SAFE": [
        ("close_approvals", "Quais papeis aprovaram (Tech Lead, PM, QA, Security, Sponsor)?"),
        ("close_rollback_plan", "Qual e o plano de rollback validado?"),
        ("close_security_review", "Qual foi o resultado da revisao de seguranca?"),
    ],
}


def _slug(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:48] or "demanda"


def _copy(template_root, name, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(template_root) / name, target)


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _derive_sigla(hub, app_repo=None):
    """Sigla is an auto-derived display label (core/boot.md): never asked."""
    candidates = []
    if app_repo is not None:
        candidates.append(Path(app_repo).name)
    candidates.append(Path(hub).resolve().parent.name)
    for name in candidates:
        match = re.match(r"(?i)itau-([a-z0-9]+)", name)
        if match:
            return match.group(1).lower()
    for name in candidates:
        slug = _slug(name)
        if slug and slug != "demanda":
            return slug
    return "unknown"


def _score(value):
    match = re.match(r"\s*([012])\b", str(value))
    return int(match.group(1)) if match else None


def _emit(state, framework_root, event_type, action, step=""):
    fields = read_state_fields(state)
    event = lifecycle_event(fields, framework_stamp(framework_root), event_type, action, step=step)
    append_event(Path(state).parent / "05-operation" / "011-observability-log.jsonl", event)
    return event


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
    _replace_metadata(req, {
        "{{initiative_proposal}}": f"iniciativa-001-{_slug(title)}",
        "{{demand_proposal}}": f"001-{_slug(title)}",
        "{{scope_proposal}}": title,
    })
    stamp = framework_stamp(framework_root)
    write_state_fields(state, {
        "id": draft_id, "title": title, "lane": "pending", "sigla": _derive_sigla(hub),
        "framework version": stamp["version"], "framework ref": stamp["ref"],
        "framework commit": stamp["commit"],
    }, section="Demand")
    write_state_fields(state, {
        "current phase": "Inception", "current step": "framing",
        "next step": "preencher 003-requirements.md", "status": "draft",
    }, section="Progress")
    return CommandResult("demand draft", changed=True, message=f"Rascunho criado: {target}", data={"draft": str(target), "requirements": str(req)}, next_steps=[f"Preencha {req} e informe `pronto`."])


def _replace_metadata(path, values):
    text = path.read_text(encoding="utf-8-sig")
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


def _resolve_lane(values, req, confirmed_by, dry_run):
    """Derive the lane from the risk checklist; the human confirms overrides.

    Returns (lane_data dict, blocked CommandResult or None).
    """
    risk_scores, complexity_scores = {}, {}
    for field, key in RISK_FIELDS.items():
        score = _score(values.get(field, ""))
        if score is None:
            return None, CommandResult("demand start", "blocked",
                                       message=f"Criterio de risco invalido em `{field}`: responda 0, 1 ou 2.")
        risk_scores[key] = score
    for field, key in CX_FIELDS.items():
        score = _score(values.get(field, ""))
        if score is None:
            return None, CommandResult("demand start", "blocked",
                                       message=f"Criterio de complexidade invalido em `{field}`: responda 0, 1 ou 2.")
        complexity_scores[key] = score
    overrides_answer = values.get("hard_overrides", "").lower()
    proposal = propose(risk_scores, complexity_scores,
                       architectural_change="arquitetural" in overrides_answer,
                       multi_squad="multi-squad" in overrides_answer or "multi squad" in overrides_answer)
    summary = (f"proposta {proposal['lane']} (risco {proposal['risk']}/10, "
               f"complexidade {proposal['complexity']}/10"
               + ("; overrides: " + "; ".join(proposal["overrides"]) if proposal["overrides"] else "") + ")")
    confirm = values.get("lane_confirm", "").strip()
    if proposal["lane"] == "FAST" and not proposal["overrides"] and not confirm:
        return {"lane": "FAST", "proposal": proposal, "summary": summary,
                "confirmed_by": "auto (FAST sem overrides)",
                "justification": "proposta aceita automaticamente"}, None
    if not confirm:
        if not dry_run:
            append_question(req,
                            f"Confirma a lane proposta? {summary}. Overrides exigem justificativa na [Resposta].",
                            "lane_confirm",
                            [f"Confirmar a proposta {proposal['lane']}",
                             "FAST - justifique na resposta",
                             "Standard - justifique na resposta",
                             "SAFE - justifique na resposta"], "A")
        return None, CommandResult("demand start", "blocked", changed=not dry_run,
                                   message=f"Lane {summary}. Confirme em {req} (campo lane_confirm).")
    lowered = confirm.lower()
    if lowered.startswith("confirmar"):
        chosen = proposal["lane"]
    else:
        chosen = next((lane for lane in LANES if lowered.startswith(lane.lower())), None)
    if chosen is None:
        return None, CommandResult("demand start", "blocked",
                                   message="Resposta de lane_confirm invalida: confirme a proposta ou responda FAST/Standard/SAFE com justificativa.")
    justification = confirm
    if chosen != proposal["lane"] and len(confirm.split()) < 3:
        return None, CommandResult("demand start", "blocked",
                                   message=f"Override de lane ({proposal['lane']} -> {chosen}) requer justificativa: responda `{chosen} - <motivo>` em lane_confirm.")
    return {"lane": chosen, "proposal": proposal, "summary": summary,
            "confirmed_by": confirmed_by, "justification": justification}, None


def start(draft_path, framework_root, confirmed_by="", dry_run=False):
    draft_path = Path(draft_path).resolve()
    req = draft_path / "01-inception" / "003-requirements.md"
    if not req.exists():
        return CommandResult("demand start", "blocked", message=f"Requirements do rascunho nao encontrado: {req}")
    values, _required, missing = parse(req)
    if missing:
        return CommandResult("demand start", "blocked", message=f"Requirements incompleto; faltam: {', '.join(missing)}", next_steps=[f"Preencha {req}"])
    if not confirmed_by:
        named = run_git(framework_root, "config", "user.name").stdout.strip()
        confirmed_by = named or "humano responsavel"
    lane_data, blocked = _resolve_lane(values, req, confirmed_by, dry_run)
    if blocked is not None:
        return blocked
    lane = lane_data["lane"]
    initiative, demand_id = values.get("initiative_id", ""), values.get("demand_id", "")
    if not ID.match(initiative) or not ID.match(demand_id):
        return CommandResult("demand start", "blocked", message="IDs de iniciativa ou demanda invalidos.")
    hub = draft_path.parent.parent
    target = hub / initiative / demand_id
    if target.exists():
        return CommandResult("demand start", "blocked", message=f"Demanda ja existe: {target}")
    app_value = values.get("target_app", "").strip()
    app_repo = None
    if app_value.lower() not in NO_APP:
        app_repo = Path(app_value).expanduser()
        if not app_repo.is_absolute():
            app_repo = (hub.parent / app_repo).resolve()
        if not app_repo.exists() or not app_repo.is_dir():
            return CommandResult("demand start", "blocked",
                                 message=f"Caminho App nao encontrado: {app_repo}. Responda `target_app` com um caminho existente ou `nenhum`.")
    app_target = app_repo / ".alfred-docs-app" / initiative / demand_id if app_repo is not None else None
    if app_target is not None and app_target.exists():
        return CommandResult("demand start", "blocked",
                             message=f"Demanda App ja existe e nao sera sobrescrita: {app_target}")
    if dry_run:
        return CommandResult("demand start", message=f"Demanda seria criada em {target}", data={"demand": str(target), "lane": lane})

    templates = Path(framework_root) / "templates" / "hub"
    staging = hub / initiative / f".stage-{demand_id}"
    app_staging = app_repo / ".alfred-docs-app" / initiative / f".stage-{demand_id}" if app_repo is not None else None
    try:
        _build_hub_demand(staging, draft_path, templates, framework_root, values, lane_data,
                          initiative, demand_id, hub, app_repo, confirmed_by)
        if app_staging is not None:
            _build_app_demand(app_staging, Path(framework_root) / "templates" / "app",
                              staging / "001-state.md", framework_root, lane)
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging, target)
        if app_staging is not None:
            try:
                app_target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(app_staging, app_target)
            except OSError as error:
                shutil.rmtree(target, ignore_errors=True)
                return CommandResult("demand start", "error",
                                     message=f"Falha ao criar artefatos do App; demanda revertida e rascunho preservado: {error}")
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        if app_staging is not None:
            shutil.rmtree(app_staging, ignore_errors=True)

    state = target / "001-state.md"
    now = _now()
    initiative_file = hub / initiative / "001-initiative.md"
    if not initiative_file.exists():
        _copy(templates, "initiative.md", initiative_file)
        _replace_metadata(initiative_file, {"`iniciativa-<sequencia>-<iniciativa>`": f"`{initiative}`"})
    relative_state = f"{initiative}/{demand_id}/001-state.md"
    _add_table_row(hub / "001-index.md", "Open demands",
                   f"| {demand_id} | {initiative} | {lane} | Inception | active | {relative_state} | {now} | completar Inception |")
    _add_table_row(initiative_file, "Demands", f"- [{demand_id}]({demand_id}/001-state.md) - active")
    shutil.rmtree(draft_path)
    next_steps = []
    if values.get("demand_type", "").lower().startswith("operational") and "urgente" in values.get("urgency", "").lower():
        next_steps.append("Demanda operacional urgente: siga o caminho Execution-first de rules/demand-types/operational.md (estabilizar primeiro, post-mortem obrigatorio).")
    return CommandResult("demand start", changed=True, message=f"Demanda iniciada: {target}",
                         data={"demand": str(target), "state": str(state), "lane": lane,
                               "risk": lane_data["proposal"]["risk"], "complexity": lane_data["proposal"]["complexity"]},
                         next_steps=next_steps)


def _build_hub_demand(staging, draft_path, templates, framework_root, values, lane_data,
                      initiative, demand_id, hub, app_repo, confirmed_by):
    lane = lane_data["lane"]
    proposal = lane_data["proposal"]
    if staging.exists():
        shutil.rmtree(staging)
    for folder in ("01-inception", "02-design", "03-execution", "04-validate", "05-operation"):
        (staging / folder).mkdir(parents=True)
    shutil.copyfile(draft_path / "001-state.md", staging / "001-state.md")
    shutil.copyfile(draft_path / "01-inception" / "003-requirements.md",
                    staging / "01-inception" / "003-requirements.md")
    for template, relative in (
        ("problem.md", "01-inception/002-problem.md"), ("risk.md", "01-inception/004-risk.md"),
        ("audit.md", "05-operation/007-audit.md"), ("metrics.md", "05-operation/008-metrics.md"),
    ):
        _copy(templates, template, staging / relative)
    if lane != "FAST":
        for template, relative in (
            ("tech-inception.md", "01-inception/005-tech-inception.md"),
            ("decisions.md", "02-design/006-decisions.md"),
            ("execution-plan.md", "03-execution/012-execution-plan.md"),
            ("validation-evidence.md", "04-validate/013-validation-evidence.md"),
        ):
            _copy(templates, template, staging / relative)
    risk_file = staging / "01-inception" / "004-risk.md"
    with risk_file.open("a", encoding="utf-8") as handle:
        handle.write("\n## Classificacao\n")
        handle.write(f"- score de risco: {proposal['risk']}/10\n")
        handle.write(f"- score de complexidade: {proposal['complexity']}/10\n")
        handle.write(f"- modo proposto: {proposal['lane']}\n")
        handle.write(f"- modo confirmado: {lane} ({lane_data['confirmed_by']})\n")
        handle.write("\n## Overrides\n")
        for item in (proposal["overrides"] or ["nenhum"]):
            handle.write(f"- {item}\n")
    stamp = framework_stamp(framework_root)
    state = staging / "001-state.md"
    now = _now()
    write_state_fields(state, {
        "id": demand_id, "sigla": _derive_sigla(hub, app_repo), "initiative id": initiative,
        "stream/type": values.get("demand_type", ""), "lane": lane,
        "framework version": stamp["version"], "framework ref": stamp["ref"],
        "framework commit": stamp["commit"], "observability schema": OBSERVABILITY_SCHEMA,
        "urgency": values.get("urgency", ""), "owner": values.get("owner", ""),
    }, section="Demand")
    write_state_fields(state, {
        "framing status": "confirmed", "framing confirmed by": confirmed_by,
        "framing confirmed at": now, "target app/source": values.get("target_app", ""),
        "artifact set": values.get("artifact_set", ""),
        "risk score": f"{proposal['risk']}/10", "complexity score": f"{proposal['complexity']}/10",
        "lane proposed": proposal["lane"], "lane justification": lane_data["justification"],
        "lane confirmed by": lane_data["confirmed_by"], "lane confirmed at": now,
    }, section="Opening Framing")
    write_state_fields(state, {
        "current phase": "Inception", "current step": "problema e risco",
        "next step": "completar Inception", "status": "active",
    }, section="Progress")
    fields = read_state_fields(state)
    event = lifecycle_event(fields, stamp, "demand_started", "demand_started",
                            artifacts=["001-state.md", "01-inception/003-requirements.md"])
    append_event(staging / "05-operation" / "011-observability-log.jsonl", event)
    return event


def _build_app_demand(app_staging, app_templates, hub_state, framework_root, lane):
    if app_staging.exists():
        shutil.rmtree(app_staging)
    for template, relative in (
        ("index.md", "001-index.md"), ("reverse-eng.md", "01-inception/002-reverse-eng.md"),
        ("audit.md", "05-operation/005-audit.md"), ("metrics.md", "05-operation/006-metrics.md"),
    ):
        _copy(app_templates, template, app_staging / relative)
    if lane != "FAST":
        _copy(app_templates, "spec.md", app_staging / "02-design" / "003-spec.md")
    fields = read_state_fields(hub_state)
    event = lifecycle_event(fields, framework_stamp(framework_root), "demand_started",
                            "demand_started", artifacts=["001-index.md"])
    (app_staging / "05-operation").mkdir(parents=True, exist_ok=True)
    append_event(app_staging / "05-operation" / "008-observability-log.jsonl", event)
    return event


def demand_status(state_path):
    state = Path(state_path)
    if not state.exists():
        return CommandResult("demand status", "blocked", message=f"State nao encontrado: {state}")
    fields = read_state_fields(state)
    return CommandResult("demand status", message=f"{fields.get('id', '?')} | {fields.get('lane', '?')} | {fields.get('current phase', '?')} | {fields.get('status', '?')}", data=fields)


def _tick_phase(state, phase):
    text = state.read_text(encoding="utf-8-sig")
    ticked = re.sub(rf"- \[ \] {re.escape(phase)}", f"- [x] {phase}", text)
    state.write_text(ticked, encoding="utf-8")
    return ticked != text


def _phase_completed(state, phase):
    return not re.search(rf"- \[ \] {re.escape(phase)}", state.read_text(encoding="utf-8-sig"))


def _transition_gate(state, fields, new_phase, force_reason):
    """Minimal lifecycle gate: sequential advance, forced jumps are audited."""
    current = fields.get("current phase", "") or "Inception"
    if current not in PHASES or new_phase == current:
        return None
    jump = PHASES.index(new_phase) - PHASES.index(current)
    if force_reason:
        return None
    if jump != 1:
        direction = "pular fases" if jump > 1 else "retroceder fase"
        return CommandResult("checkpoint", "blocked",
                             message=f"Transicao {current} -> {new_phase} nao e sequencial; para {direction} use --force com justificativa (auditada).")
    if not _phase_completed(state, current):
        return CommandResult("checkpoint", "blocked",
                             message=f"Fase {current} ainda tem checkbox aberto no Checklist; use `checkpoint --complete {current}` (com o humano de acordo) antes de avancar para {new_phase}.")
    if new_phase == "Execution" and fields.get("lane", "") in ("Standard", "SAFE"):
        _output, errors, _warnings, failed = run_sdd_gate(state.parent, "", strict=False)
        if failed:
            # run_sdd_gate yields (severity, code, message) triples.
            details = "; ".join(message for _severity, _code, message in errors[:3])
            return CommandResult("checkpoint", "blocked",
                                 message=f"SDD gate bloqueou a entrada em Execution ({fields.get('lane')}): {details}. Complete spec/decisions ou use --force com justificativa.")
    return None


def checkpoint(state_path, framework_root, updates, question="", field_name="", options=None,
               recommended="", multiple=False, complete="", force_reason="", dry_run=False):
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
    if complete and complete not in PHASES:
        return CommandResult("checkpoint", "blocked", message=f"Fase invalida em --complete: {complete}")
    phase = updates.get("current phase")
    if phase and phase not in PHASES:
        return CommandResult("checkpoint", "blocked", message=f"Fase invalida: {phase}")
    if dry_run:
        return CommandResult("checkpoint", message="Checkpoint seria atualizado.", data=updates)
    if complete:
        _tick_phase(state, complete)
    if phase:
        gate = _transition_gate(state, read_state_fields(state), phase, force_reason)
        if gate is not None:
            return gate
    write_state_fields(state, updates, section="Progress")
    fields = read_state_fields(state)
    now = _now()
    audit = state.parent / "05-operation" / "007-audit.md"
    if audit.exists():
        detail = "Estado atualizado"
        if force_reason:
            detail = f"Transicao forcada: {force_reason}"
        elif complete:
            detail = f"Fase {complete} concluida"
        with audit.open("a", encoding="utf-8") as handle:
            handle.write(f"| {now} | Alfred CLI | {fields.get('current phase', '')} | Checkpoint | {fields.get('model', 'n/a')} | {detail} | humano responsavel |\n")
    _emit(state, framework_root, "checkpoint", "checkpoint_recorded",
          step=fields.get("current step", ""))
    warnings = []
    data = dict(fields)
    try:
        data["toolbar"] = render_toolbar(state, framework_root=framework_root, profile="text")
    except (OSError, ValueError) as error:
        warnings.append(f"Toolbar indisponivel: {error}")
    return CommandResult("checkpoint", changed=True, message=f"Checkpoint registrado para {fields.get('id', '')}.", data=data, warnings=warnings)


def _acceptance_kind(raw):
    lowered = raw.lower()
    if "aceitar" in lowered or lowered.startswith("accept"):
        return "accepted"
    if "rejeitar" in lowered or lowered.startswith("reject"):
        return "rejected"
    if "ajust" in lowered or "solicitar" in lowered:
        return "changes_requested"
    return "unknown"


def _missing_close_evidence(values, lane):
    required = []
    if lane in ("Standard", "SAFE"):
        required += CLOSE_EVIDENCE["Standard"]
    if lane == "SAFE":
        required += CLOSE_EVIDENCE["SAFE"]
    return [(field, question) for field, question in required if not values.get(field, "").strip()]


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
                             message=f"Aceite final deve ser respondido em {req}.",
                             next_steps=[f"Responda o campo final_acceptance em {req}."]), ""
    kind = _acceptance_kind(acceptance)
    if kind == "rejected":
        if not dry_run:
            write_state_fields(state, {"status": "rejeitada"}, section="Progress")
        return CommandResult("demand close", "blocked", changed=not dry_run,
                             message="Aceite final = Rejeitar a entrega: a demanda NAO sera encerrada como concluida (status: rejeitada).",
                             next_steps=["O humano decide: reabrir com ajustes (responda `Solicitar ajustes`), cancelar, ou substituir a demanda."]), ""
    if kind == "changes_requested":
        if not dry_run:
            write_state_fields(state, {"status": "active"}, section="Progress")
        return CommandResult("demand close", "blocked", changed=not dry_run,
                             message="Aceite final = Solicitar ajustes: a demanda permanece aberta para replanejamento.",
                             next_steps=["Replaneje os ajustes (Execution/Validate) e responda o aceite novamente ao concluir."]), ""
    if kind != "accepted":
        return CommandResult("demand close", "blocked",
                             message="Resposta de aceite final nao reconhecida; responda Aceitar a entrega, Rejeitar a entrega ou Solicitar ajustes.",
                             next_steps=[f"Ajuste o campo final_acceptance em {req}."]), ""
    fields = read_state_fields(state)
    lane = fields.get("lane", "")
    missing_evidence = _missing_close_evidence(values, lane)
    if missing_evidence:
        if req.exists() and not dry_run:
            for field, question in missing_evidence:
                append_question(req, question, field)
        names = ", ".join(field for field, _ in missing_evidence)
        return CommandResult("demand close", "blocked", changed=not dry_run,
                             message=f"Lane {lane} exige evidencias de fechamento; faltam: {names}.",
                             next_steps=[f"Responda as evidencias em {req}."]), ""
    text = state.read_text(encoding="utf-8-sig")
    incomplete = [phase for phase in PHASES[:-1] if re.search(rf"- \[ \] {re.escape(phase)}", text)]
    if incomplete:
        return CommandResult("demand close", "blocked",
                             message="Fases ainda abertas: " + ", ".join(incomplete),
                             next_steps=["Para cada fase concluida com o humano, rode `alfred checkpoint --state <state> --complete <fase>`."]), ""
    template = Path(framework_root) / "templates" / "hub" / "summary.md"
    if not summary.exists():
        if not dry_run:
            _copy(template.parent, template.name, summary)
        return CommandResult("demand close", "blocked", changed=not dry_run,
                             message=f"Resumo criado e precisa ser preenchido: {summary}",
                             next_steps=[f"Preencha {summary} em pt-BR e rode o close novamente."]), ""
    if summary.read_text(encoding="utf-8-sig").strip() == template.read_text(encoding="utf-8-sig").strip():
        return CommandResult("demand close", "blocked", message=f"Resumo ainda esta vazio: {summary}",
                             next_steps=[f"Preencha {summary} em pt-BR e rode o close novamente."]), ""
    if not dry_run:
        _record_acceptance_audit(state, acceptance, values)
    return CommandResult("demand close", message="Fechamento pronto para validacao estrita."), "accepted"


def _record_acceptance_audit(state, acceptance, values):
    audit = state.parent / "05-operation" / "007-audit.md"
    if not audit.exists():
        return
    text = audit.read_text(encoding="utf-8-sig")
    if "Aceite final registrado" in text:
        return
    evidence = "; ".join(f"{field}={values[field]}" for field, _q in
                         CLOSE_EVIDENCE["Standard"] + CLOSE_EVIDENCE["SAFE"] if values.get(field))
    with audit.open("a", encoding="utf-8") as handle:
        handle.write(f"| {_now()} | humano responsavel | Operation | Aceite final registrado | n/a | {acceptance}"
                     + (f" ({evidence})" if evidence else "") + " | humano responsavel |\n")


def close(state_path, framework_root, acceptance, dry_run=False):
    state = Path(state_path).resolve()
    if dry_run:
        return CommandResult("demand close", message="Demanda seria encerrada apos validacao estrita.")
    _tick_phase(state, "Operation")
    write_state_fields(state, {"current phase": "Operation", "current step": "fechamento",
                               "next step": "demanda concluida", "status": "concluida"}, section="Progress")
    fields = read_state_fields(state)
    metrics = state.parent / "05-operation" / "008-metrics.md"
    if metrics.exists():
        mtext = metrics.read_text(encoding="utf-8-sig")
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
