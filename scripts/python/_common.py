"""Shared helpers for the Alfred Python helper scripts.

These mirror the PowerShell helpers under ``scripts/powershell``. They are
optional: Alfred still works manually through Markdown if no helper runs.
The Python set exists so the framework can be validated on machines without
PowerShell (D3 portability).
"""

import json
import re
from pathlib import Path


def read_lines(path):
    """Read a text file as a list of lines without trailing newlines."""
    return Path(path).read_text(encoding="utf-8-sig").splitlines()


def read_text(path):
    return Path(path).read_text(encoding="utf-8-sig")


def get_field(lines, names):
    """Return the first ``- name: value`` match for any name in ``names``.

    Mirrors the PowerShell ``Get-Field``/``Get-StateField`` helpers: matches a
    markdown list field, trims whitespace and surrounding backticks.
    """
    if isinstance(names, str):
        names = [names]
    for name in names:
        escaped = re.escape(name)
        pattern = re.compile(r"^\s*-\s+" + escaped + r"\s*:\s*(.*?)\s*$")
        for line in lines:
            match = pattern.match(line)
            if match:
                return match.group(1).strip().strip("`")
    return ""


def value_or(value, default):
    if value is None or str(value) == "":
        return default
    return str(value)


def normalize_phase(value):
    normalized = str(value).lower()
    if "inception" in normalized:
        return "inception"
    if "design" in normalized:
        return "design"
    if "execution" in normalized:
        return "execution"
    if "validate" in normalized or "validation" in normalized:
        return "validate"
    if "operation" in normalized:
        return "operation"
    return normalized


def phase_number(phase):
    normalized = str(phase).lower()
    if "inception" in normalized:
        return 1
    if "design" in normalized:
        return 2
    if "execution" in normalized:
        return 3
    if "validate" in normalized or "validation" in normalized:
        return 4
    if "operation" in normalized:
        return 5
    return 0


def iter_jsonl(path):
    """Yield ``(line_number, parsed_or_None, raw)`` for each non-empty line.

    ``parsed_or_None`` is ``None`` when the line is not valid JSON.
    """
    line_number = 0
    for raw in read_lines(path):
        line_number += 1
        if raw.strip() == "":
            continue
        try:
            yield line_number, json.loads(raw), raw
        except json.JSONDecodeError:
            yield line_number, None, raw


def find_observability_logs(root):
    return sorted(Path(root).rglob("*observability-log.jsonl"))
