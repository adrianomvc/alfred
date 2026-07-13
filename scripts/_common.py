"""Compatibility shim for shared Alfred Python helpers.

New code should import from ``shared.common``. This module preserves the legacy
``from _common import ...`` call sites used by public command wrappers.
"""

from shared.common import (  # noqa: F401
    find_observability_logs,
    get_field,
    iter_jsonl,
    normalize_phase,
    phase_number,
    read_lines,
    read_state_fields,
    read_text,
)


def value_or(value, default):
    if value is None or str(value) == "":
        return default
    return str(value)
