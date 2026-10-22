"""Regression tests for the second independent Phase 0 audit (reports/phase0/audyt2/).

K1-01: numeric epoch text without an integer part (".5", "+.5", "-.5") bypassed the epoch
ban. The fix replaces the deny-list with an allow-listed RFC 3339 profile (DEC-004), and
correction 2 also covers the related forms found while reproducing the finding. The DEC-020
split domain (user decision, docs/requirements/FAZA0_KOREKTA2_DECYZJE.md) is tested here too.

SYNTHETIC DATA: all values are invented for tests.
"""

import json
import random
import re
from datetime import UTC, datetime
from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.models import (
    Candle,
    Instrument,
    MarketEvent,
    MarketTick,
    Trade,
    VersionedContractModel,
)

RFC3339_PROFILE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?(Z|[+-][0-9]{2}:[0-9]{2})"
)


def _listed_at(instrument_kwargs: dict[str, Any], value: str, path: str) -> datetime | None:
    payload = {**instrument_kwargs, "listed_at": value}
    if path == "python":
        return Instrument.model_validate(payload).listed_at
    return Instrument.model_validate_json(json.dumps(payload)).listed_at


PATHS = ["python", "json"]

# ---------------------------------------------------------------- K1-01
K1_01_AUDIT_CASES = [".5", "+.5", "-.5"]
NUMERIC_VARIANTS = [
    ".5e3",
    ".5E+3",
    "-.5e-1",
    "+.5e0",
    "1e3",
    "+1",
    "-0",
    "5.",
    "1767225600",
    "1767225600000",
    "1767225600.5",
    " .5",
    "\t.5",
    ".5\n",
    "1767225600 ",
]


class TestK101NumericText:
    @pytest.mark.parametrize("path", PATHS)
    @pytest.mark.parametrize("value", K1_01_AUDIT_CASES)
    def test_audit_cases_rejected(
        self, instrument_kwargs: dict[str, Any], value: str, path: str
    ) -> None:
        with pytest.raises(ValidationError, match="numeric timestamps are not accepted"):
            _listed_at(instrument_kwargs, value, path)

    @pytest.mark.parametrize("path", PATHS)
    @pytest.mark.parametrize("value", NUMERIC_VARIANTS, ids=repr)
    def test_numeric_variants_rejected(
        self, instrument_kwargs: dict[str, Any], value: str, path: str
    ) -> None:
        with pytest.raises(ValidationError):
            _listed_at(instrument_kwargs, value, path)

    @pytest.mark.parametrize(
        ("fixture_name", "model", "field"),
        [
            ("tick_kwargs", MarketTick, "exchange_time"),
            ("tick_kwargs", MarketTick, "received_at"),
            ("trade_kwargs", Trade, "executed_at"),
            ("trade_kwargs", Trade, "received_at"),
            ("candle_kwargs", Candle, "start"),
            ("candle_kwargs", Candle, "end"),
            ("event_kwargs", MarketEvent, "detected_at"),
            ("event_kwargs", MarketEvent, "window_start"),
            ("event_kwargs", MarketEvent, "window_end"),
        ],
    )
    def test_every_timestamp_field_rejects_audit_case(
        self, request: pytest.FixtureRequest, fixture_name: str, model: type[Any], field: str
    ) -> None:
        kwargs = request.getfixturevalue(fixture_name)
        with pytest.raises(ValidationError, match="numeric timestamps"):
            model(**{**kwargs, field: ".5"})


