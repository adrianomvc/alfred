"""Read which model a DEVIN CLI session actually ran.

Devin exposes the model three ways — `--model`, the interactive `/model`, and
`agent.model` in `config.json` — and none of them tells a script what is running
right now: no environment variable, no hook field, no session metadata (checked
against docs.devin.ai). Alfred therefore reported the *policy target* flagged
`nao confirmado`, which is honest but never resolves.

The CLI does record it locally, in two places:

- `cli/logs/devin_<ts>_<pid>.log`, at startup:
  ``model_input=<none> resolved_model=SWE-1.6 Slow resolved_model_uid=swe-1-6-slow``
  Written when the session opens, so it is readable **while** the session runs.
- `cli/transcripts/<session>.json` -> ``agent.model_name``, written when the
  session ends. Exact, but only after the fact.

The log is preferred for that reason. Only these fields are read; transcript
`steps` carry session content and are never touched (telemetry is emailed to the
org destination, so what is read here matters).
"""

import json
import os
import re
from pathlib import Path

RESOLVED = re.compile(r"resolved_model=(?P<name>.+?)\s+resolved_model_uid=(?P<uid>[\w.-]+)")


def config_dir():
    """DEVIN CLI configuration root, per host (docs.devin.ai/cli)."""
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "devin"
    return Path.home() / ".config" / "devin"


def read_session_model(root=None):
    """Return ``{"model", "uid", "source"}`` for the most recent session, or None.

    A mid-session `/model` switch is not guaranteed to re-log, so the caller must
    treat this as the model the session *started* with, not a live reading.
    """
    root = Path(root) if root is not None else config_dir()
    from_log = _read_from_logs(root / "cli" / "logs")
    if from_log is not None:
        return from_log
    return _read_from_transcripts(root / "cli" / "transcripts")


def _newest(directory, pattern):
    if not directory.is_dir():
        return []
    files = [path for path in directory.glob(pattern) if path.is_file()]
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)


def _read_from_logs(logs_dir):
    for path in _newest(logs_dir, "devin_*.log")[:5]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        matches = RESOLVED.findall(text)
        if matches:
            # last wins: a re-resolution later in the session supersedes startup
            name, uid = matches[-1]
            return {"model": name.strip(), "uid": uid, "source": f"devin log {path.name}"}
    return None


def _read_from_transcripts(transcripts_dir):
    for path in _newest(transcripts_dir, "*.json")[:5]:
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            continue
        model = (data.get("agent") or {}).get("model_name")
        if model:
            return {"model": str(model).strip(), "uid": "",
                    "source": f"devin transcript {path.name}"}
    return None
