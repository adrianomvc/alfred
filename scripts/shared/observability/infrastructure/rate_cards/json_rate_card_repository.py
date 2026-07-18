"""Load an approved rate card from disk (I/O side of pricing).

Mirrors the legacy ``load_rate_card`` in the metrics commands: validate the
``alfred.usage-rate-card.v1`` schema, require models, and expose the file hash
and metadata the cost event carries.
"""

import hashlib
import json
import math
from datetime import date, datetime, timezone
from pathlib import Path

from shared.observability.domain.services.rate_card import ModelRate


class RateCardError(Exception):
    """Raised when the rate card is missing, malformed, or empty."""


def load_approved_acu_usd_rate(path: str, observed_at: str | None = None) -> float | None:
    """Load an approved, effective USD/ACU rate or degrade to ``None``."""
    if not path:
        return None
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        rate = float((payload.get("acu") or {}).get("usd_per_acu"))
        effective = date.fromisoformat(payload["effective_from"])
        observed = datetime.fromisoformat(
            (observed_at or datetime.now(timezone.utc).isoformat()).replace("Z", "+00:00")
        ).date()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
    required = (payload.get("source"), payload.get("approved_by"), payload.get("currency"))
    if payload.get("schema_version") != "alfred.usage-rate-card.v1" or not all(required):
        return None
    if str(payload["currency"]).upper() != "USD" or effective > observed:
        return None
    if not math.isfinite(rate) or rate <= 0:
        return None
    effective_to = payload.get("effective_to")
    if effective_to:
        try:
            if observed > date.fromisoformat(effective_to):
                return None
        except ValueError:
            return None
    return rate


class JsonRateCardRepository:
    def __init__(self, path: str) -> None:
        resolved = Path(path).resolve()
        payload = json.loads(resolved.read_text(encoding="utf-8-sig"))
        if payload.get("schema_version") != "alfred.usage-rate-card.v1":
            raise RateCardError("Unsupported rate card schema_version.")
        if not payload.get("models"):
            raise RateCardError("Rate card has no models.")
        self._payload = payload
        self._path = str(resolved)
        self._hash = hashlib.sha256(resolved.read_bytes()).hexdigest()

    def get_for_model(self, model: str) -> ModelRate | None:
        rates = (self._payload.get("models") or {}).get(model)
        return ModelRate.from_mapping(rates)

    def raw_rates_for(self, model: str) -> dict | None:
        """The declared rate mapping, as-is, for embedding in the cost event."""
        return (self._payload.get("models") or {}).get(model)

    @property
    def path(self) -> str:
        return self._path

    @property
    def hash(self) -> str:
        return self._hash

    def metadata(self) -> dict:
        return {
            "path": self._path,
            "hash": self._hash,
            "source": self._payload.get("source"),
            "currency": self._payload.get("currency", "USD"),
            "confidence": self._payload.get("confidence", "rated"),
            "effective_from": self._payload.get("effective_from"),
            "approved_by": self._payload.get("approved_by"),
        }
