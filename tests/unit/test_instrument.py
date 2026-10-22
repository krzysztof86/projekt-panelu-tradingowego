from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.models import (
    ContractStatus,
    Exchange,
    Instrument,
    MarketType,
)


class TestValidInstruments:
    def test_bybit(self, bybit_instrument: Instrument) -> None:
        assert bybit_instrument.exchange is Exchange.BYBIT
        assert bybit_instrument.market_type is MarketType.USDT_LINEAR_PERPETUAL
        assert bybit_instrument.status is ContractStatus.TRADING
        assert bybit_instrument.instrument_id == "BYBIT:USDT_LINEAR_PERPETUAL:BTCUSDT"
        assert bybit_instrument.listed_at is None

    def test_binance(self, binance_instrument: Instrument) -> None:
        assert binance_instrument.exchange is Exchange.BINANCE
        assert binance_instrument.instrument_id == "BINANCE:USDT_LINEAR_PERPETUAL:BTCUSDT"

    @pytest.mark.parametrize("status", list(ContractStatus))
    def test_all_statuses(self, instrument_kwargs: dict[str, Any], status: ContractStatus) -> None:
        assert Instrument(**{**instrument_kwargs, "status": status}).status is status


class TestIdentity:
    def test_same_symbol_on_different_exchanges_is_different(
        self, bybit_instrument: Instrument, binance_instrument: Instrument
    ) -> None:
        assert bybit_instrument.symbol == binance_instrument.symbol
        assert bybit_instrument != binance_instrument
        assert bybit_instrument.instrument_id != binance_instrument.instrument_id
        assert len({bybit_instrument, binance_instrument}) == 2

    def test_equal_definitions_are_equal(self, instrument_kwargs: dict[str, Any]) -> None:
        assert Instrument(**instrument_kwargs) == Instrument(**instrument_kwargs)

    @pytest.mark.parametrize("symbol", ["1000PEPEUSDT", "btcusdt", "SHIB1000USDT", "币安人生USDT"])
    def test_symbol_preserved_verbatim(
        self, instrument_kwargs: dict[str, Any], symbol: str
    ) -> None:
        assert Instrument(**{**instrument_kwargs, "symbol": symbol}).symbol == symbol

    @pytest.mark.parametrize(
        "symbol", ["", " BTCUSDT", "BTCUSDT ", "BTC USDT", "BTC:USDT", "X" * 65]
    )
    def test_invalid_symbol(self, instrument_kwargs: dict[str, Any], symbol: str) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, "symbol": symbol})


class TestScope:
    @pytest.mark.parametrize(
        "market_type",
        ["SPOT", "COIN_M_PERPETUAL", "INVERSE_PERPETUAL", "USDC_LINEAR_PERPETUAL", "linear", ""],
    )
    def test_rejects_other_market_types(
        self, instrument_kwargs: dict[str, Any], market_type: str
    ) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, "market_type": market_type})

    @pytest.mark.parametrize("quote", ["USDC", "BUSD", "USD", "usdt", "BTC", ""])
    def test_rejects_other_quote_assets(
        self, instrument_kwargs: dict[str, Any], quote: str
    ) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, "quote_asset": quote})

    @pytest.mark.parametrize("exchange", ["OKX", "bybit", "Binance", ""])
    def test_rejects_unknown_exchange(
        self, instrument_kwargs: dict[str, Any], exchange: str
    ) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, "exchange": exchange})

    @pytest.mark.parametrize("status", ["Trading", "PENDING_TRADING", "UNKNOWN"])
    def test_rejects_exchange_native_status(
        self, instrument_kwargs: dict[str, Any], status: str
    ) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, "status": status})


class TestTickSize:
    @pytest.mark.parametrize("tick_size", ["0", "-0.1", "-1"])
    def test_rejects_non_positive(self, instrument_kwargs: dict[str, Any], tick_size: str) -> None:
        with pytest.raises(ValidationError, match="greater than zero"):
            Instrument(**{**instrument_kwargs, "tick_size": tick_size})

    def test_required(self, instrument_kwargs: dict[str, Any]) -> None:
        del instrument_kwargs["tick_size"]
        with pytest.raises(ValidationError):
            Instrument(**instrument_kwargs)


class TestImmutability:
    def test_frozen(self, bybit_instrument: Instrument) -> None:
        with pytest.raises(ValidationError):
            bybit_instrument.symbol = "ETHUSDT"  # type: ignore[misc]

    def test_extra_fields_forbidden(self, instrument_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, "leverage": "100"})
