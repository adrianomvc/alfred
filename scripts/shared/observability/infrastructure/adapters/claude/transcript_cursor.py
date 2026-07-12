"""Incremental byte-offset cursor for Claude Code transcripts.

Single home for the cursor logic that was duplicated in
``attribute-usage-transcript.py`` and ``claude-code-usage-hook.py``. The cursor
lets the hook re-run on a growing transcript without re-emitting past requests,
and degrades safely (offset 0 = reread) on corruption, path mismatch, or
truncation/rotation.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class TranscriptCursor:
    def read_offset(self, cursor_path, transcript_path) -> int:
        if not cursor_path or not Path(cursor_path).exists():
            return 0
        try:
            payload = json.loads(Path(cursor_path).read_text(encoding="utf-8-sig"))
            if payload.get("transcript_path") != str(Path(transcript_path).resolve()):
                return 0
            offset = int(payload.get("last_byte_offset") or 0)
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return 0
        size = Path(transcript_path).stat().st_size
        return 0 if offset < 0 or offset > size else offset

    def write(self, cursor_path, transcript_path, offset, last_request_id=None) -> None:
        if not cursor_path:
            return
        target = Path(cursor_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "transcript_path": str(Path(transcript_path).resolve()),
            "last_byte_offset": offset,
            "last_request_id": last_request_id,
            "updated_at": _now_iso(),
        }
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
        tmp.replace(target)

    def read_slice(self, transcript_path, cursor_path=None):
        """Return (lines, start_offset, end_offset) from cursor to EOF.

        Lines keep the raw text (including blanks); callers filter as needed.
        """
        full = Path(transcript_path).resolve()
        offset = self.read_offset(cursor_path, full) if cursor_path else 0
        with full.open("rb") as handle:
            handle.seek(offset)
            data = handle.read()
            end_offset = handle.tell()
        lines = data.decode("utf-8-sig", errors="replace").splitlines()
        return lines, offset, end_offset
