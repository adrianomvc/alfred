#!/usr/bin/env python3
"""Alfred notification adapter: an MCP server that sends e-mail (Python stdlib only).

Implements the `notification` connector contract (``connectors/notification-email.md``)
as a Model Context Protocol server over stdio (newline-delimited JSON-RPC 2.0).
No third-party dependencies — transport is smtplib; dry-run needs no network.

Owner decision (2.0.0 plan): the notification channel is MCP + Python. This adapter
is intentionally single-runtime; degradation (D3) is the manual handoff already
defined in the connector contract.

Adapter states (``connectors/connectors.md``):
- ``dry-run`` (default): composes the RFC-822 message and writes it to an outbox
  folder instead of sending. Safe by default.
- ``active``: sends through SMTP (STARTTLS). Requires explicit configuration.
- ``disabled``: refuses to operate.

Configuration — where the destination is REGISTERED (durable authorization, D44):
1. **Config file** (recommended; survives framework updates): JSON at
   ``~/.alfred-email.json`` (or the path in ``ALFRED_EMAIL_CONFIG``)::

       {"mode": "dry-run", "default_to": "voce@dominio.com",
        "telemetry_to": "central-de-metricas@organizacao.com",
        "allowlist": ["voce@dominio.com"],
        "smtp": {"host": "", "port": 587, "user": "", "sender": ""}}

   ``telemetry_to`` is the ORG destination that receives every runner's
   observability batches (``send_telemetry``) — provisional transport until the
   telemetry API exists (D45). It is auto-added to the allowlist.

   Secret values are never accepted from this file.

2. **Environment variables** (override the file):
   ``ALFRED_EMAIL_MODE``       dry-run | active | disabled   (default: dry-run)
   ``ALFRED_EMAIL_DEFAULT_TO`` default destination
   ``ALFRED_EMAIL_ALLOWLIST``  comma-separated allowed recipients (default: DEFAULT_TO)
   ``ALFRED_EMAIL_OUTBOX``     dry-run outbox dir (default: ./.alfred-email-outbox)
   ``ALFRED_EMAIL_AUDIT``      audit JSONL path (default: <outbox>/audit-log.jsonl)
   ``SMTP_HOST`` ``SMTP_PORT`` ``SMTP_USER`` ``SMTP_PASS`` ``SMTP_FROM``  (active mode)
3. At adoption, the sigla records destination + triggers in its HUB ``knowledge``
   (see ``knowledge/notification.md``); this file/env is the machine-level mirror.

Register in Claude Code:  ``claude mcp add alfred-email -- python scripts/adapters/mcp-email-server.py``

Guardrails (injection/authorization):
- recipients outside the allowlist are refused — new destination requires a human
  updating the configuration, never the model talking the adapter into it;
- the subject is always prefixed ``[Alfred-Framework]``;
- every attempt (sent, dry-run, or refused) is appended to the audit JSONL with
  the connector's audit fields.
"""

import getpass
import hashlib
import json
import os
import re
import smtplib
import socket
import sys
import time
from email.message import EmailMessage
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_ROOT))
from shared.email_tools import TOOLS  # noqa: E402

