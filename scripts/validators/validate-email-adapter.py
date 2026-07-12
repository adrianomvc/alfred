#!/usr/bin/env python3
"""Behavior-check the Python-only notification e-mail adapter."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def read_jsonl(path):
    events = []
    if not path.exists():
        raise SystemExit(f"Missing audit JSONL: {path}")
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Invalid audit JSONL at line {line_number}: {exc}") from exc
    return events


def run_adapter(root, temp_dir, to_addr):
    adapter = root / "scripts/adapters/mcp-email-server.py"
    demand = root / "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/006-simulado-adocao-v2"
    outbox = temp_dir / "outbox"
    audit = temp_dir / "audit.jsonl"
    env = os.environ.copy()
    env.update({
        "ALFRED_EMAIL_MODE": "dry-run",
        "ALFRED_EMAIL_DEFAULT_TO": "test@example.com",
        "ALFRED_EMAIL_ALLOWLIST": "test@example.com",
        "ALFRED_EMAIL_OUTBOX": str(outbox),
        "ALFRED_EMAIL_AUDIT": str(audit),
    })
    command = [
        sys.executable,
        str(adapter),
        "send-report",
        "--demand-path",
        str(demand),
        "--to",
        to_addr,
    ]
    return subprocess.run(command, capture_output=True, text=True, env=env), outbox, audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    with tempfile.TemporaryDirectory(prefix="alfred-email-adapter-") as tmp:
        temp_dir = Path(tmp)

        allowed, outbox, audit = run_adapter(root, temp_dir, "test@example.com")
        if allowed.returncode != 0:
            raise SystemExit(f"Expected dry-run send-report to pass: {allowed.stderr or allowed.stdout}")
        if "DRY-RUN: e-mail composed" not in allowed.stdout:
            raise SystemExit("Dry-run output did not report composed e-mail.")
        if "[Alfred-Framework]" not in allowed.stdout:
            raise SystemExit("Dry-run output did not include the subject prefix.")
        eml_files = list(outbox.glob("*.eml"))
        if len(eml_files) != 1:
            raise SystemExit(f"Expected exactly one dry-run .eml, found {len(eml_files)}.")

        refused, _, audit = run_adapter(root, temp_dir, "outside@example.com")
        if refused.returncode == 0:
            raise SystemExit("Expected destination outside allowlist to be refused.")
        if "not in the allowlist" not in refused.stdout:
            raise SystemExit("Refusal output did not explain allowlist failure.")

        events = read_jsonl(audit)
        dry_events = [event for event in events if event.get("result") == "dry-run"]
        refused_events = [event for event in events if event.get("result") == "refused"]
        if len(dry_events) != 1 or len(refused_events) != 1:
            raise SystemExit("Expected one dry-run audit event and one refused audit event.")
        for event in dry_events + refused_events:
            subject = str(event.get("subject", ""))
            if not subject.startswith("[Alfred-Framework]"):
                raise SystemExit(f"Audit subject missing prefix for {event.get('result')}: {subject}")

    print("Email adapter validation completed.")


if __name__ == "__main__":
    main()
