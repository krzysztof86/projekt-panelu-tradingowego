"""JSON round-trip, Decimal precision and schema versioning of all contracts."""

import json
from decimal import Decimal
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from market_intelligence.core.models import (
    SCHEMA_VERSION,
    Candle,
    DataQuality,
    Instrument,
    MarketEvent,
    MarketTick,
    MetricValue,
    Trade,
    VersionedContractModel,
)

VERSIONED_MODELS: list[type[VersionedContractModel]] = [
    Instrument,
    MarketTick,
    Candle,
    Trade,
    MarketEvent,
]


@pytest.fixture
def samples(
    bybit_instrument: Instrument,
    tick_kwargs: dict[str, Any],
    candle_kwargs: dict[str, Any],
    trade_kwargs: dict[str, Any],
    event_kwargs: dict[str, Any],
) -> list[BaseModel]:
    return [
        bybit_instrument,
        MarketTick(**tick_kwargs),
        MarketTick(**{**tick_kwargs, "exchange_time": None}),
        Candle(**candle_kwargs),
        Trade(**trade_kwargs),
        MarketEvent(**event_kwargs),
        DataQuality(status="GAP", reason="synthetic gap"),
        MetricValue(name="ratio", value="3.75", unit="RATIO"),
    ]


def test_json_round_trip(samples: list[BaseModel]) -> None:
    for sample in samples:
        restored = type(sample).model_validate_json(sample.model_dump_json())
        assert restored == sample, type(sample).__name__


@pytest.mark.parametrize(
    "value",
    ["0.00000001", "50000.10", "1E-12", "123456789012345678901234567890.123456789", "0.10"],
)
def test_decimal_survives_json_exactly(instrument_kwargs: dict[str, Any], value: str) -> None:
    instrument = Instrument(**{**instrument_kwargs, "tick_size": value})
    payload = instrument.model_dump_json()
    assert isinstance(json.loads(payload)["tick_size"], str), "Decimal must be a JSON string"
    restored = Instrument.model_validate_json(payload)
    assert restored.tick_size.as_tuple() == Decimal(value).as_tuple()


def test_trade_value_precision_survives_json(trade_kwargs: dict[str, Any]) -> None:
    trade = Trade(**trade_kwargs)
    data = json.loads(trade.model_dump_json())
    assert data["price"] == "50000.10"
    assert data["quantity"] == "0.002"
    assert data["value_usdt"] == "100.00020"


def test_datetimes_serialized_as_utc(candle_kwargs: dict[str, Any]) -> None:
    data = json.loads(Candle(**candle_kwargs).model_dump_json())
    assert data["start"] == "2026-01-05T12:00:00Z"
    assert data["end"] == "2026-01-05T12:01:00Z"


def test_missing_exchange_time_serialized_as_null(tick_kwargs: dict[str, Any]) -> None:
    data = json.loads(MarketTick(**{**tick_kwargs, "exchange_time": None}).model_dump_json())
    assert data["exchange_time"] is None


def test_enums_serialized_as_values(trade_kwargs: dict[str, Any]) -> None:
    data = json.loads(Trade(**trade_kwargs).model_dump_json())
    assert data["aggressor_side"] == "BUY"
    assert data["source"] == "SYNTHETIC"
    assert data["instrument"]["exchange"] == "BYBIT"


def test_market_event_metrics_round_trip_as_tuples(event_kwargs: dict[str, Any]) -> None:
    event = MarketEvent(**event_kwargs)
    restored = MarketEvent.model_validate_json(event.model_dump_json())
    assert isinstance(restored.observed_values, tuple)
    assert restored.observed_values[0].value.as_tuple() == Decimal("1.25").as_tuple()


class TestSchemaVersion:
    def test_current_version(self) -> None:
        assert SCHEMA_VERSION == 1

    def test_present_in_every_record(self, samples: list[BaseModel]) -> None:
        for sample in samples:
            if isinstance(sample, VersionedContractModel):
                assert json.loads(sample.model_dump_json())["schema_version"] == SCHEMA_VERSION

    @pytest.mark.parametrize("version", [0, 2, "1", None])
    def test_other_versions_rejected(self, bybit_instrument: Instrument, version: Any) -> None:
        data = json.loads(bybit_instrument.model_dump_json())
        data["schema_version"] = version
        with pytest.raises(ValidationError):
            Instrument.model_validate_json(json.dumps(data))

    @pytest.mark.parametrize("model", VERSIONED_MODELS)
    def test_json_schema_declares_version(self, model: type[VersionedContractModel]) -> None:
        schema = model.model_json_schema()
        assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
        assert schema["additionalProperties"] is False
