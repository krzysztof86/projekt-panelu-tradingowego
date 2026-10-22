"""Regression tests for the third independent Phase 0 audit (reports/phase0/audyt3/).

K2-A01: an aware timestamp whose UTC equivalent falls outside the ``datetime`` range (for
example ``0001-01-01T00:00:00+01:00``) leaked a raw ``OverflowError`` from ``ensure_utc``
instead of a validation error. Correction 3 converts it to ``ValueError`` (``ValidationError``
inside contracts) without adding any business limit on years.

SYNTHETIC DATA: all values are invented for tests.
"""

import json
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.clock import ensure_utc
from market_intelligence.core.models import (
    Candle,
    Instrument,
    MarketEvent,
    MarketTick,
    Trade,
)

PLUS_1 = timezone(timedelta(hours=1))
MINUS_1 = timezone(timedelta(hours=-1))
UNREPRESENTABLE_TEXT = ["0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00"]
UNREPRESENTABLE_DATETIMES = [
    datetime(1, 1, 1, tzinfo=PLUS_1),
    datetime(9999, 12, 31, 23, 59, 59, tzinfo=MINUS_1),
]
MESSAGE = "has no representable UTC equivalent"
PATHS = ["python", "json"]


def _listed_at(instrument_kwargs: dict[str, Any], value: Any, path: str) -> datetime | None:
    payload = {**instrument_kwargs, "listed_at": value}
    if path == "python":
        return Instrument.model_validate(payload).listed_at
    return Instrument.model_validate_json(json.dumps(payload)).listed_at


class TestK2A01UtcOverflow:
    @pytest.mark.parametrize("path", PATHS)
    @pytest.mark.parametrize("value", UNREPRESENTABLE_TEXT)
    def test_text_edges_rejected_with_validation_error(
        self, instrument_kwargs: dict[str, Any], value: str, path: str
    ) -> None:
        with pytest.raises(ValidationError, match=MESSAGE):
            _listed_at(instrument_kwargs, value, path)

    @pytest.mark.parametrize("value", UNREPRESENTABLE_DATETIMES, ids=str)
    def test_datetime_edges_rejected_with_validation_error(
        self, instrument_kwargs: dict[str, Any], value: datetime
    ) -> None:
        with pytest.raises(ValidationError, match=MESSAGE):
            _listed_at(instrument_kwargs, value, "python")

    @pytest.mark.parametrize(
        ("fixture_name", "model", "field"),
        [
            ("tick_kwargs", MarketTick, "exchange_time"),
            ("tick_kwargs", MarketTick, "received_at"),
            ("trade_kwargs", Trade, "executed_at"),
            ("trade_kwargs", Trade, "received_at"),
            ("candle_kwargs", Candle, "start"),
            ("candle_kwargs", Candle, "end"),
            ("event_kwargs", MarketEvent, "detected_at"),
            ("event_kwargs", MarketEvent, "window_start"),
            ("event_kwargs", MarketEvent, "window_end"),
        ],
    )
    @pytest.mark.parametrize("value", UNREPRESENTABLE_TEXT)
    def test_every_timestamp_field(
        self,
        request: pytest.FixtureRequest,
        fixture_name: str,
        model: type[Any],
        field: str,
        value: str,
    ) -> None:
        kwargs = request.getfixturevalue(fixture_name)
        with pytest.raises(ValidationError, match=MESSAGE):
            model(**{**kwargs, field: value})

    @pytest.mark.parametrize("value", UNREPRESENTABLE_DATETIMES, ids=str)
    def test_ensure_utc_raises_value_error(self, value: datetime) -> None:
        with pytest.raises(ValueError, match=MESSAGE) as info:
            ensure_utc(value)
        assert not isinstance(info.value, OverflowError)
        assert isinstance(info.value.__cause__, OverflowError)

    @pytest.mark.parametrize("value", UNREPRESENTABLE_DATETIMES, ids=str)
    def test_candle_contains_raises_value_error(
        self, candle_kwargs: dict[str, Any], value: datetime
    ) -> None:
        with pytest.raises(ValueError, match=MESSAGE):
            Candle(**candle_kwargs).contains(value)


REPRESENTABLE_EDGES = {
    "0001-01-01T00:00:00Z": datetime(1, 1, 1, tzinfo=UTC),
    "9999-12-31T23:59:59.999999Z": datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=UTC),
    "0001-01-01T01:00:00+01:00": datetime(1, 1, 1, tzinfo=UTC),
    "9999-12-31T22:59:59-01:00": datetime(9999, 12, 31, 23, 59, 59, tzinfo=UTC),
}


class TestRepresentableEdges:
    @pytest.mark.parametrize("path", PATHS)
    @pytest.mark.parametrize("value", list(REPRESENTABLE_EDGES))
    def test_accepted_and_normalized(
        self, instrument_kwargs: dict[str, Any], value: str, path: str
    ) -> None:
        assert _listed_at(instrument_kwargs, value, path) == REPRESENTABLE_EDGES[value]

    @pytest.mark.parametrize("value", list(REPRESENTABLE_EDGES.values()), ids=str)
    def test_ensure_utc_identity_at_utc_edges(self, value: datetime) -> None:
        assert ensure_utc(value) == value


class _OutOfRangeOffset(tzinfo):
    """tzinfo returning an offset outside the range ``datetime`` accepts (+25 h)."""

    def utcoffset(self, dt: datetime | None) -> timedelta:
        return timedelta(hours=25)

    def dst(self, dt: datetime | None) -> None:
        return None

    def tzname(self, dt: datetime | None) -> str:
        return "+25:00"


EDGE_INPUTS: list[tuple[str, str, Any]] = [
    ("tick_size", "huge exponent", "1e999999999999999999999"),
    ("tick_size", "huge negative exponent", "1e-999999999999999999999"),
    ("tick_size", "5000-digit text", "1" * 5000),
    ("tick_size", "4000-digit int", int("1" * 4000)),
    ("tick_size", "signaling NaN", Decimal("sNaN")),
    ("tick_size", "negative zero", "-0"),
    ("listed_at", "+25h tzinfo", datetime(2026, 1, 1, tzinfo=_OutOfRangeOffset())),
    ("listed_at", "year 1 +01:00", "0001-01-01T00:00:00+01:00"),
]


class TestOnlyValidationErrors:
    """Edge inputs must end in ValidationError — never in another exception type."""

    @pytest.mark.parametrize(
        ("field", "value"), [(f, v) for f, _, v in EDGE_INPUTS], ids=[n for _, n, _ in EDGE_INPUTS]
    )
    def test_instrument_edge_inputs(
        self, instrument_kwargs: dict[str, Any], field: str, value: Any
    ) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, field: value})

    def test_huge_json_integer_schema_version(self, bybit_instrument: Instrument) -> None:
        payload = bybit_instrument.model_dump_json().replace(
            '"schema_version":2', '"schema_version":' + "9" * 5000
        )
        with pytest.raises(ValidationError):
            Instrument.model_validate_json(payload)

    def test_extreme_but_valid_event_window(self, event_kwargs: dict[str, Any]) -> None:
        event = MarketEvent(
            **{
                **event_kwargs,
                "window_start": "0001-01-01T00:00:00Z",
                "window_end": "9999-12-31T23:59:59Z",
                "detected_at": "9999-12-31T23:59:59Z",
            }
        )
        assert event.window_start.year == 1