SERVER_NAME = "alfred-email"
SERVER_VERSION = "2.0.0"
SUBJECT_PREFIX = "[Alfred-Framework]"
ATTACHMENT_EXTENSIONS = {".md", ".jsonl", ".json", ".txt", ".csv", ".log"}
ATTACHMENT_MAX_BYTES = 5 * 1024 * 1024
# Telemetry payload allowlist: only schema fields leave the machine (D45).
TELEMETRY_FIELDS = {
    "schema_version", "alfred", "ts", "event_id", "trace_id", "session_id",
    "interaction_id", "request_id", "parent_event_id", "sequence",
    "interaction_sequence", "request_sequence", "event_type", "event_scope",
    "initiative_id", "demand_id", "phase", "lane", "agent", "actor_type",
    "actor_id", "action", "status", "step", "model", "duration_ms",
    "tokens_input", "tokens_output", "tokens_cache_creation", "tokens_cache_read",
    "total_tokens", "cost_usd", "retry_count", "token_confidence",
    "interaction_confidence", "correlation_method", "usage", "context",
    "outcome", "validation", "artifact", "artifacts_used", "request_count",
    "tool_call_count", "tool_failure_count", "from_commit", "to_commit",
}
SECRET_PATTERNS = re.compile(
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|(?i:(password|secret|api[_-]?key|token)\s*[=:]\s*\S)")
# Absolute paths must be reduced to a bare filename before telemetry leaves the
# machine. os.path.isabs() answers for the *running* platform only — on Linux it
# does not recognise "C:/x/y", so a Windows path forwarded through a Linux host
# would ship the whole path. Telemetry sanitization must not depend on where it
# runs, so both conventions are matched explicitly: POSIX root, drive letter, UNC.
ABSOLUTE_PATH = re.compile(r"^(?:[/\\]|[A-Za-z]:[/\\])")


def load_config_file():
    path = Path(os.environ.get("ALFRED_EMAIL_CONFIG", str(Path.home() / ".alfred-email.json")))
    if not path.is_file():
        return {}, None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), str(path)
    except (json.JSONDecodeError, OSError):
        return {}, str(path) + " (unreadable — fix or remove it)"


def config():
    file_cfg, config_path = load_config_file()
    file_smtp = file_cfg.get("smtp") or {}
    mode = (os.environ.get("ALFRED_EMAIL_MODE") or file_cfg.get("mode") or "dry-run").strip().lower()
    default_to = (os.environ.get("ALFRED_EMAIL_DEFAULT_TO") or file_cfg.get("default_to") or "").strip()
    telemetry_to = (os.environ.get("ALFRED_TELEMETRY_TO") or file_cfg.get("telemetry_to") or "").strip()
    allow_raw = os.environ.get("ALFRED_EMAIL_ALLOWLIST")
    if allow_raw is not None:
        allowlist = [a.strip().lower() for a in allow_raw.split(",") if a.strip()]
    elif file_cfg.get("allowlist"):
        allowlist = [str(a).strip().lower() for a in file_cfg["allowlist"] if str(a).strip()]
    else:
        allowlist = [default_to.lower()] if default_to else []
    if telemetry_to and telemetry_to.lower() not in allowlist:
        allowlist.append(telemetry_to.lower())  # org telemetry destination is pre-authorized by config
    outbox = Path(os.environ.get("ALFRED_EMAIL_OUTBOX") or file_cfg.get("outbox") or ".alfred-email-outbox")
    audit = Path(os.environ.get("ALFRED_EMAIL_AUDIT") or file_cfg.get("audit") or str(outbox / "audit-log.jsonl"))
    attach_raw = os.environ.get("ALFRED_EMAIL_ATTACH_ROOTS")
    if attach_raw is not None:
        attach_roots = [a.strip() for a in attach_raw.split(os.pathsep) if a.strip()]
    else:
        attach_roots = [str(a) for a in (file_cfg.get("allowed_attachment_roots") or [])]
    attach_roots = [Path(a).expanduser().resolve() for a in attach_roots] or [Path.cwd().resolve(),
                                                                              outbox.resolve()]
    sender_alias = (os.environ.get("ALFRED_EMAIL_SENDER_ALIAS") or file_cfg.get("sender_alias") or "").strip()
    return {
        "mode": mode, "default_to": default_to, "telemetry_to": telemetry_to, "allowlist": allowlist,
        "outbox": outbox, "audit": audit, "config_path": config_path,
        "attach_roots": attach_roots, "sender_alias": sender_alias,
        "secret_in_file": bool(file_smtp.get("password")),
        "smtp": {
            "host": os.environ.get("SMTP_HOST") or file_smtp.get("host", ""),
            "port": int(os.environ.get("SMTP_PORT") or file_smtp.get("port") or 587),
            "user": os.environ.get("SMTP_USER") or file_smtp.get("user", ""),
            "password": os.environ.get("SMTP_PASS", ""),
            "sender": os.environ.get("SMTP_FROM") or file_smtp.get("sender", "")
                      or os.environ.get("SMTP_USER") or file_smtp.get("user", ""),
        },
    }


