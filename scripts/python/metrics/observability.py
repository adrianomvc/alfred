"""Shared observability helpers for Alfred metrics scripts.

The helpers keep compatibility with ``alfred.observability.v1`` while adding
normalized, decision-oriented fields. They never inspect file contents unless a
caller explicitly asks for metadata about a path.
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SENSITIVE_PATH_RE = re.compile(
    r"(^|[\\/])(\.env($|[.\-_])|id_rsa|id_dsa|id_ed25519|\.ssh|\.aws|"
    r"credentials?|secrets?|private[-_]?key|token|password)",
    re.IGNORECASE,
)

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


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_hash(value):
    return "sha256:" + hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def is_sensitive_path(path):
    return bool(path and SENSITIVE_PATH_RE.search(str(path)))


def safe_path(path):
    if not path:
        return None
    text = str(path).replace("\\", "/")
    if is_sensitive_path(text):
        return {
            "path": None,
            "path_redacted": True,
            "path_category": "sensitive",
            "path_hash": stable_hash(text),
        }
    return {"path": text, "path_redacted": False}


def classify_artifact(path):
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
    if normalized.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rs")):
        return "source_code"
    if "/test" in normalized or normalized.endswith(("_test.py", ".test.ts", ".spec.ts")):
        return "test"
    if normalized.endswith((".tf", ".yaml", ".yml", ".json", ".toml", ".ini", ".env")):
        return "configuration"
    if normalized.endswith((".md", ".rst", ".txt")):
        return "documentation"
    if normalized.endswith((".log", ".jsonl")):
        return "log"
    if normalized.endswith((".diff", ".patch")):
        return "diff"
    return "external_source" if re.match(r"^[a-z]+://", normalized) else "unknown"


def path_metadata(path):
    safe = safe_path(path)
    if not safe or safe.get("path_redacted"):
        return safe or {}
    p = Path(path)
    if not p.exists() or not p.is_file():
        return safe
    try:
        text = p.read_text(encoding="utf-8-sig", errors="ignore")
        safe["size_bytes"] = p.stat().st_size
        safe["lines_read"] = len(text.splitlines())
        safe["content_hash"] = file_hash(p)
    except OSError:
        safe["size_bytes"] = p.stat().st_size if p.exists() else None
    return safe


def canonical_artifact(path, operation="read", *, selection_reason=None, observed_by=None,
                       ts=None, extra=None, collect_file_metadata=False):
    metadata = path_metadata(path) if collect_file_metadata else safe_path(path)
    item = {
        "path": metadata.get("path") if metadata else None,
        "artifact_type": classify_artifact(path),
        "operation": operation,
        "selection_reason": selection_reason,
        "observed_by": observed_by,
        "size_bytes": metadata.get("size_bytes") if metadata else None,
        "lines_read": metadata.get("lines_read") if metadata else None,
        "content_hash": metadata.get("content_hash") if metadata else None,
        "first_seen_at": ts,
        "last_seen_at": ts,
        "read_count": 1 if operation == "read" else 0,
    }
    if metadata:
        for key in ("path_redacted", "path_category", "path_hash"):
            if key in metadata:
                item[key] = metadata[key]
    if extra:
        item.update(extra)
    return item


def normalize_artifacts_used(value, *, observed_by=None, ts=None):
    """Return the canonical list shape, accepting legacy object/list forms."""
    if value is None:
        return []
    if isinstance(value, list):
        output = []
        for item in value:
            if isinstance(item, dict):
                path = item.get("path") or item.get("target")
                operation = item.get("operation") or item.get("action") or item.get("role") or "read"
                normalized = canonical_artifact(path, operation, observed_by=observed_by, ts=ts)
                normalized.update({k: v for k, v in item.items() if k not in ("path", "operation", "action")})
                if "operation" not in normalized or normalized["operation"] is None:
                    normalized["operation"] = operation
                output.append(normalized)
            elif isinstance(item, str):
                output.append(canonical_artifact(item, "read", observed_by=observed_by, ts=ts))
        return output
    if isinstance(value, dict):
        output = []
        for operation, paths in value.items():
            if paths is None:
                continue
            if not isinstance(paths, list):
                paths = [paths]
            op = "create" if operation == "created" else "update" if operation == "updated" else operation
            for path in paths:
                output.append(canonical_artifact(path, op, observed_by=observed_by, ts=ts))
        return output
    return []


def token_value(event, key):
    output = event.get("output") or {}
    value = output.get(key)
    if value is None:
        value = event.get(key)
    return value if value is not None else None


def token_int(event, key):
    value = token_value(event, key)
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def usage_tokens(event):
    tokens = {
        "tokens_input": token_int(event, "tokens_input"),
        "tokens_output": token_int(event, "tokens_output"),
        "tokens_cache_creation": token_int(event, "tokens_cache_creation"),
        "tokens_cache_read": token_int(event, "tokens_cache_read"),
    }
    tokens["total_tokens"] = sum(tokens.values())
    denominator = tokens["tokens_input"] + tokens["tokens_cache_creation"] + tokens["tokens_cache_read"]
    tokens["cache_reuse_ratio"] = None if denominator == 0 else tokens["tokens_cache_read"] / denominator
    return tokens


def semantic_event_key(event):
    event_type = event.get("event_type")
    if event_type == "usage_attributed":
        return (
            event_type,
            event.get("session_id"),
            event.get("request_id") or tuple((event.get("input") or {}).get("request_ids") or []),
        )
    if event_type == "usage_cost_attributed":
        metadata = event.get("metadata") or {}
        return (event_type, event.get("parent_event_id"), metadata.get("rate_card_hash"))
    return (event_type, event.get("event_id"))


def effective_events(events):
    """Deduplicate by event_id and semantic key, keeping the latest occurrence."""
    keyed = {}
    unkeyed = []
    for index, event in enumerate(events):
        event_id = event.get("event_id")
        semantic = semantic_event_key(event)
        key = ("event_id", event_id) if event_id else ("semantic", json.dumps(semantic, sort_keys=True, default=str))
        keyed[key] = (index, event)
        if not event_id and key[0] != "semantic":
            unkeyed.append((index, event))
    merged = [*keyed.values(), *unkeyed]
    return [event for _, event in sorted(merged, key=lambda item: item[0])]


def cost_value(event):
    value = (event.get("output") or {}).get("cost_usd")
    if value is None:
        value = event.get("cost_usd")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
