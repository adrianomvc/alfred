"""Lifecycle normalization helpers."""


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
