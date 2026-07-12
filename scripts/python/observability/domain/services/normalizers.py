def normalize_lane(value: object) -> str | None:
    text = str(value or "").strip().lower()
    if not text:
        return None
    aliases = {"standard": "standard", "std": "standard", "safe": "safe", "fast": "fast"}
    return aliases.get(text, text)


def normalize_phase(value: object) -> str | None:
    text = str(value or "").strip().lower()
    aliases = {
        "validation": "validate",
        "validate": "validate",
        "operations": "operation",
        "operate": "operation",
        "operation": "operation",
        "inception": "inception",
        "design": "design",
        "execution": "execution",
    }
    return aliases.get(text, text or None)


def normalize_host(value: object) -> str | None:
    text = str(value or "").strip().lower().replace("_", "-").replace(" ", "-")
    aliases = {"claude": "claude-code", "claude-code": "claude-code", "devin": "devin-cli"}
    return aliases.get(text, text or None)

