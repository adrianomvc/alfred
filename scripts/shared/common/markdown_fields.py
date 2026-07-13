"""Markdown list-field parsing helpers."""

import re


def get_field(lines, names):
    """Return the first ``- name: value`` match for any name in ``names``."""
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
