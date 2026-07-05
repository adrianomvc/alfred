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
        "smtp": {"host": "", "port": 587, "user": "", "password": "", "sender": ""}}

   ``telemetry_to`` is the ORG destination that receives every runner's
   observability batches (``send_telemetry``) — provisional transport until the
   telemetry API exists (D45). It is auto-added to the allowlist.

2. **Environment variables** (override the file):
   ``ALFRED_EMAIL_MODE``       dry-run | active | disabled   (default: dry-run)
   ``ALFRED_EMAIL_DEFAULT_TO`` default destination
   ``ALFRED_EMAIL_ALLOWLIST``  comma-separated allowed recipients (default: DEFAULT_TO)
   ``ALFRED_EMAIL_OUTBOX``     dry-run outbox dir (default: ./.alfred-email-outbox)
   ``ALFRED_EMAIL_AUDIT``      audit JSONL path (default: <outbox>/audit-log.jsonl)
   ``SMTP_HOST`` ``SMTP_PORT`` ``SMTP_USER`` ``SMTP_PASS`` ``SMTP_FROM``  (active mode)
3. At adoption, the sigla records destination + triggers in its HUB ``knowledge``
   (see ``knowledge/notification.md``); this file/env is the machine-level mirror.

Register in Claude Code:  ``claude mcp add alfred-email -- python scripts/python/adapters/mcp-email-server.py``

Guardrails (injection/authorization):
- recipients outside the allowlist are refused — new destination requires a human
  updating the configuration, never the model talking the adapter into it;
- the subject is always prefixed ``[Alfred-Framework]``;
- every attempt (sent, dry-run, or refused) is appended to the audit JSONL with
  the connector's audit fields.
