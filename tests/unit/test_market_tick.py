from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.models import DataQualityStatus, DataSource, MarketTick


def test_valid_tick(tick_kwargs: dict[str, Any]) -> None:
    tick = MarketTick(**tick_kwargs)
    assert tick.last_price == Decimal("50000.10")
    assert tick.source is DataSource.SYNTHETIC
    assert tick.quality.status is DataQualityStatus.VALID


def test_exchange_time_is_optional(tick_kwargs: dict[str, Any]) -> None:
    del tick_kwargs["exchange_time"]
    tick = MarketTick(**tick_kwargs)
    assert tick.exchange_time is None
    assert tick.received_at is not None


def test_exchange_time_explicit_none(tick_kwargs: dict[str, Any]) -> None:
    assert MarketTick(**{**tick_kwargs, "exchange_time": None}).exchange_time is None


def test_received_at_is_required(tick_kwargs: dict[str, Any]) -> None:
    del tick_kwargs["received_at"]
    with pytest.raises(ValidationError):
        MarketTick(**tick_kwargs)


def test_timestamps_normalized_to_utc(tick_kwargs: dict[str, Any]) -> None:
    offset = timezone(timedelta(hours=-5))
    local = datetime(2026, 1, 5, 7, 0, tzinfo=offset)
    tick = MarketTick(**{**tick_kwargs, "exchange_time": local, "received_at": local})
    assert tick.exchange_time == datetime(2026, 1, 5, 12, 0, tzinfo=UTC)
    assert tick.received_at.tzinfo is UTC


@pytest.mark.parametrize("field", ["exchange_time", "received_at"])
def test_rejects_naive_timestamps(tick_kwargs: dict[str, Any], field: str) -> None:
    naive = datetime(2026, 1, 5, 12, 0)  # noqa: DTZ001 - naive on purpose
    with pytest.raises(ValidationError, match="naive datetime"):
        MarketTick(**{**tick_kwargs, field: naive})


@pytest.mark.parametrize("price", ["0", "-50000", "NaN", "Infinity", 50000.1, None])
def test_rejects_invalid_price(tick_kwargs: dict[str, Any], price: Any) -> None:
    with pytest.raises(ValidationError):
        MarketTick(**{**tick_kwargs, "last_price": price})


def test_rejects_unknown_source(tick_kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        MarketTick(**{**tick_kwargs, "source": "SCRAPER"})
