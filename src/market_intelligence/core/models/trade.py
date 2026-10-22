"""Single executed public trade."""

from decimal import localcontext
from typing import Annotated, Self

from pydantic import Field, model_validator

from market_intelligence.core.models.base import VersionedContractModel
from market_intelligence.core.models.data_quality import DataQuality
from market_intelligence.core.models.enums import AggressorSide, DataSource
from market_intelligence.core.models.instrument import Instrument
from market_intelligence.core.models.types import PositiveDecimal, UtcDatetime

TradeId = Annotated[str, Field(pattern=r"^\S{1,128}$")]
"""Exchange-native trade identifier, preserved verbatim."""

_VALUE_PRECISION = 100
"""Decimal precision for the value check; high enough that the product is exact."""


class Trade(VersionedContractModel):
    """Executed trade with its aggressor side.

    ``quantity`` is in units of the base asset. For a linear USDT contract the value in
    USDT is exactly ``price * quantity``; the contract enforces that equality (DEC-010).
    """

    instrument: Instrument
    trade_id: TradeId
    price: PositiveDecimal
    quantity: PositiveDecimal
    value_usdt: PositiveDecimal
    aggressor_side: AggressorSide
    executed_at: UtcDatetime
    received_at: UtcDatetime
    source: DataSource
    quality: DataQuality

    @model_validator(mode="after")
    def _check_value(self) -> Self:
        with localcontext(prec=_VALUE_PRECISION):
            expected = self.price * self.quantity
        if self.value_usdt != expected:
            raise ValueError(
                f"value_usdt {self.value_usdt} must equal price * quantity ({expected})"
            )
        return self
