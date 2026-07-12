"""Compatibility shim for Alfred metrics commands.

The observability helpers now live in the shared SOLID package; this module
re-exports them so existing ``from metrics.observability import ...`` call sites
keep working unchanged. New code should import from ``shared.observability.*``
directly.
"""

from datetime import datetime, timezone

from shared.observability.domain.services.artifact_classifier import classify_artifact  # noqa: F401
from shared.observability.domain.services.legacy_usage import (  # noqa: F401
    cost_value,
    semantic_event_key,
    token_int,
    token_value,
    usage_tokens,
)
from shared.observability.domain.services.redaction import (  # noqa: F401
    SENSITIVE_PATH_RE,
    is_sensitive_path,
    safe_path,
    stable_hash,
)
from shared.observability.infrastructure.artifacts import (  # noqa: F401
    canonical_artifact,
    file_hash,
    normalize_artifacts_used,
    path_metadata,
)
from shared.observability.infrastructure.legacy_events import effective_events  # noqa: F401


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
