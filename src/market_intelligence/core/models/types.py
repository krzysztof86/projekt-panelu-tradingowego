"""Reusable constrained field types for data contracts.

Financial values are ``Decimal``. ``float`` and ``bool`` inputs are rejected so that no
binary rounding can enter a contract silently (DEC-003). Every Decimal field is limited to
the financial domain defined below (DEC-020). Timestamps must be a timezone-aware
``datetime`` or an ISO 8601 string with a UTC offset and are normalized to UTC; numeric
epoch timestamps are rejected because their unit (s/ms/us) would have to be guessed
(DEC-004).
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Final

from pydantic import AfterValidator, BeforeValidator, Field

from market_intelligence.core.clock import ensure_utc

MAX_DECIMAL_PLACES: Final = 18
"""Maximum digits after the decimal point of a contract Decimal (DEC-020)."""

MAX_INTEGER_DIGITS: Final = 20
"""Absolute value of a contract Decimal must be below ``10 ** MAX_INTEGER_DIGITS`` (DEC-020)."""

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


def _require_financial_domain(value: Decimal) -> Decimal:
    # Only context-free operations: the caller's decimal context must not matter.
    exponent = value.as_tuple().exponent
    if not isinstance(exponent, int):  # unreachable after _require_finite
        raise ValueError("NaN and Infinity are not allowed")
    if exponent < -MAX_DECIMAL_PLACES:
        raise ValueError(
            f"at most {MAX_DECIMAL_PLACES} digits after the decimal point are allowed "
            "(including trailing zeros)"
        )
    if value != 0 and value.adjusted() >= MAX_INTEGER_DIGITS:
        raise ValueError(f"absolute value must be below 1E+{MAX_INTEGER_DIGITS}")
    return value


def _require_positive(value: Decimal) -> Decimal:
    if value <= 0:
        raise ValueError("value must be greater than zero")
    return value


def _require_non_negative(value: Decimal) -> Decimal:
    if value < 0:
        raise ValueError("value must not be negative")
    return value


def _require_timestamp_input(value: object) -> object:
    if isinstance(value, bool | int | float | Decimal) or (
        isinstance(value, str) and _NUMERIC_STRING.match(value)
    ):
        raise ValueError(
            "numeric timestamps are not accepted; provide a timezone-aware datetime "
            "or an ISO 8601 string with a UTC offset"
        )
    if not isinstance(value, datetime | str):
        raise ValueError(
            f"unsupported timestamp type {type(value).__name__}; provide a timezone-aware "
            "datetime or an ISO 8601 string with a UTC offset"
        )
    return value


def _require_single_line(value: str) -> str:
    # str.splitlines() defines the separators: LF, CR, CR LF, VT, FF, U+001C, U+001D,
    # U+001E, U+0085, U+2028 and U+2029.
    if value.splitlines() != [value]:
        raise ValueError("must be a single line; line separators are not allowed")
    return value


FiniteDecimal = Annotated[
    Decimal,
    BeforeValidator(_reject_float_and_bool),
    AfterValidator(_require_finite),
    AfterValidator(_require_financial_domain),
]
"""Finite Decimal within the financial domain (may be negative or zero)."""

PositiveDecimal = Annotated[FiniteDecimal, AfterValidator(_require_positive)]
"""Domain Decimal strictly greater than zero (prices, quantities, tick size)."""

NonNegativeDecimal = Annotated[FiniteDecimal, AfterValidator(_require_non_negative)]
"""Domain Decimal greater than or equal to zero (turnover)."""

UtcDatetime = Annotated[
    datetime, BeforeValidator(_require_timestamp_input), AfterValidator(ensure_utc)
]
"""Timezone-aware datetime normalized to UTC. Only ``datetime`` and ISO 8601 ``str`` input."""

ExchangeSymbol = Annotated[str, Field(pattern=r"^[^\s:]{1,64}$")]
"""Exchange-native symbol, preserved verbatim (no case or format normalization)."""

AssetCode = Annotated[str, Field(pattern=r"^[^\s:]{1,32}$")]
"""Asset code as reported by the exchange, preserved verbatim."""

ReasonText = Annotated[
    str,
    Field(min_length=1, max_length=500, pattern=r"^\S(.*\S)?$"),
    AfterValidator(_require_single_line),
]
"""Single-line, non-blank explanation without leading or trailing whitespace."""
