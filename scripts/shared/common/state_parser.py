"""Demand state Markdown parsing helpers."""

from pathlib import Path


def read_state_fields(path):
    """Parse a state markdown file into a ``{lowercased key: value}`` dict."""
    fields = {}
    path = Path(path) if path else None
    if not path or not path.exists():
        return fields
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped[2:].split(":", 1)
        fields[key.strip().lower()] = value.strip()
    return fields
