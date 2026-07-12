from typing import Protocol

from shared.observability.domain.services.rate_card import ModelRate

__all__ = ["ModelRate", "RateCardRepository"]


class RateCardRepository(Protocol):
    def get_for_model(self, model: str) -> ModelRate | None: ...

    def metadata(self) -> dict: ...
