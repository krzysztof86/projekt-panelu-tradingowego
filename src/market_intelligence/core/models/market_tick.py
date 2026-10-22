"""Last traded price observation."""

from market_intelligence.core.models.base import VersionedContractModel
from market_intelligence.core.models.data_quality import DataQuality
from market_intelligence.core.models.enums import DataSource
from market_intelligence.core.models.instrument import Instrument
from market_intelligence.core.models.types import PositiveDecimal, UtcDatetime


class MarketTick(VersionedContractModel):
    """Last trade price of an instrument at a point in time.

    ``exchange_time`` is ``None`` when the exchange did not provide a timestamp; it is
    never substituted with ``received_at``. No ordering between the two timestamps is
    enforced because exchange and local clocks can drift; that is a quality concern.
    """

    instrument: Instrument
    last_price: PositiveDecimal
    exchange_time: UtcDatetime | None = None
    received_at: UtcDatetime
    source: DataSource
    quality: DataQuality
