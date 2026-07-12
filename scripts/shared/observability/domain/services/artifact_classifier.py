"""Canonical artifact-type classification (pure domain service).

Single source of truth, unifying the two prior copies (this module and the
legacy ``metrics/observability.py``). Output matches the legacy metrics
classifier for every case except that a test file is classified as ``test``
before ``source_code`` (the intended, previously-encoded improvement).
"""

import re

FRAMEWORK_PREFIX_TYPES = [
    ("core/", "framework_core"),
    ("rules/common/", "framework_policy"),
    ("rules/", "framework_rule"),
    ("skills/", "framework_skill"),
    ("templates/", "framework_template"),
    ("connectors/", "framework_connector"),
    ("hosts/", "framework_host_adapter"),
    ("knowledge/", "framework_knowledge"),
]

DEMAND_NAME_TYPES = [
    ("001-state.md", "state"),
    ("002-problem.md", "problem"),
    ("003-requirements.md", "requirements"),
    ("004-risk.md", "risk"),
    ("006-decisions.md", "decisions"),
    ("003-spec.md", "spec"),
    ("012-execution-plan.md", "execution_plan"),
    ("013-validation-evidence.md", "validation_evidence"),
    ("007-audit.md", "audit"),
    ("008-metrics.md", "metrics"),
    ("009-summary.md", "summary"),
]


def _is_test(normalized: str) -> bool:
    return "/test" in normalized or normalized.endswith(("_test.py", ".test.ts", ".spec.ts"))


def classify_artifact(path: str | None) -> str:
    if not path:
        return "unknown"
    normalized = str(path).replace("\\", "/").lstrip("./")
    for prefix, artifact_type in FRAMEWORK_PREFIX_TYPES:
        if normalized.startswith(prefix):
            return artifact_type
    name = normalized.rsplit("/", 1)[-1]
    for suffix, artifact_type in DEMAND_NAME_TYPES:
        if name == suffix:
            return artifact_type
    if _is_test(normalized):
        return "test"
    if normalized.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rs")):
        return "source_code"
    if normalized.endswith((".tf", ".yaml", ".yml", ".json", ".toml", ".ini", ".env")):
        return "configuration"
    if normalized.endswith((".md", ".rst", ".txt")):
        return "documentation"
    if normalized.endswith((".log", ".jsonl")):
        return "log"
    if normalized.endswith((".diff", ".patch")):
        return "diff"
    return "external_source" if re.match(r"^[a-z]+://", normalized) else "unknown"
