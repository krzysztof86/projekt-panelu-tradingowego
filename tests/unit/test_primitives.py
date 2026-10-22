"""Decimal and UTC datetime primitives, exercised through real contract fields."""

from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.clock import UTC_EPOCH, ensure_utc
from market_intelligence.core.models import Instrument

NON_FINITE = ["NaN", "nan", "sNaN", "Infinity", "-Infinity", "inf", Decimal("NaN"), Decimal("Inf")]


class TestEnsureUtc:
    def test_converts_offset_to_utc(self) -> None:
        warsaw_summer = timezone(timedelta(hours=2))
        result = ensure_utc(datetime(2026, 7, 1, 14, 0, tzinfo=warsaw_summer))
        assert result == datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
        assert result.utcoffset() == timedelta(0)

    def test_rejects_naive(self) -> None:
        with pytest.raises(ValueError, match="naive datetime"):
            ensure_utc(datetime(2026, 1, 1))  # noqa: DTZ001 - naive on purpose

    def test_epoch(self) -> None:
        assert UTC_EPOCH.timestamp() == 0


class TestDecimalFields:
    @pytest.mark.parametrize("value", NON_FINITE)
    def test_rejects_nan_and_infinity(self, instrument_kwargs: dict[str, Any], value: Any) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, "tick_size": value})

    def test_rejects_float(self, instrument_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="float is not accepted"):
            Instrument(**{**instrument_kwargs, "tick_size": 0.1})

    def test_rejects_bool(self, instrument_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="bool is not a valid"):
            Instrument(**{**instrument_kwargs, "tick_size": True})

    @pytest.mark.parametrize("value", ["0.10", Decimal("0.10"), 1])
    def test_accepts_str_decimal_int(self, instrument_kwargs: dict[str, Any], value: Any) -> None:
        instrument = Instrument(**{**instrument_kwargs, "tick_size": value})
        assert isinstance(instrument.tick_size, Decimal)
        assert instrument.tick_size == Decimal(value)

    def test_keeps_exact_representation(self, instrument_kwargs: dict[str, Any]) -> None:
        instrument = Instrument(**{**instrument_kwargs, "tick_size": "0.00000100"})
        assert instrument.tick_size.as_tuple() == Decimal("0.00000100").as_tuple()


class TestDatetimeFields:
    def test_normalizes_to_utc(self, instrument_kwargs: dict[str, Any]) -> None:
        instrument = Instrument(**{**instrument_kwargs, "listed_at": "2026-03-01T10:00:00+05:30"})
        assert instrument.listed_at == datetime(2026, 3, 1, 4, 30, tzinfo=UTC)
        assert instrument.listed_at.tzinfo is UTC

    def test_accepts_z_suffix(self, instrument_kwargs: dict[str, Any]) -> None:
        instrument = Instrument(**{**instrument_kwargs, "listed_at": "2026-03-01T10:00:00Z"})
        assert instrument.listed_at == datetime(2026, 3, 1, 10, 0, tzinfo=UTC)

    @pytest.mark.parametrize(
        "value",
        [
            datetime(2026, 3, 1, 10, 0),  # noqa: DTZ001 - naive on purpose
            "2026-03-01T10:00:00",
        ],
    )
    def test_rejects_naive(self, instrument_kwargs: dict[str, Any], value: Any) -> None:
        with pytest.raises(ValidationError, match="naive datetime"):
            Instrument(**{**instrument_kwargs, "listed_at": value})

    @pytest.mark.parametrize("value", [1767225600, 1767225600000, 1767225600.5, "1767225600000"])
    def test_rejects_numeric_timestamps(
        self, instrument_kwargs: dict[str, Any], value: Any
    ) -> None:
        with pytest.raises(ValidationError, match="numeric timestamps"):
            Instrument(**{**instrument_kwargs, "listed_at": value})