# ---------------------------------------------------------------- RFC 3339 profile
OUTSIDE_PROFILE = [
    "2026-01-01 00:00:00+00:00",  # space instead of T
    "2026-01-01t00:00:00Z",  # lowercase t
    "2026-01-01T00:00:00z",  # lowercase z
    "2026-01-01T00:00:00+0100",  # offset without colon
    "2026-01-01T00:00:00+01",  # offset without minutes
    "2026-01-01T00:00Z",  # no seconds
    "2026-01-01T00:00:00.Z",  # empty fraction
    "2026-01-01T00:00:00.1234567Z",  # 7 fraction digits (would be truncated)
    "2026-01-01T00:00:00.123456789Z",  # nanoseconds (would be truncated)
    "2026-01-01T00:00:00,5Z",  # comma as decimal separator
    "2026-01-01T24:00:00Z",  # hour 24
    "2026-01-01T00:00:60Z",  # leap second (not representable)
    "2026-01-01T00:00:00+24:00",  # offset out of range
    "20260101T000000Z",  # ISO 8601 basic format
    "2026-W01-1T00:00:00Z",  # week date
    "2026-001T00:00:00Z",  # ordinal date
    "2026-01-01",  # date only
    "T12:00:00Z",  # time only
    " 2026-01-01T00:00:00Z",  # leading space
    "2026-01-01T00:00:00Z ",  # trailing space
    "2026-01-01T00:00:00Z\n",  # trailing newline
    "٢٠٢٦-01-01T00:00:00Z",  # non-ASCII digits
    "2026-02-30T00:00:00Z",  # invalid calendar date
    "now",
    "",
]
INSIDE_PROFILE = {
    "2026-01-01T00:00:00Z": datetime(2026, 1, 1, tzinfo=UTC),
    "2026-01-01T00:00:00.5Z": datetime(2026, 1, 1, 0, 0, 0, 500000, tzinfo=UTC),
    "2026-01-01T00:00:00.123456Z": datetime(2026, 1, 1, 0, 0, 0, 123456, tzinfo=UTC),
    "2026-01-01T01:00:00+01:00": datetime(2026, 1, 1, tzinfo=UTC),
    "2025-12-31T19:00:00-05:00": datetime(2026, 1, 1, tzinfo=UTC),
    "2026-01-01T23:59:00+23:59": datetime(2026, 1, 1, 0, 0, tzinfo=UTC),
    "2026-01-01T00:00:00-00:00": datetime(2026, 1, 1, tzinfo=UTC),
    "2024-02-29T12:00:00Z": datetime(2024, 2, 29, 12, tzinfo=UTC),
}


class TestRfc3339Profile:
    @pytest.mark.parametrize("path", PATHS)
    @pytest.mark.parametrize("value", OUTSIDE_PROFILE, ids=ascii)
    def test_text_outside_profile_rejected(
        self, instrument_kwargs: dict[str, Any], value: str, path: str
    ) -> None:
        with pytest.raises(ValidationError):
            _listed_at(instrument_kwargs, value, path)

    @pytest.mark.parametrize("path", PATHS)
    @pytest.mark.parametrize("value", list(INSIDE_PROFILE))
    def test_profile_accepted_and_normalized(
        self, instrument_kwargs: dict[str, Any], value: str, path: str
    ) -> None:
        listed = _listed_at(instrument_kwargs, value, path)
        assert listed == INSIDE_PROFILE[value]
        assert listed is not None
        assert listed.tzinfo is UTC

    @pytest.mark.parametrize("path", PATHS)
    def test_naive_text_reported_as_naive(
        self, instrument_kwargs: dict[str, Any], path: str
    ) -> None:
        with pytest.raises(ValidationError, match="naive datetime"):
            _listed_at(instrument_kwargs, "2026-01-01T00:00:00", path)

    def test_message_names_the_accepted_form(self, instrument_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match=r"YYYY-MM-DDTHH:MM:SS\[\.ffffff\]"):
            _listed_at(instrument_kwargs, "2026-01-01 00:00:00+00:00", "python")

    def test_contract_output_is_accepted_input(
        self,
        bybit_instrument: Instrument,
        tick_kwargs: dict[str, Any],
        candle_kwargs: dict[str, Any],
        trade_kwargs: dict[str, Any],
        event_kwargs: dict[str, Any],
    ) -> None:
        records: list[VersionedContractModel] = [
            bybit_instrument.replace(listed_at=datetime(2026, 1, 1, 0, 0, 0, 250000, tzinfo=UTC)),
            MarketTick(**tick_kwargs),
            Candle(**candle_kwargs),
            Trade(**trade_kwargs),
            MarketEvent(**event_kwargs),
        ]
        for record in records:
            text = record.model_dump_json()
            timestamps = re.findall(r'"(\d{4}-\d{2}-\d{2}T[^"]*)"', text)
            assert timestamps, type(record).__name__
            for stamp in timestamps:
                assert RFC3339_PROFILE.fullmatch(stamp), stamp
            assert type(record).model_validate_json(text) == record


