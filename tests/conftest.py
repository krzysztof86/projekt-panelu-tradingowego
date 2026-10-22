"""Shared test data.

SYNTHETIC DATA: every value below (prices, quantities, timestamps, identifiers) is
invented for tests and does not describe real market activity. Records that carry a
``source`` field use ``DataSource.SYNTHETIC``.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest

from market_intelligence.core.models import DataQuality, DataSource, Instrument

SYNTHETIC_T0 = datetime(2026, 1, 5, 12, 0, tzinfo=UTC)
"""Synthetic reference timestamp, aligned to every supported candle interval."""

SYNTHETIC_EVENT_ID = UUID("00000000-0000-4000-8000-000000000001")


def _instrument_kwargs(exchange: str) -> dict[str, Any]:
    return {
        "exchange": exchange,
        "symbol": "BTCUSDT",
        "market_type": "USDT_LINEAR_PERPETUAL",
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "status": "TRADING",
        "tick_size": "0.10",
    }


@pytest.fixture
def instrument_kwargs() -> dict[str, Any]:
    return _instrument_kwargs("BYBIT")


@pytest.fixture
def bybit_instrument() -> Instrument:
    return Instrument(**_instrument_kwargs("BYBIT"))


@pytest.fixture
def binance_instrument() -> Instrument:
    return Instrument(**_instrument_kwargs("BINANCE"))


@pytest.fixture
def valid_quality() -> DataQuality:
    return DataQuality.valid()


@pytest.fixture
def tick_kwargs(bybit_instrument: Instrument, valid_quality: DataQuality) -> dict[str, Any]:
    return {
        "instrument": bybit_instrument,
        "last_price": "50000.10",
        "exchange_time": SYNTHETIC_T0,
        "received_at": SYNTHETIC_T0 + timedelta(milliseconds=35),
        "source": DataSource.SYNTHETIC,
        "quality": valid_quality,
    }


@pytest.fixture
def candle_kwargs(bybit_instrument: Instrument, valid_quality: DataQuality) -> dict[str, Any]:
    return {
        "instrument": bybit_instrument,
        "interval": "1m",
        "start": SYNTHETIC_T0,
        "end": SYNTHETIC_T0 + timedelta(minutes=1),
        "open": "50000.00",
        "high": "50100.00",
        "low": "49900.00",
        "close": "50050.00",
        "turnover_usdt": "1250000.50",
        "is_closed": True,
        "source": DataSource.SYNTHETIC,
        "quality": valid_quality,
    }


@pytest.fixture
def trade_kwargs(bybit_instrument: Instrument, valid_quality: DataQuality) -> dict[str, Any]:
    return {
        "instrument": bybit_instrument,
        "trade_id": "synthetic-trade-0001",
        "price": "50000.10",
        "quantity": "0.002",
        "value_usdt": "100.00020",
        "aggressor_side": "BUY",
        "executed_at": SYNTHETIC_T0,
        "received_at": SYNTHETIC_T0 + timedelta(milliseconds=20),
        "source": DataSource.SYNTHETIC,
        "quality": valid_quality,
    }


@pytest.fixture
def event_kwargs(bybit_instrument: Instrument, valid_quality: DataQuality) -> dict[str, Any]:
    return {
        "event_id": SYNTHETIC_EVENT_ID,
        "instrument_id": bybit_instrument.instrument_id,
        "detector_id": "D1",
        "detector_version": "0.1.0",
        "config_version": "synthetic-cfg-1",
        "detected_at": SYNTHETIC_T0 + timedelta(seconds=60),
        "window_start": SYNTHETIC_T0,
        "window_end": SYNTHETIC_T0 + timedelta(seconds=60),
        "direction": "UP",
        "observed_values": [{"name": "price_change", "value": "1.25", "unit": "PERCENT"}],
        "reference_values": [{"name": "price_change", "value": "0.80", "unit": "PERCENT"}],
        "quality": valid_quality,
        "status": "CANDIDATE",
    }
