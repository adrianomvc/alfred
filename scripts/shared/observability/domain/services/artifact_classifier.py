from pathlib import PurePosixPath


def classify_artifact(path: str | None) -> str:
    if not path:
        return "unknown"
    normalized = str(path).replace("\\", "/").lstrip("./")
    name = PurePosixPath(normalized).name.lower()
    if name.endswith(("_test.py", ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")) or "/test" in normalized.lower():
        return "test"
    if normalized.startswith("core/"):
        return "framework_core"
    if normalized.startswith("rules/common/"):
        return "framework_policy"
    if normalized.startswith("rules/"):
        return "framework_rule"
    if normalized.startswith("skills/"):
        return "framework_skill"
    if normalized.startswith("templates/"):
        return "framework_template"
    if normalized.startswith("connectors/"):
        return "framework_connector"
    if normalized.startswith("hosts/"):
        return "framework_host_adapter"
    if normalized.startswith("knowledge/"):
        return "framework_knowledge"
    if name in {"001-state.md"}:
        return "state"
    if name.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rs")):
        return "source_code"
    if name.endswith((".tf", ".yaml", ".yml", ".json", ".toml", ".ini", ".env")):
        return "configuration"
    if name.endswith((".log", ".jsonl")):
        return "log"
    if name.endswith((".md", ".rst", ".txt")):
        return "documentation"
    return "external_source" if "://" in normalized else "unknown"

