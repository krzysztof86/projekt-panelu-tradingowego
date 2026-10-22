"""Reusable constrained field types for data contracts.

Financial values are ``Decimal``. ``float`` and ``bool`` inputs are rejected so that no
binary rounding can enter a contract silently (DEC-003). Every Decimal field is limited to
the financial domain defined below (DEC-020). Timestamps must be a timezone-aware
``datetime`` or a string in the RFC 3339 profile below and are normalized to UTC; any other
text, including numeric epoch timestamps whose unit would have to be guessed, is rejected
(DEC-004).
"""

import re
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Final

from pydantic import AfterValidator, BeforeValidator, Field

from market_intelligence.core.clock import ensure_utc

MAX_DECIMAL_PLACES: Final = 18
"""Maximum digits after the decimal point of a contract Decimal (DEC-020)."""

MAX_PRODUCT_DECIMAL_PLACES: Final = 2 * MAX_DECIMAL_PLACES
"""Maximum digits after the decimal point of a product of two domain values (DEC-020)."""

MAX_INTEGER_DIGITS: Final = 20
"""Absolute value of a contract Decimal must be below ``10 ** MAX_INTEGER_DIGITS`` (DEC-020)."""

_NUMERIC_STRING = re.compile(r"\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\s*")

_RFC3339 = re.compile(
    r"(?:[0-9]{4}-[0-9]{2}-[0-9]{2}T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]{1,6})?)"
    r"(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])?"
)
"""Accepted timestamp text (DEC-004): ``YYYY-MM-DDTHH:MM:SS[.ffffff](Z|+HH:MM|-HH:MM)``."""

_TIMESTAMP_FORMAT = "YYYY-MM-DDTHH:MM:SS[.ffffff] followed by Z, +HH:MM or -HH:MM"


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


def _financial_domain(max_places: int) -> Callable[[Decimal], Decimal]:
    def check(value: Decimal) -> Decimal:
        # Only context-free operations: the caller's decimal context must not matter.
        exponent = value.as_tuple().exponent
        if not isinstance(exponent, int):  # unreachable after _require_finite
            raise ValueError("NaN and Infinity are not allowed")
        if exponent < -max_places:
            raise ValueError(
                f"at most {max_places} digits after the decimal point are allowed "
                "(including trailing zeros)"
            )
        if value != 0 and value.adjusted() >= MAX_INTEGER_DIGITS:
            raise ValueError(f"absolute value must be below 1E+{MAX_INTEGER_DIGITS}")
        return value

    return check


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
        isinstance(value, str) and _NUMERIC_STRING.fullmatch(value)
    ):
        raise ValueError(
            "numeric timestamps are not accepted; provide a timezone-aware datetime "
            f"or text in the form {_TIMESTAMP_FORMAT}"
        )
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ValueError(
            f"unsupported timestamp type {type(value).__name__}; provide a timezone-aware "
            f"datetime or text in the form {_TIMESTAMP_FORMAT}"
        )
    # Allow-list: only this profile is parsed, so no other parser interprets the text. The
    # offset is optional here so that text without one is reported as naive by ensure_utc.
    if _RFC3339.fullmatch(value) is None:
        raise ValueError(f"timestamp text must have the form {_TIMESTAMP_FORMAT}")
    return datetime.fromisoformat(value)


def _require_single_line(value: str) -> str:
    # str.splitlines() defines the separators: LF, CR, CR LF, VT, FF, U+001C, U+001D,
    # U+001E, U+0085, U+2028 and U+2029.
    if value.splitlines() != [value]:
        raise ValueError("must be a single line; line separators are not allowed")
    return value


_CheckedDecimal = Annotated[
    Decimal, BeforeValidator(_reject_float_and_bool), AfterValidator(_require_finite)
]

FiniteDecimal = Annotated[_CheckedDecimal, AfterValidator(_financial_domain(MAX_DECIMAL_PLACES))]
"""Finite Decimal within the financial domain (may be negative or zero)."""

PositiveDecimal = Annotated[FiniteDecimal, AfterValidator(_require_positive)]
"""Domain Decimal strictly greater than zero (prices, quantities, tick size)."""

NonNegativeDecimal = Annotated[FiniteDecimal, AfterValidator(_require_non_negative)]
"""Domain Decimal greater than or equal to zero (turnover)."""

PositiveProductDecimal = Annotated[
    _CheckedDecimal,
    AfterValidator(_financial_domain(MAX_PRODUCT_DECIMAL_PLACES)),
    AfterValidator(_require_positive),
]
"""Positive product of two domain values (``Trade.value_usdt``): up to 36 decimal places."""

UtcDatetime = Annotated[
    datetime, BeforeValidator(_require_timestamp_input), AfterValidator(ensure_utc)
]
"""Timezone-aware datetime normalized to UTC; input ``datetime`` or RFC 3339 profile text."""

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
