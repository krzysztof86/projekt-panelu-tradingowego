"""Enumerations used by data contracts.

Values are upper-case internal identifiers. Exchange-specific spellings (e.g. Bybit
``"Buy"`` or Binance ``"PENDING_TRADING"``) are not accepted here; mapping them is the
responsibility of the planned exchange connectors.
"""

from datetime import timedelta
from enum import StrEnum


class Exchange(StrEnum):
    BYBIT = "BYBIT"
    BINANCE = "BINANCE"


class MarketType(StrEnum):
    """Only USDT-margined linear perpetual contracts are in scope (no Spot, no COIN-M)."""

    USDT_LINEAR_PERPETUAL = "USDT_LINEAR_PERPETUAL"


class ContractStatus(StrEnum):
    """Normalized contract trading status (exchange mapping is PROPOSED, DEC-012)."""

    PRE_LAUNCH = "PRE_LAUNCH"
    TRADING = "TRADING"
    SETTLING = "SETTLING"
    CLOSED = "CLOSED"


class DataSource(StrEnum):
    """Origin of a record."""

    REST = "REST"
    """Exchange public REST API."""
    WEBSOCKET = "WEBSOCKET"
    """Exchange public WebSocket stream."""
    REPLAY = "REPLAY"
    """Read back from locally stored history."""
    SYNTHETIC = "SYNTHETIC"
    """Generated test data; never real market data."""


class DataQualityStatus(StrEnum):
    VALID = "VALID"
    WARMUP = "WARMUP"
    STALE = "STALE"
    GAP = "GAP"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INVALID = "INVALID"


class AggressorSide(StrEnum):
    """Side of the taker (aggressor) order of a trade."""

    BUY = "BUY"
    SELL = "SELL"


class CandleInterval(StrEnum):
    """Fixed-length candle intervals available on both Bybit V5 and Binance USDⓈ-M."""

    M1 = "1m"
    M3 = "3m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H2 = "2h"
    H4 = "4h"
    H6 = "6h"
    H12 = "12h"
    D1 = "1d"

    @property
    def duration(self) -> timedelta:
        return _INTERVAL_DURATIONS[self]


_INTERVAL_DURATIONS: dict[CandleInterval, timedelta] = {
    CandleInterval.M1: timedelta(minutes=1),
    CandleInterval.M3: timedelta(minutes=3),
    CandleInterval.M5: timedelta(minutes=5),
    CandleInterval.M15: timedelta(minutes=15),
    CandleInterval.M30: timedelta(minutes=30),
    CandleInterval.H1: timedelta(hours=1),
    CandleInterval.H2: timedelta(hours=2),
    CandleInterval.H4: timedelta(hours=4),
    CandleInterval.H6: timedelta(hours=6),
    CandleInterval.H12: timedelta(hours=12),
    CandleInterval.D1: timedelta(days=1),
}


class DetectorId(StrEnum):
    D1 = "D1"
    """Price Velocity Detector (PLANNED)."""
    D2 = "D2"
    """Relative Volume Detector (PLANNED)."""
    D3 = "D3"
    """Delta/Price Divergence Detector (PLANNED)."""


class EventDirection(StrEnum):
    UP = "UP"
    DOWN = "DOWN"
    NON_DIRECTIONAL = "NON_DIRECTIONAL"


class EventStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    ANALYZING = "ANALYZING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
