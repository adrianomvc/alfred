"""Text-file helpers used by command wrappers."""

from pathlib import Path


def read_lines(path):
    """Read a text file as a list of lines without trailing newlines."""
    return Path(path).read_text(encoding="utf-8-sig").splitlines()


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig")


def find_observability_logs(root):
    return sorted(Path(root).rglob("*observability-log.jsonl"))
