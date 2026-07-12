"""Load an approved rate card from disk (I/O side of pricing).

Mirrors the legacy ``load_rate_card`` in the metrics commands: validate the
``alfred.usage-rate-card.v1`` schema, require models, and expose the file hash
and metadata the cost event carries.
"""

import hashlib
import json
from pathlib import Path

from shared.observability.domain.services.rate_card import ModelRate


class RateCardError(Exception):
    """Raised when the rate card is missing, malformed, or empty."""


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
