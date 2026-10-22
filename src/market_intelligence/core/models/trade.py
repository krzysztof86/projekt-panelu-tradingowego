"""Single executed public trade."""

from decimal import (
    MAX_EMAX,
    MIN_EMIN,
    ROUND_HALF_EVEN,
    Clamped,
    Context,
    Decimal,
    DecimalException,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Subnormal,
    Underflow,
)
from typing import Annotated, Self

from pydantic import Field, model_validator

from market_intelligence.core.models.base import VersionedContractModel
from market_intelligence.core.models.data_quality import DataQuality
from market_intelligence.core.models.enums import AggressorSide, DataSource
from market_intelligence.core.models.instrument import Instrument
from market_intelligence.core.models.types import PositiveDecimal, UtcDatetime

TradeId = Annotated[str, Field(pattern=r"^\S{1,128}$")]
"""Exchange-native trade identifier, preserved verbatim."""

_ALL_SIGNALS = [
    Clamped,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Subnormal,
    Underflow,
]


def _exact_product(left: Decimal, right: Decimal) -> Decimal:
    """Return ``left * right`` exactly, independent of the caller's decimal context.

    A product of an n-digit and an m-digit coefficient has at most n + m digits, so a
    private context with that precision never rounds. Every signal is trapped, so any
    deviation from an exact result raises instead of returning a rounded value.
    """
    digits = len(left.as_tuple().digits) + len(right.as_tuple().digits)
    context = Context(
        prec=digits,
        rounding=ROUND_HALF_EVEN,
        Emin=MIN_EMIN,
        Emax=MAX_EMAX,
        capitals=1,
        clamp=0,
        flags=[],
        traps=_ALL_SIGNALS,
    )
    try:
        return context.multiply(left, right)
    except DecimalException as exc:
        raise ValueError(f"price * quantity cannot be computed exactly: {exc!r}") from exc


class Trade(VersionedContractModel):
    """Executed trade with its aggressor side.

    ``quantity`` is in units of the base asset. For a linear USDT contract the value in
    USDT is exactly ``price * quantity``; the contract enforces that equality with exact
    arithmetic that does not depend on the active decimal context (DEC-010).
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
        expected = _exact_product(self.price, self.quantity)
        if self.value_usdt != expected:
            raise ValueError(
                f"value_usdt {self.value_usdt} must equal price * quantity ({expected})"
            )
        return self