"""

import getpass
import json
import os
import smtplib
import socket
import sys
import time
from email.message import EmailMessage
from pathlib import Path

SERVER_NAME = "alfred-email"
SERVER_VERSION = "2.0.0"
SUBJECT_PREFIX = "[Alfred-Framework]"


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
    return {
        "mode": mode, "default_to": default_to, "telemetry_to": telemetry_to, "allowlist": allowlist,
        "outbox": outbox, "audit": audit, "config_path": config_path,
        "smtp": {
            "host": os.environ.get("SMTP_HOST") or file_smtp.get("host", ""),
            "port": int(os.environ.get("SMTP_PORT") or file_smtp.get("port") or 587),
            "user": os.environ.get("SMTP_USER") or file_smtp.get("user", ""),
            "password": os.environ.get("SMTP_PASS") or file_smtp.get("password", ""),
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
    except OSError:
        pass  # auditing must never break the send path; the caller still reports
    return event


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
    if not destination:
        return err("No destination: pass `to` or set ALFRED_EMAIL_DEFAULT_TO. "
                   "The destination must come from configuration, not from guessed values.")
    if destination.lower() not in cfg["allowlist"]:
        audit_event(cfg, destination, subject, attachments, "refused",
                    "destination not in allowlist", trigger)
        return err(f"Destination '{destination}' is not in the allowlist. "
                   "A new destination requires a HUMAN to update ALFRED_EMAIL_ALLOWLIST "
                   "(durable authorization) — do not retry with other addresses.")
    missing = [a for a in attachments if not Path(a).is_file()]
    if missing:
        return err("Attachment(s) not found: " + ", ".join(missing) +
                   ". Pass existing file paths (e.g. the demand's metrics/audit files).")
    if not subject.startswith(SUBJECT_PREFIX):
        subject = f"{SUBJECT_PREFIX} {subject}"

    if cfg["mode"] == "dry-run":
        cfg["outbox"].mkdir(parents=True, exist_ok=True)
        msg = build_message(cfg["smtp"]["sender"], destination, subject, body, attachments)
        out = cfg["outbox"] / (time.strftime("%Y%m%dT%H%M%S") + "-" +
                               "".join(c if c.isalnum() else "-" for c in subject[:40]) + ".eml")
        out.write_bytes(bytes(msg))
        audit_event(cfg, destination, subject, attachments, "dry-run", None, trigger)
        return ok(f"DRY-RUN: e-mail composed, not sent. Written to {out} | to={destination} | "
                  f"subject={subject} | attachments={len(attachments)}. "
                  "Set ALFRED_EMAIL_MODE=active (+ SMTP_*) to really send.")

    smtp = cfg["smtp"]
    if not smtp["host"] or not smtp["sender"]:
        audit_event(cfg, destination, subject, attachments, "failed",
                    "active mode without SMTP configuration", trigger)
        return err("Active mode but SMTP is not configured. Set SMTP_HOST, SMTP_PORT, "
                   "SMTP_USER, SMTP_PASS, SMTP_FROM — or use ALFRED_EMAIL_MODE=dry-run.")
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


def tool_send_telemetry(cfg, args):
    """Batch every local observability JSONL and e-mail it to the org telemetry
    destination — provisional transport (D45) until the telemetry API exists, so
    logs from everyone running Alfred can be aggregated into org metrics."""
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

    sender_id = f"{getpass.getuser()}@{socket.gethostname()}"
    stamp = time.strftime("%Y%m%dT%H%M%S")
    cfg["outbox"].mkdir(parents=True, exist_ok=True)
    batch_path = cfg["outbox"] / f"telemetry-batch-{stamp}.jsonl"
    total = 0
    per_source = []
    with open(batch_path, "w", encoding="utf-8") as batch:
        for log in logs:
            try:
                rel = str(log.relative_to(root))
            except ValueError:
                rel = str(log)
            count = 0
            for raw in log.read_text(encoding="utf-8-sig").splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    event = {"_unparsed": raw}
                batch.write(json.dumps({"sender": sender_id, "collected_at": stamp,
                                         "source": rel, "event": event},
                                        ensure_ascii=False) + "\n")
                count += 1
                total += 1
            per_source.append(f"- {rel}: {count} evento(s)")

    subject = f"[telemetry][{sender_id}] {total} eventos de observabilidade"
    body = ("Lote de telemetria do Alfred (transporte provisorio por e-mail ate a API existir - D45).\n"
            f"- remetente: {sender_id}\n- raiz varrida: {root}\n- fontes: {len(logs)}\n"
            + "\n".join(per_source)
            + "\nCada linha do anexo = {sender, collected_at, source, event}.")
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
        "outbox": str(cfg["outbox"]),
        "audit_log": str(cfg["audit"]),
        "config_file": cfg["config_path"] or "not found (create ~/.alfred-email.json or set ALFRED_EMAIL_CONFIG)",
        "adapter_state": ("disabled" if cfg["mode"] == "disabled"
                           else "active" if cfg["mode"] == "active" and smtp_ready
                           else "dry-run"),
    }, ensure_ascii=False))


TOOLS = [
    {
        "name": "send_email",
        "description": ("Send an Alfred strategic notification e-mail (demand closed, critical "
                        "checkpoint, escalation, incident). Only to allowlisted destinations; "
                        "subject is prefixed [Alfred-Framework]; every attempt is audited. "
                        "In dry-run mode the message is written to an outbox instead of sent."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "short subject (prefix added automatically)"},
                "body": {"type": "string", "description": "short summary body; attach files instead of pasting them"},
                "to": {"type": "string", "description": "destination; defaults to ALFRED_EMAIL_DEFAULT_TO"},
                "trigger": {"type": "string", "description": "which configured trigger fired (e.g. demand_completed)"},
                "attachments": {"type": "array", "items": {"type": "string"},
                                 "description": "file paths (metrics.md, audit.md, summary.md)"},
            },
            "required": ["subject", "body"],
        },
    },
    {
        "name": "send_demand_report",
        "description": ("Send the demand report e-mail: reads 001-state.md for context and attaches "
                        "the demand's metrics, audit, summary, and observability JSONL automatically. "
                        "Same guardrails as send_email (allowlist, prefix, audit, dry-run by default)."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "demand_path": {"type": "string",
                                 "description": "HUB demand folder (contains 001-state.md)"},
                "to": {"type": "string", "description": "destination; defaults to the registered one"},
                "trigger": {"type": "string", "description": "default: demand_report"},
            },
            "required": ["demand_path"],
        },
    },
    {
        "name": "send_telemetry",
        "description": ("Batch every local observability JSONL under root_path and e-mail it to the "
                        "org telemetry destination (telemetry_to) — provisional transport until the "
                        "telemetry API exists. Each batch line carries {sender, collected_at, source, "
                        "event} so logs from many people can be aggregated into org metrics. "
                        "Same guardrails: allowlist, audit, dry-run by default."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "root_path": {"type": "string",
                               "description": "root to scan for *observability-log.jsonl (HUB/app root or a demand folder); default: current dir"},
                "trigger": {"type": "string", "description": "default: telemetry_batch"},
            },
        },
    },
    {
        "name": "email_status",
        "description": "Report the adapter state: mode (dry-run/active/disabled), destinations (default/telemetry), allowlist, SMTP readiness, outbox/audit paths, and which config file is in use.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


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