# ---------------------------------------------------------------- DEC-020 split domain
def _fixed(value: Fraction, places: int) -> str:
    scaled = value * 10**places
    assert scaled.denominator == 1
    digits = str(scaled.numerator).rjust(places + 1, "0")
    return f"{digits[:-places]}.{digits[-places:]}"


class TestDec020ProductDomain:
    def test_audit_example_product_is_representable(self, trade_kwargs: dict[str, Any]) -> None:
        payload = {
            **trade_kwargs,
            "price": "0.0000000001",
            "quantity": "0.0000000001",
            "value_usdt": "0.00000000000000000001",
        }
        assert Trade(**payload).value_usdt == Decimal("1E-20")

    def test_product_with_36_places_accepted(self, trade_kwargs: dict[str, Any]) -> None:
        price = quantity = "0.000000000000000001"
        value = "0.000000000000000000000000000000000001"
        payload = {**trade_kwargs, "price": price, "quantity": quantity, "value_usdt": value}
        assert Trade(**payload).value_usdt == Decimal("1E-36")

    def test_value_with_37_places_rejected(self, trade_kwargs: dict[str, Any]) -> None:
        value = "100.0002" + "0" * 33  # equal to price * quantity, but 37 decimal places
        assert len(value.split(".")[1]) == 37
        payload = {**trade_kwargs, "value_usdt": value}
        with pytest.raises(ValidationError, match="at most 36 digits after the decimal point"):
            Trade(**payload)

    def test_value_magnitude_still_limited(self, trade_kwargs: dict[str, Any]) -> None:
        payload = {
            **trade_kwargs,
            "price": "10000000000",
            "quantity": "10000000000",
            "value_usdt": "100000000000000000000",
        }
        with pytest.raises(ValidationError, match=r"below 1E\+20"):
            Trade(**payload)

    @pytest.mark.parametrize("field", ["price", "quantity"])
    def test_factors_keep_18_places(self, trade_kwargs: dict[str, Any], field: str) -> None:
        with pytest.raises(ValidationError, match="at most 18 digits"):
            Trade(**{**trade_kwargs, field: "0.0000000000000000001"})

    def test_every_valid_factor_pair_has_representable_value(
        self, trade_kwargs: dict[str, Any]
    ) -> None:
        rng = random.Random(20261022 + 2)
        checked = 0
        while checked < 300:
            factors = []
            for _ in range(2):
                integer = str(rng.randint(0, 10 ** rng.randint(1, 9)))
                places = rng.randint(0, 18)
                fraction = "".join(rng.choice("0123456789") for _ in range(places))
                factors.append(f"{integer}.{fraction}" if places else integer)
            exact = Fraction(factors[0]) * Fraction(factors[1])
            if exact == 0 or exact >= 10**20:
                continue
            payload = {**trade_kwargs, "price": factors[0], "quantity": factors[1]}
            value = _fixed(exact, 36)
            assert Trade(**{**payload, "value_usdt": value}).value_usdt == Decimal(value)
            with pytest.raises(ValidationError, match="must equal price"):
                Trade(**{**payload, "value_usdt": _fixed(exact + Fraction(1, 10**36), 36)})
            checked += 1
