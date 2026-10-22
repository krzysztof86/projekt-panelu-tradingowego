from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.models import Candle, CandleInterval

SYNTHETIC_DAY = datetime(2026, 1, 5, tzinfo=UTC)


def test_valid_candle(candle_kwargs: dict[str, Any]) -> None:
    candle = Candle(**candle_kwargs)
    assert candle.interval is CandleInterval.M1
    assert candle.turnover_usdt == Decimal("1250000.50")
    assert candle.is_closed is True


class TestOhlcConsistency:
    @pytest.mark.parametrize(
        ("overrides", "message"),
        [
            ({"high": "49999.00"}, "high must be greater"),  # high < open
            ({"high": "50040.00"}, "high must be greater"),  # high < close
            ({"low": "50001.00"}, "low must be less"),  # low > open
            ({"open": "50060.00", "close": "49950.00", "low": "49960.00"}, "low must be less"),
            ({"high": "49000.00", "low": "49500.00"}, "low must not be greater than high"),
        ],
    )
    def test_rejects_inconsistent(
        self, candle_kwargs: dict[str, Any], overrides: dict[str, str], message: str
    ) -> None:
        with pytest.raises(ValidationError, match=message):
            Candle(**{**candle_kwargs, **overrides})

    def test_flat_candle_is_valid(self, candle_kwargs: dict[str, Any]) -> None:
        flat = dict.fromkeys(("open", "high", "low", "close"), "50000.00")
        candle = Candle(**{**candle_kwargs, **flat, "turnover_usdt": "0"})
        assert candle.high == candle.low

    @pytest.mark.parametrize("field", ["open", "high", "low", "close"])
    @pytest.mark.parametrize("value", ["0", "-1", "NaN", "Infinity"])
    def test_rejects_non_positive_or_non_finite_prices(
        self, candle_kwargs: dict[str, Any], field: str, value: str
    ) -> None:
        with pytest.raises(ValidationError):
            Candle(**{**candle_kwargs, field: value})


class TestTurnover:
    def test_zero_is_valid(self, candle_kwargs: dict[str, Any]) -> None:
        assert Candle(**{**candle_kwargs, "turnover_usdt": "0"}).turnover_usdt == 0

    def test_negative_is_rejected(self, candle_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="must not be negative"):
            Candle(**{**candle_kwargs, "turnover_usdt": "-0.01"})

    def test_missing_is_not_zero(self, candle_kwargs: dict[str, Any]) -> None:
        del candle_kwargs["turnover_usdt"]
        with pytest.raises(ValidationError):
            Candle(**candle_kwargs)

    def test_none_is_not_zero(self, candle_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError):
            Candle(**{**candle_kwargs, "turnover_usdt": None})


class TestInterval:
    @pytest.mark.parametrize("interval", list(CandleInterval))
    def test_every_interval_aligned_on_day_boundary(
        self, candle_kwargs: dict[str, Any], interval: CandleInterval
    ) -> None:
        candle = Candle(
            **{
                **candle_kwargs,
                "interval": interval,
                "start": SYNTHETIC_DAY,
                "end": SYNTHETIC_DAY + interval.duration,
            }
        )
        assert candle.end - candle.start == interval.duration

    def test_rejects_wrong_length(self, candle_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="must equal the interval"):
            Candle(**{**candle_kwargs, "end": candle_kwargs["start"] + timedelta(minutes=5)})

    def test_rejects_end_before_start(self, candle_kwargs: dict[str, Any]) -> None:
        start = candle_kwargs["start"]
        with pytest.raises(ValidationError):
            Candle(**{**candle_kwargs, "start": start, "end": start - timedelta(minutes=1)})

    def test_rejects_zero_length(self, candle_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError):
            Candle(**{**candle_kwargs, "end": candle_kwargs["start"]})

    def test_rejects_misaligned_start(self, candle_kwargs: dict[str, Any]) -> None:
        start = candle_kwargs["start"] + timedelta(seconds=30)
        with pytest.raises(ValidationError, match="not aligned"):
            Candle(**{**candle_kwargs, "start": start, "end": start + timedelta(minutes=1)})

    @pytest.mark.parametrize("field", ["start", "end"])
    def test_rejects_naive_bounds(self, candle_kwargs: dict[str, Any], field: str) -> None:
        naive = candle_kwargs[field].replace(tzinfo=None)
        with pytest.raises(ValidationError, match="naive datetime"):
            Candle(**{**candle_kwargs, field: naive})

    def test_rejects_unsupported_interval(self, candle_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError):
            Candle(**{**candle_kwargs, "interval": "1M"})


class TestHalfOpenInterval:
    def test_start_is_inclusive_end_is_exclusive(self, candle_kwargs: dict[str, Any]) -> None:
        candle = Candle(**candle_kwargs)
        assert candle.contains(candle.start)
        assert candle.contains(candle.end - timedelta(microseconds=1))
        assert not candle.contains(candle.end)
        assert not candle.contains(candle.start - timedelta(microseconds=1))

    def test_consecutive_candles_do_not_overlap(self, candle_kwargs: dict[str, Any]) -> None:
        first = Candle(**candle_kwargs)
        second = Candle(
            **{**candle_kwargs, "start": first.end, "end": first.end + timedelta(minutes=1)}
        )
        boundary = first.end
        assert not first.contains(boundary)
        assert second.contains(boundary)

    def test_contains_rejects_naive(self, candle_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValueError, match="naive datetime"):
            Candle(**candle_kwargs).contains(datetime(2026, 1, 5, 12, 0))  # noqa: DTZ001


class TestClosedFlag:
    def test_open_candle(self, candle_kwargs: dict[str, Any]) -> None:
        assert Candle(**{**candle_kwargs, "is_closed": False}).is_closed is False

    @pytest.mark.parametrize("value", ["true", 1, "yes", None])
    def test_requires_strict_bool(self, candle_kwargs: dict[str, Any], value: Any) -> None:
        with pytest.raises(ValidationError):
            Candle(**{**candle_kwargs, "is_closed": value})
