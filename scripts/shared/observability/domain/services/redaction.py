"""Sensitive-path redaction (pure domain policy).

Moved verbatim from the legacy ``metrics/observability.py`` so the redaction
rule has a single home. No file I/O -- only pattern matching and hashing.
"""

import hashlib
import re

SENSITIVE_PATH_RE = re.compile(
    r"(^|[\\/])(\.env($|[.\-_])|id_rsa|id_dsa|id_ed25519|\.ssh|\.aws|"
    r"credentials?|secrets?|private[-_]?key|token|password)",
    re.IGNORECASE,
)


def stable_hash(value):
    return "sha256:" + hashlib.sha256(str(value).encode("utf-8")).hexdigest()


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
