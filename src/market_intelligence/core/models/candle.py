"""OHLC candle over a half-open time interval."""

from datetime import datetime
from typing import Self

from pydantic import StrictBool, model_validator

from market_intelligence.core.clock import UTC_EPOCH, ensure_utc
from market_intelligence.core.models.base import VersionedContractModel
from market_intelligence.core.models.data_quality import DataQuality
from market_intelligence.core.models.enums import CandleInterval, DataSource
from market_intelligence.core.models.instrument import Instrument
from market_intelligence.core.models.types import (
    NonNegativeDecimal,
    PositiveDecimal,
    UtcDatetime,
)


class Candle(VersionedContractModel):
    """OHLC candle covering ``[start, end)``.

    ``end`` is exclusive and equals the next candle's ``start``. ``start`` must be
    aligned to a multiple of the interval since the Unix epoch (DEC-007).
    ``turnover_usdt`` is the traded value in USDT; zero means no trading, while missing
    turnover is not representable (the field is required).
    """

    instrument: Instrument
    interval: CandleInterval
    start: UtcDatetime
    end: UtcDatetime
    open: PositiveDecimal
    high: PositiveDecimal
    low: PositiveDecimal
    close: PositiveDecimal
    turnover_usdt: NonNegativeDecimal
    is_closed: StrictBool
    source: DataSource
    quality: DataQuality

    @model_validator(mode="after")
    def _check_interval(self) -> Self:
        duration = self.interval.duration
        if self.end - self.start != duration:
            raise ValueError(f"end - start must equal the interval {self.interval} ({duration})")
        if (self.start - UTC_EPOCH) % duration:
            raise ValueError(f"start is not aligned to the {self.interval} interval")
        return self

    @model_validator(mode="after")
    def _check_ohlc(self) -> Self:
        if self.low > self.high:
            raise ValueError("low must not be greater than high")
        if self.high < max(self.open, self.close):
            raise ValueError("high must be greater than or equal to open and close")
        if self.low > min(self.open, self.close):
            raise ValueError("low must be less than or equal to open and close")
        return self

    def contains(self, moment: datetime) -> bool:
        """Return whether ``moment`` falls inside ``[start, end)``."""
        return self.start <= ensure_utc(moment) < self.end