def audit_event(cfg, destination, subject, attachments, result, failure_reason=None, trigger=None):
    event = {
        "schema_version": "alfred.observability.v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "event_type": "notification_attempted",
        "connector": "notification-email-mcp",
        "send_mode": cfg["mode"],
        "destination": destination,
        "trigger": trigger,
        "subject": subject,
        "attachments": attachments,
        "approval_reference": "configured destination + trigger (durable authorization)",
        "result": result,
        "failure_reason": failure_reason,
    }
    try:
        cfg["audit"].parent.mkdir(parents=True, exist_ok=True)
        with open(cfg["audit"], "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError as exc:
        # Every external send must be auditable; active mode aborts when the
        # audit trail cannot be persisted (dry-run only reports the failure).
        return None, str(exc)
    return event, None


def check_attachments(cfg, attachments):
    """Attachments are demand/HUB artifacts only: allowed root + type + size."""
    problems = []
    for raw in attachments:
        path = Path(raw).expanduser()
        try:
            resolved = path.resolve()
        except OSError:
            problems.append(f"{raw}: caminho invalido")
            continue
        if not resolved.is_file():
            problems.append(f"{raw}: nao encontrado")
            continue
        if not any(resolved == root or root in resolved.parents for root in cfg["attach_roots"]):
            problems.append(f"{raw}: fora das raizes permitidas (allowed_attachment_roots)")
            continue
        if resolved.suffix.lower() not in ATTACHMENT_EXTENSIONS:
            problems.append(f"{raw}: extensao nao permitida ({resolved.suffix or 'sem extensao'})")
            continue
        if resolved.stat().st_size > ATTACHMENT_MAX_BYTES:
            problems.append(f"{raw}: acima do limite de {ATTACHMENT_MAX_BYTES // (1024 * 1024)} MB")
    return problems


def build_message(sender, destination, subject, body, attachments):
    msg = EmailMessage()
    msg["From"] = sender or "alfred@localhost"
    msg["To"] = destination
    msg["Subject"] = subject
    msg.set_content(body)
    for path in attachments:
        data = Path(path).read_bytes()
        msg.add_attachment(data, maintype="application", subtype="octet-stream",
                           filename=Path(path).name)
    return msg


def tool_send_email(cfg, args):
    subject = str(args.get("subject", "")).strip()
    body = str(args.get("body", "")).strip()
    destination = str(args.get("to", "") or cfg["default_to"]).strip()
    trigger = str(args.get("trigger", "")).strip() or None
    attachments = [str(a) for a in (args.get("attachments") or [])]

    if not subject or not body:
        return err("Missing required argument. Provide `subject` and `body`; "
                   "optional: `to`, `trigger`, `attachments` (file paths).")
    if cfg["mode"] == "disabled":
        return err("Adapter is disabled (ALFRED_EMAIL_MODE=disabled). "
                   "Prepare the content and remind the human to send manually (degradation).")
    if cfg["mode"] == "active" and cfg["secret_in_file"]:
        return err("Remove smtp.password from the JSON config. Store SMTP_PASS in the "
                   "Devin Secrets UI, environment, or an approved secret store.")
    if not destination:
        return err("No destination: pass `to` or set ALFRED_EMAIL_DEFAULT_TO. "
                   "The destination must come from configuration, not from guessed values.")
    if not subject.startswith(SUBJECT_PREFIX):
        subject = f"{SUBJECT_PREFIX} {subject}"
    if destination.lower() not in cfg["allowlist"]:
        audit_event(cfg, destination, subject, attachments, "refused",
                    "destination not in allowlist", trigger)
        return err(f"Destination '{destination}' is not in the allowlist. "
                   "A new destination requires a HUMAN to update ALFRED_EMAIL_ALLOWLIST "
                   "(durable authorization) — do not retry with other addresses.")
    problems = check_attachments(cfg, attachments)
    if problems:
        audit_event(cfg, destination, subject, attachments, "refused",
                    "attachment policy: " + "; ".join(problems), trigger)
        return err("Attachment(s) refused: " + "; ".join(problems) +
                   ". Attach demand/HUB artifacts under the allowed roots only "
                   "(config `allowed_attachment_roots`).")

    if cfg["mode"] == "dry-run":
        cfg["outbox"].mkdir(parents=True, exist_ok=True)
        msg = build_message(cfg["smtp"]["sender"], destination, subject, body, attachments)
        out = cfg["outbox"] / (time.strftime("%Y%m%dT%H%M%S") + "-" +
                               "".join(c if c.isalnum() else "-" for c in subject[:40]) + ".eml")
        out.write_bytes(bytes(msg))
        _event, audit_error = audit_event(cfg, destination, subject, attachments, "dry-run", None, trigger)
        note = f" | AVISO: audit nao gravado ({audit_error})" if audit_error else ""
        return ok(f"DRY-RUN: e-mail composed, not sent. Written to {out} | to={destination} | "
                  f"subject={subject} | attachments={len(attachments)}.{note} "
                  "Set ALFRED_EMAIL_MODE=active (+ SMTP_*) to really send.")

    smtp = cfg["smtp"]
    if not smtp["host"] or not smtp["sender"]:
        audit_event(cfg, destination, subject, attachments, "failed",
                    "active mode without SMTP configuration", trigger)
        return err("Active mode but SMTP is not configured. Set SMTP_HOST, SMTP_PORT, "
                   "SMTP_USER, SMTP_PASS, SMTP_FROM — or use ALFRED_EMAIL_MODE=dry-run.")
    _event, audit_error = audit_event(cfg, destination, subject, attachments, "sending", None, trigger)
    if audit_error:
        return err(f"Send aborted: the audit trail could not be persisted ({audit_error}). "
                   "Every external send must be audited; fix the audit path "
                   f"({cfg['audit']}) or use dry-run.")
    try:
        msg = build_message(smtp["sender"], destination, subject, body, attachments)
        with smtplib.SMTP(smtp["host"], smtp["port"], timeout=30) as client:
            client.starttls()
            if smtp["user"]:
                client.login(smtp["user"], smtp["password"])
            client.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        audit_event(cfg, destination, subject, attachments, "failed", str(exc), trigger)
        return err(f"SMTP send failed: {exc}. Check SMTP_* settings/network, or fall back "
                   "to dry-run and remind the human to send manually.")
    audit_event(cfg, destination, subject, attachments, "sent", None, trigger)
    return ok(f"SENT to {destination} | subject={subject} | attachments={len(attachments)}. "
              f"Audit appended to {cfg['audit']}.")


REPORT_FILES = [
    ("05-operation/008-metrics.md", "metrics"),
    ("05-operation/007-audit.md", "audit"),
    ("05-operation/009-summary.md", "summary"),
    ("05-operation/011-observability-log.jsonl", "observability"),
]


def state_field(lines, names):
    for name in names:
        for line in lines:
            stripped = line.strip()
            if stripped.lower().startswith(f"- {name}:"):
                return stripped.split(":", 1)[1].strip().strip("`")
    return ""


def tool_send_demand_report(cfg, args):
    demand_path = Path(str(args.get("demand_path", "")).strip())
    state = demand_path / "001-state.md"
    if not state.is_file():
        return err(f"`001-state.md` not found under '{demand_path}'. Pass the HUB demand "
                   "folder, e.g. alfred-docs-hub/<id-iniciativa>/<id-demanda>.")
    lines = state.read_text(encoding="utf-8-sig").splitlines()
    demand_id = state_field(lines, ["id"]) or demand_path.name
    sigla = state_field(lines, ["sigla"]) or "SIGLA"
    title = state_field(lines, ["titulo", "title"]) or demand_id
    lane = state_field(lines, ["lane", "modo"]) or "?"
    phase = state_field(lines, ["current phase", "fase atual"]) or "?"
    status = state_field(lines, ["status"]) or "?"
    version = state_field(lines, ["framework version"]) or "?"

    attachments, missing = [], []
    for rel, label in REPORT_FILES:
        path = demand_path / rel
        (attachments if path.is_file() else missing).append(str(path) if path.is_file() else label)
    if not attachments:
        return err("No report artifact found (metrics/audit/summary/observability). "
                   "Generate them before sending the report.")

    subject = f"[{sigla}][{demand_id}] Relatorio — {title}"
    body = (f"Relatorio da demanda {demand_id} ({sigla}).\n"
            f"- lane: {lane} · fase: {phase} · status: {status} · Alfred: {version}\n"
            f"- anexos: metricas, audit, summary e observability JSONL (quando existentes)\n"
            + (f"- ausentes nesta demanda: {', '.join(missing)}\n" if missing else "")
            + f"- state: {state}\n"
            "Corpo curto por padrao (D44): o detalhe vai anexado, nao colado.")
    return tool_send_email(cfg, {
        "subject": subject, "body": body, "to": args.get("to", ""),
        "trigger": args.get("trigger", "demand_report"), "attachments": attachments,
    })


def telemetry_sender(cfg):
    """Configured alias, or a stable anonymous hash — never raw user@hostname."""
    if cfg["sender_alias"]:
        return cfg["sender_alias"]
    digest = hashlib.sha256(f"{getpass.getuser()}@{socket.gethostname()}".encode("utf-8")).hexdigest()
    return f"runner-{digest[:12]}"


def sanitize_telemetry_event(event):
    """Field-allowlist sanitization: schema fields only, relative paths only.

    Returns the sanitized event, or ``None`` when the event must be skipped
    (secret-pattern match).
    """
    if SECRET_PATTERNS.search(json.dumps(event, ensure_ascii=False)):
        return None
    clean = {key: value for key, value in event.items() if key in TELEMETRY_FIELDS}
    artifacts = clean.get("artifacts_used")
    if isinstance(artifacts, list):
        for item in artifacts:
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                item["path"] = strip_absolute_path(item["path"])
    return clean


def strip_absolute_path(value):
    """Reduce an absolute path to its filename, on any platform (see ABSOLUTE_PATH).

    Relative paths are meaningful telemetry (``01-inception/003-requirements.md``
    says which artifact was touched) and are kept as-is.
    """
    if not ABSOLUTE_PATH.match(value):
        return value
    return re.split(r"[/\\]", value)[-1]


def tool_send_telemetry(cfg, args):
    """Batch every local observability JSONL and e-mail it to the org telemetry
    destination — provisional transport (D45) until the telemetry API exists, so
    logs from everyone running Alfred can be aggregated into org metrics.
    Events are sanitized by field allowlist; unparsed lines and secret-pattern
    matches never leave the machine (only their counts do)."""
    if not cfg["telemetry_to"]:
        return err("No telemetry destination configured. Set `telemetry_to` in "
                   "~/.alfred-email.json (or ALFRED_TELEMETRY_TO) — the org address "
                   "is recorded in knowledge/notification.md.")
    root = Path(str(args.get("root_path", "") or ".")).resolve()
    logs = [p for p in sorted(root.rglob("*observability-log.jsonl"))
            if ".git" not in p.parts and ".alfred-email-outbox" not in p.parts]
    if not logs:
        return err(f"No observability JSONL found under {root}. Pass `root_path` "
                   "pointing at the HUB/app root (or one demand folder).")

    sender_id = telemetry_sender(cfg)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    cfg["outbox"].mkdir(parents=True, exist_ok=True)
    batch_path = cfg["outbox"] / f"telemetry-batch-{stamp}.jsonl"
    total = 0
    skipped = 0
    per_source = []
    with open(batch_path, "w", encoding="utf-8") as batch:
        for log in logs:
            try:
                rel = log.relative_to(root).as_posix()
            except ValueError:
                rel = log.name
            count = 0
            for raw in log.read_text(encoding="utf-8-sig").splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    skipped += 1
                    continue
                clean = sanitize_telemetry_event(event)
                if clean is None:
                    skipped += 1
                    continue
                batch.write(json.dumps({"sender": sender_id, "collected_at": stamp,
                                         "source": rel, "event": clean},
                                        ensure_ascii=False) + "\n")
                count += 1
                total += 1
            per_source.append(f"- {rel}: {count} evento(s)")

    subject = f"[telemetry][{sender_id}] {total} eventos de observabilidade"
    body = ("Lote de telemetria do Alfred (transporte provisorio por e-mail ate a API existir - D45).\n"
            f"- remetente: {sender_id}\n- fontes: {len(logs)}\n"
            + (f"- eventos retidos localmente (nao parseaveis ou padrao de segredo): {skipped}\n" if skipped else "")
            + "\n".join(per_source)
            + "\nCada linha do anexo = {sender, collected_at, source, event} (campos sanitizados por allowlist).")
    result = tool_send_email(cfg, {
        "subject": subject, "body": body, "to": cfg["telemetry_to"],
        "trigger": str(args.get("trigger", "") or "telemetry_batch"),
        "attachments": [str(batch_path)],
    })
    result["content"][0]["text"] += f" | batch kept at {batch_path}"
    return result


def tool_email_status(cfg, _args):
    smtp_ready = bool(cfg["smtp"]["host"] and cfg["smtp"]["sender"])
    return ok(json.dumps({
        "mode": cfg["mode"],
        "default_to": cfg["default_to"] or None,
        "telemetry_to": cfg["telemetry_to"] or None,
        "allowlist": cfg["allowlist"],
        "smtp_configured": smtp_ready,
        "secret_in_file": cfg["secret_in_file"],
        "outbox": str(cfg["outbox"]),
        "audit_log": str(cfg["audit"]),
        "config_file": cfg["config_path"] or "not found (create ~/.alfred-email.json or set ALFRED_EMAIL_CONFIG)",
        "adapter_state": ("disabled" if cfg["mode"] == "disabled"
                           else "active" if cfg["mode"] == "active" and smtp_ready
                           else "dry-run"),
    }, ensure_ascii=False))


def ok(text):
    return {"content": [{"type": "text", "text": text}], "isError": False}


def err(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


def handle(method, params):
    if method == "initialize":
        return {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        cfg = config()
        name = params.get("name")
        args = params.get("arguments") or {}
        if name == "send_email":
            return tool_send_email(cfg, args)
        if name == "send_demand_report":
            return tool_send_demand_report(cfg, args)
        if name == "send_telemetry":
            return tool_send_telemetry(cfg, args)
        if name == "email_status":
            return tool_email_status(cfg, args)
        return err(f"Unknown tool '{name}'. Available: send_email, send_demand_report, send_telemetry, email_status.")
    return None


def main():
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            continue
        method = message.get("method", "")
        msg_id = message.get("id")
        if method.startswith("notifications/"):
            continue
        result = handle(method, message.get("params") or {})
        if msg_id is None:
            continue
        if result is None:
            response = {"jsonrpc": "2.0", "id": msg_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}}
        else:
            response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


def cli_main(argv):
    """CLI mode — for hosts without MCP registration (or scheduled sends).

    The DEVIN CLI can register this as an MCP server (`.devin/config.local.json`),
    but any host that can run a shell command can use these subcommands instead:
        python mcp-email-server.py status
        python mcp-email-server.py send-telemetry --root <hub/app root>
        python mcp-email-server.py send-report --demand-path <hub demand folder>
    """
    import argparse
    parser = argparse.ArgumentParser(description=cli_main.__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    telemetry = sub.add_parser("send-telemetry")
    telemetry.add_argument("--root", "-Root", dest="root", default=".")
    telemetry.add_argument("--trigger", dest="trigger", default="telemetry_batch")
    report = sub.add_parser("send-report")
    report.add_argument("--demand-path", "-DemandPath", dest="demand_path", required=True)
    report.add_argument("--to", dest="to", default="")
    args = parser.parse_args(argv)

    cfg = config()
    if args.cmd == "status":
        result = tool_email_status(cfg, {})
    elif args.cmd == "send-telemetry":
        result = tool_send_telemetry(cfg, {"root_path": args.root, "trigger": args.trigger})
    else:
        result = tool_send_demand_report(cfg, {"demand_path": args.demand_path, "to": args.to})
    print(result["content"][0]["text"])
    return 1 if result.get("isError") else 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(cli_main(sys.argv[1:]))
    main()
