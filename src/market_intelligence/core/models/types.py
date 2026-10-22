"""Reusable constrained field types for data contracts.

Financial values are ``Decimal``. ``float`` and ``bool`` inputs are rejected so that no
binary rounding can enter a contract silently (DEC-003). Timestamps must carry timezone
information and are normalized to UTC; numeric epoch timestamps are rejected because
their unit (s/ms/us) would have to be guessed (DEC-004).
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, Field

from market_intelligence.core.clock import ensure_utc

_NUMERIC_STRING = re.compile(r"^\s*[+-]?\d+(\.\d*)?([eE][+-]?\d+)?\s*$")


def _reject_float_and_bool(value: object) -> object:
    if isinstance(value, bool):
        raise ValueError("bool is not a valid financial value")
    if isinstance(value, float):
        raise ValueError("float is not accepted for financial values; pass Decimal, int or str")
    return value


def _require_finite(value: Decimal) -> Decimal:
    if not value.is_finite():
        raise ValueError("NaN and Infinity are not allowed")
    return value


def _require_positive(value: Decimal) -> Decimal:
    if value <= 0:
        raise ValueError("value must be greater than zero")
    return value


def _require_non_negative(value: Decimal) -> Decimal:
    if value < 0:
        raise ValueError("value must not be negative")
    return value


def _reject_numeric_timestamp(value: object) -> object:
    if isinstance(value, bool | int | float | Decimal) or (
        isinstance(value, str) and _NUMERIC_STRING.match(value)
    ):
        raise ValueError(
            "numeric timestamps are not accepted; provide a timezone-aware datetime "
            "or an ISO 8601 string with a UTC offset"
        )
    return value


FiniteDecimal = Annotated[
    Decimal, BeforeValidator(_reject_float_and_bool), AfterValidator(_require_finite)
]
"""Any finite Decimal (may be negative or zero)."""

PositiveDecimal = Annotated[FiniteDecimal, AfterValidator(_require_positive)]
"""Finite Decimal strictly greater than zero (prices, quantities, tick size)."""

NonNegativeDecimal = Annotated[FiniteDecimal, AfterValidator(_require_non_negative)]
"""Finite Decimal greater than or equal to zero (turnover)."""

UtcDatetime = Annotated[
    datetime, BeforeValidator(_reject_numeric_timestamp), AfterValidator(ensure_utc)
]
"""Timezone-aware datetime normalized to UTC. Naive datetimes are rejected."""

ExchangeSymbol = Annotated[str, Field(pattern=r"^[^\s:]{1,64}$")]
"""Exchange-native symbol, preserved verbatim (no case or format normalization)."""

AssetCode = Annotated[str, Field(pattern=r"^[^\s:]{1,32}$")]
"""Asset code as reported by the exchange, preserved verbatim."""

ReasonText = Annotated[str, Field(min_length=1, max_length=500, pattern=r"^\S(.*\S)?$")]
"""Single-line, non-blank explanation without leading or trailing whitespace."""
