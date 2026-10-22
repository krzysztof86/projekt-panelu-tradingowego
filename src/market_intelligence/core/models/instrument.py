"""Tradable instrument definition."""

from typing import Annotated, Literal

from pydantic import Field

from market_intelligence.core.models.base import VersionedContractModel
from market_intelligence.core.models.enums import ContractStatus, Exchange, MarketType
from market_intelligence.core.models.types import (
    AssetCode,
    ExchangeSymbol,
    PositiveDecimal,
    UtcDatetime,
)

_EXCHANGES = "|".join(exchange.value for exchange in Exchange)
_MARKET_TYPES = "|".join(market_type.value for market_type in MarketType)

InstrumentId = Annotated[
    str, Field(pattern=rf"^(?:{_EXCHANGES}):(?:{_MARKET_TYPES}):[^\s:]{{1,64}}$")
]
"""Canonical instrument identifier ``<EXCHANGE>:<MARKET_TYPE>:<SYMBOL>`` (DEC-006)."""


class Instrument(VersionedContractModel):
    """A USDT linear perpetual contract on a single exchange.

    Identity is the triple (exchange, market_type, symbol): the same symbol on two
    exchanges is two different instruments. ``symbol`` is kept exactly as the exchange
    reports it.
    """

    exchange: Exchange
    symbol: ExchangeSymbol
    market_type: MarketType
    base_asset: AssetCode
    quote_asset: Literal["USDT"]
    status: ContractStatus
    tick_size: PositiveDecimal
    listed_at: UtcDatetime | None = None

    @property
    def instrument_id(self) -> str:
        return f"{self.exchange}:{self.market_type}:{self.symbol}"
