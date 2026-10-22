from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.models import AggressorSide, Trade


def test_valid_trade(trade_kwargs: dict[str, Any]) -> None:
    trade = Trade(**trade_kwargs)
    assert trade.value_usdt == trade.price * trade.quantity
    assert trade.trade_id == "synthetic-trade-0001"


@pytest.mark.parametrize("side", [AggressorSide.BUY, AggressorSide.SELL])
def test_aggressor_side(trade_kwargs: dict[str, Any], side: AggressorSide) -> None:
    assert Trade(**{**trade_kwargs, "aggressor_side": side.value}).aggressor_side is side


@pytest.mark.parametrize("side", ["Buy", "buy", "Sell", "BID", "ASK", "", None, True])
def test_rejects_non_canonical_side(trade_kwargs: dict[str, Any], side: Any) -> None:
    with pytest.raises(ValidationError):
        Trade(**{**trade_kwargs, "aggressor_side": side})


class TestValue:
    def test_rejects_value_mismatch(self, trade_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="must equal price"):
            Trade(**{**trade_kwargs, "value_usdt": "100.00"})

    def test_equivalent_decimal_representation_accepted(self, trade_kwargs: dict[str, Any]) -> None:
        trade = Trade(**{**trade_kwargs, "value_usdt": "100.0002000"})
        assert trade.value_usdt == Decimal("100.0002")

    def test_high_precision_product_is_exact(self, trade_kwargs: dict[str, Any]) -> None:
        # The exact product has 38 significant digits (the domain maximum); the default
        # Decimal context (28 digits) would round it, so this checks that no rounding happens.
        price, quantity = "1234567890.123456789", "9876543210.987654321"
        value = "12193263113702179522.374638011112635269"
        trade = Trade(**{**trade_kwargs, "price": price, "quantity": quantity, "value_usdt": value})
        assert trade.value_usdt == Decimal(value)


@pytest.mark.parametrize("field", ["price", "quantity", "value_usdt"])
@pytest.mark.parametrize("value", ["0", "-0.002", "NaN", "-Infinity", 0.002])
def test_rejects_invalid_amounts(trade_kwargs: dict[str, Any], field: str, value: Any) -> None:
    with pytest.raises(ValidationError):
        Trade(**{**trade_kwargs, field: value})


@pytest.mark.parametrize("trade_id", ["", " ", "id with space", "x" * 129])
def test_rejects_invalid_trade_id(trade_kwargs: dict[str, Any], trade_id: str) -> None:
    with pytest.raises(ValidationError):
        Trade(**{**trade_kwargs, "trade_id": trade_id})


def test_numeric_trade_id_must_be_string(trade_kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        Trade(**{**trade_kwargs, "trade_id": 123456})


@pytest.mark.parametrize("field", ["executed_at", "received_at"])
def test_rejects_naive_timestamps(trade_kwargs: dict[str, Any], field: str) -> None:
    naive = datetime(2026, 1, 5, 12, 0)  # noqa: DTZ001 - naive on purpose
    with pytest.raises(ValidationError, match="naive datetime"):
        Trade(**{**trade_kwargs, field: naive})


def test_executed_at_is_required(trade_kwargs: dict[str, Any]) -> None:
    del trade_kwargs["executed_at"]
    with pytest.raises(ValidationError):
        Trade(**trade_kwargs)
