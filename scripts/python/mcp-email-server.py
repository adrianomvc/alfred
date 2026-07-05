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

Configuration (environment):
- ``ALFRED_EMAIL_MODE``       dry-run | active | disabled   (default: dry-run)
- ``ALFRED_EMAIL_DEFAULT_TO`` default destination (required to send anything)
- ``ALFRED_EMAIL_ALLOWLIST``  comma-separated allowed recipients (default: DEFAULT_TO)
- ``ALFRED_EMAIL_OUTBOX``     dry-run outbox dir (default: ./.alfred-email-outbox)
- ``ALFRED_EMAIL_AUDIT``      audit JSONL path (default: <outbox>/audit-log.jsonl)
- ``SMTP_HOST`` ``SMTP_PORT`` ``SMTP_USER`` ``SMTP_PASS`` ``SMTP_FROM``  (active mode)

Register in Claude Code:  ``claude mcp add alfred-email -- python scripts/python/mcp-email-server.py``

Guardrails (injection/authorization):
- recipients outside the allowlist are refused — new destination requires a human
  updating the configuration, never the model talking the adapter into it;
- the subject is always prefixed ``[Alfred-Framework]``;
- every attempt (sent, dry-run, or refused) is appended to the audit JSONL with
  the connector's audit fields.
"""

import json
import os
import smtplib
import sys
import time
from email.message import EmailMessage
from pathlib import Path

SERVER_NAME = "alfred-email"
SERVER_VERSION = "2.0.0"
SUBJECT_PREFIX = "[Alfred-Framework]"


def config():
    mode = os.environ.get("ALFRED_EMAIL_MODE", "dry-run").strip().lower()
    default_to = os.environ.get("ALFRED_EMAIL_DEFAULT_TO", "").strip()
    allowlist = [a.strip().lower() for a in
                 os.environ.get("ALFRED_EMAIL_ALLOWLIST", default_to).split(",") if a.strip()]
    outbox = Path(os.environ.get("ALFRED_EMAIL_OUTBOX", ".alfred-email-outbox"))
    audit = Path(os.environ.get("ALFRED_EMAIL_AUDIT", str(outbox / "audit-log.jsonl")))
    return {
        "mode": mode, "default_to": default_to, "allowlist": allowlist,
        "outbox": outbox, "audit": audit,
        "smtp": {
            "host": os.environ.get("SMTP_HOST", ""),
            "port": int(os.environ.get("SMTP_PORT", "587") or 587),
            "user": os.environ.get("SMTP_USER", ""),
            "password": os.environ.get("SMTP_PASS", ""),
            "sender": os.environ.get("SMTP_FROM", os.environ.get("SMTP_USER", "")),
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


def tool_email_status(cfg, _args):
    smtp_ready = bool(cfg["smtp"]["host"] and cfg["smtp"]["sender"])
    return ok(json.dumps({
        "mode": cfg["mode"],
        "default_to": cfg["default_to"] or None,
        "allowlist": cfg["allowlist"],
        "smtp_configured": smtp_ready,
        "outbox": str(cfg["outbox"]),
        "audit_log": str(cfg["audit"]),
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
        "name": "email_status",
        "description": "Report the adapter state: mode (dry-run/active/disabled), allowlist, SMTP readiness, outbox and audit paths.",
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
        if name == "email_status":
            return tool_email_status(cfg, args)
        return err(f"Unknown tool '{name}'. Available: send_email, email_status.")
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


if __name__ == "__main__":
    main()
