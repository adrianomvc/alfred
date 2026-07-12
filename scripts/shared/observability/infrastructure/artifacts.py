"""Artifact record building (infrastructure: file I/O + canonical shapes).

Moved from ``metrics/observability.py``. Classification and redaction come from
the domain; this layer adds the optional filesystem metadata (size, lines, hash)
and the canonical artifact dict shape the observability events carry.
"""

import hashlib
from pathlib import Path

from shared.observability.domain.services.artifact_classifier import classify_artifact
from shared.observability.domain.services.redaction import safe_path


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


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
