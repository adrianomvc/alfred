from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class ModelRate:
    input_per_1m: Decimal = Decimal("0")
    output_per_1m: Decimal = Decimal("0")
    cache_creation_per_1m: Decimal = Decimal("0")
    cache_read_per_1m: Decimal = Decimal("0")


class RateCardRepository(Protocol):
    def get_for_model(self, model: str) -> ModelRate | None: ...

