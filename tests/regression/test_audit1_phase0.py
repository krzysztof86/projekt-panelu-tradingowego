"""Regression tests for the first independent Phase 0 audit (reports/phase0/audyt1/).

Each class maps to one audit finding (A-01 ... A-07) or to a related gap found while
reproducing the audit (E-1 ... E-4, see reports/phase0/korekta1/KOREKTA1_RAPORT.md).

SYNTHETIC DATA: all values are invented for tests.
"""

import copy
import json
import random
from collections.abc import Callable
from datetime import date, time
from decimal import (
    ROUND_05UP,
    ROUND_FLOOR,
    ROUND_UP,
    Clamped,
    Context,
    Decimal,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Subnormal,
    Underflow,
    getcontext,
    localcontext,
)
from fractions import Fraction
from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.models import (
    SCHEMA_VERSION,
    Candle,
    DataQuality,
    DataQualityStatus,
    Instrument,
    MarketEvent,
    MarketTick,
    MetricValue,
    Trade,
    VersionedContractModel,
)

P_101_PLACES = "1." + "0" * 99 + "1"
"""Audit A-01 probe: 101 digits after the decimal point."""

MAX_PRICE, MAX_QUANTITY = "1234567890.123456789", "9876543210.987654321"
MAX_VALUE = "12193263113702179522.374638011112635269"
"""Exact product with 38 significant digits and 18 decimal places (domain maximum)."""

ALL_SIGNALS = [
    Clamped,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Subnormal,
    Underflow,
]
HOSTILE_CONTEXTS: dict[str, Callable[[], Context]] = {
    "prec_1": lambda: Context(prec=1),
    "prec_5_round_up": lambda: Context(prec=5, rounding=ROUND_UP),
    "prec_3_round_floor": lambda: Context(prec=3, rounding=ROUND_FLOOR),
    "trap_inexact_rounded": lambda: Context(traps=[Inexact, Rounded]),
    "small_exponent_range": lambda: Context(Emax=3, Emin=-3),
    "all_traps_round_05up": lambda: Context(prec=28, rounding=ROUND_05UP, traps=ALL_SIGNALS),
}


def _fixed_18(value: Fraction) -> str:
    """Format a fraction whose denominator divides 10**18 with exactly 18 decimal places."""
    scaled = value * 10**18
    assert scaled.denominator == 1
    digits = str(abs(scaled.numerator)).rjust(19, "0")
    sign = "-" if scaled < 0 else ""
    return f"{sign}{digits[:-18]}.{digits[-18:]}"


def _random_amount(rng: random.Random) -> str:
    integer = str(rng.randint(1, 10 ** rng.randint(1, 10) - 1))
    places = rng.randint(0, 9)
    fraction = "".join(rng.choice("0123456789") for _ in range(places))
    return f"{integer}.{fraction}" if places else integer


# ---------------------------------------------------------------- A-01
class TestA01FinancialDomain:
    def test_audit_rounded_value_rejected(self, trade_kwargs: dict[str, Any]) -> None:
        payload = {**trade_kwargs, "price": P_101_PLACES, "quantity": "1", "value_usdt": "1"}
        with pytest.raises(ValidationError, match="at most 18 digits after the decimal point"):
            Trade(**payload)

    def test_audit_exact_value_rejected_by_explicit_domain(
        self, trade_kwargs: dict[str, Any]
    ) -> None:
        payload = {**trade_kwargs, "price": P_101_PLACES, "quantity": "1"}
        with pytest.raises(ValidationError, match="at most 18 digits after the decimal point"):
            Trade(**{**payload, "value_usdt": P_101_PLACES})

    def test_audit_huge_exponent_is_validation_error(self, trade_kwargs: dict[str, Any]) -> None:
        payload = {
            **trade_kwargs,
            "price": "1e999999",
            "quantity": "10",
            "value_usdt": "1e1000000",
        }
        with pytest.raises(ValidationError, match=r"below 1E\+20"):
            Trade(**payload)

    @pytest.mark.parametrize(
        "value",
        [
            "0.000000000000000001",
            "99999999999999999999.999999999999999999",
            "1E+19",
            "123.450000000000000000",
        ],
    )
    def test_domain_boundaries_accepted(
        self, instrument_kwargs: dict[str, Any], value: str
    ) -> None:
        tick = Instrument(**{**instrument_kwargs, "tick_size": value}).tick_size
        assert tick.as_tuple() == Decimal(value).as_tuple()

    @pytest.mark.parametrize(
        ("value", "message"),
        [
            ("0.0000000000000000001", "at most 18 digits"),
            ("1.0000000000000000000", "at most 18 digits"),
            ("1E-19", "at most 18 digits"),
            ("100000000000000000000", r"below 1E\+20"),
            ("1E+20", r"below 1E\+20"),
        ],
    )
    def test_domain_violations_rejected(
        self, instrument_kwargs: dict[str, Any], value: str, message: str
    ) -> None:
        with pytest.raises(ValidationError, match=message):
            Instrument(**{**instrument_kwargs, "tick_size": value})

    def test_zero_with_excess_places_rejected(self, candle_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="at most 18 digits"):
            Candle(**{**candle_kwargs, "turnover_usdt": "0.0000000000000000000"})

    @pytest.mark.parametrize(
        "value", ["-99999999999999999999.999999999999999999", "-0.000000000000000001"]
    )
    def test_negative_metric_boundaries_accepted(self, value: str) -> None:
        assert MetricValue(name="delta", value=value, unit="USDT").value == Decimal(value)

    @pytest.mark.parametrize("value", ["-1E+20", "-0.0000000000000000001"])
    def test_negative_metric_violations_rejected(self, value: str) -> None:
        with pytest.raises(ValidationError):
            MetricValue(name="delta", value=value, unit="USDT")


class TestA01ExactProduct:
    def test_maximum_precision_product_accepted(self, trade_kwargs: dict[str, Any]) -> None:
        payload = {**trade_kwargs, "price": MAX_PRICE, "quantity": MAX_QUANTITY}
        assert Trade(**{**payload, "value_usdt": MAX_VALUE}).value_usdt == Decimal(MAX_VALUE)

    def test_default_context_rounded_product_rejected(self, trade_kwargs: dict[str, Any]) -> None:
        with localcontext(Context(prec=28)):
            rounded = str(Decimal(MAX_PRICE) * Decimal(MAX_QUANTITY))
        assert Decimal(rounded) != Decimal(MAX_VALUE)
        payload = {**trade_kwargs, "price": MAX_PRICE, "quantity": MAX_QUANTITY}
        with pytest.raises(ValidationError, match="must equal price"):
            Trade(**{**payload, "value_usdt": rounded})

    @pytest.mark.parametrize("context_name", list(HOSTILE_CONTEXTS))
    def test_exact_value_accepted_under_any_context(
        self, trade_kwargs: dict[str, Any], context_name: str
    ) -> None:
        payload = {
            **trade_kwargs,
            "price": MAX_PRICE,
            "quantity": MAX_QUANTITY,
            "value_usdt": MAX_VALUE,
        }
        with localcontext(HOSTILE_CONTEXTS[context_name]()):
            trade = Trade(**payload)
        assert trade.value_usdt == Decimal(MAX_VALUE)

    @pytest.mark.parametrize("context_name", list(HOSTILE_CONTEXTS))
    @pytest.mark.parametrize("delta", ["0.000000000000000001", "-0.000000000000000001"])
    def test_one_unit_off_rejected_under_any_context(
        self, trade_kwargs: dict[str, Any], context_name: str, delta: str
    ) -> None:
        wrong = _fixed_18(Fraction(MAX_VALUE) + Fraction(delta))
        payload = {**trade_kwargs, "price": MAX_PRICE, "quantity": MAX_QUANTITY}
        with localcontext(HOSTILE_CONTEXTS[context_name]()), pytest.raises(ValidationError):
            Trade(**{**payload, "value_usdt": wrong})

    @pytest.mark.parametrize("context_name", list(HOSTILE_CONTEXTS))
    def test_audit_probes_raise_only_validation_errors(
        self, trade_kwargs: dict[str, Any], context_name: str
    ) -> None:
        probes = [
            {"price": P_101_PLACES, "quantity": "1", "value_usdt": "1"},
            {"price": P_101_PLACES, "quantity": "1", "value_usdt": P_101_PLACES},
            {"price": "1e999999", "quantity": "10", "value_usdt": "1e1000000"},
        ]
        for probe in probes:
            with localcontext(HOSTILE_CONTEXTS[context_name]()), pytest.raises(ValidationError):
                Trade(**{**trade_kwargs, **probe})

    def test_caller_context_is_not_modified(self, trade_kwargs: dict[str, Any]) -> None:
        payload = {
            **trade_kwargs,
            "price": MAX_PRICE,
            "quantity": MAX_QUANTITY,
            "value_usdt": MAX_VALUE,
        }
        with localcontext(Context(prec=7, rounding=ROUND_UP)) as caller:
            Trade(**payload)
            assert caller.prec == 7
            assert caller.rounding == ROUND_UP
            assert not any(caller.flags.values())
        assert getcontext().prec == 28

    def test_generated_cases_match_rational_oracle(self, trade_kwargs: dict[str, Any]) -> None:
        rng = random.Random(20261022)
        for _ in range(300):
            price, quantity = _random_amount(rng), _random_amount(rng)
            exact = Fraction(price) * Fraction(quantity)
            if exact >= 10**20:
                continue
            value = _fixed_18(exact)
            payload = {**trade_kwargs, "price": price, "quantity": quantity}
            assert Trade(**{**payload, "value_usdt": value}).value_usdt == Decimal(value)
            wrong = _fixed_18(exact + Fraction(1, 10**18))
            with pytest.raises(ValidationError):
                Trade(**{**payload, "value_usdt": wrong})

    def test_product_needing_more_than_18_places_has_no_valid_value(
        self, trade_kwargs: dict[str, Any]
    ) -> None:
        # 0.0000000001 * 0.0000000001 = 1E-20: not representable in the domain.
        payload = {**trade_kwargs, "price": "0.0000000001", "quantity": "0.0000000001"}
        for value in ["0.000000000000000000", "0.000000000000000001"]:
            with pytest.raises(ValidationError):
                Trade(**{**payload, "value_usdt": value})


# ---------------------------------------------------------------- A-02
INVALID_VERSION_INPUTS: list[Any] = [True, False, 1.0, 2.0, 0, 1, 3, "2", None]


@pytest.fixture
def versioned_samples(
    bybit_instrument: Instrument,
    tick_kwargs: dict[str, Any],
    candle_kwargs: dict[str, Any],
    trade_kwargs: dict[str, Any],
    event_kwargs: dict[str, Any],
) -> dict[str, VersionedContractModel]:
    return {
        "Instrument": bybit_instrument,
        "MarketTick": MarketTick(**tick_kwargs),
        "Candle": Candle(**candle_kwargs),
        "Trade": Trade(**trade_kwargs),
        "MarketEvent": MarketEvent(**event_kwargs),
    }


VERSIONED_NAMES = ["Instrument", "MarketTick", "Candle", "Trade", "MarketEvent"]


class TestA02SchemaVersion:
    @pytest.mark.parametrize("name", VERSIONED_NAMES)
    def test_current_version_accepted_on_both_paths(
        self, versioned_samples: dict[str, VersionedContractModel], name: str
    ) -> None:
        sample = versioned_samples[name]
        data = json.loads(sample.model_dump_json())
        assert data["schema_version"] == SCHEMA_VERSION
        assert type(sample).model_validate(data) == sample
        assert type(sample).model_validate_json(json.dumps(data)) == sample

    @pytest.mark.parametrize("name", VERSIONED_NAMES)
    @pytest.mark.parametrize("version", INVALID_VERSION_INPUTS, ids=repr)
    def test_invalid_marker_rejected_python(
        self, versioned_samples: dict[str, VersionedContractModel], name: str, version: Any
    ) -> None:
        sample = versioned_samples[name]
        data = {**json.loads(sample.model_dump_json()), "schema_version": version}
        with pytest.raises(ValidationError):
            type(sample).model_validate(data)

    @pytest.mark.parametrize("name", VERSIONED_NAMES)
    @pytest.mark.parametrize("version", INVALID_VERSION_INPUTS, ids=repr)
    def test_invalid_marker_rejected_json(
        self, versioned_samples: dict[str, VersionedContractModel], name: str, version: Any
    ) -> None:
        sample = versioned_samples[name]
        data = {**json.loads(sample.model_dump_json()), "schema_version": version}
        with pytest.raises(ValidationError):
            type(sample).model_validate_json(json.dumps(data))

    @pytest.mark.parametrize("version", [Decimal(2), Decimal("2.0")], ids=repr)
    def test_decimal_marker_rejected(self, instrument_kwargs: dict[str, Any], version: Any) -> None:
        with pytest.raises(ValidationError, match="schema_version must be an integer"):
            Instrument(**{**instrument_kwargs, "schema_version": version})


# ---------------------------------------------------------------- A-03
UNSUPPORTED_TIMESTAMPS: list[Any] = [
    b"1767225600",
    b"2026-01-01T00:00:00Z",
    bytearray(b"1767225600"),
    memoryview(b"2026-01-01T00:00:00Z"),
    date(2026, 1, 1),
    time(12, 0),
    Decimal("1767225600"),
    ["2026-01-01T00:00:00Z"],
]


class TestA03TimestampInputTypes:
    @pytest.mark.parametrize("value", UNSUPPORTED_TIMESTAMPS, ids=repr)
    def test_unsupported_types_rejected(
        self, instrument_kwargs: dict[str, Any], value: Any
    ) -> None:
        with pytest.raises(ValidationError):
            Instrument(**{**instrument_kwargs, "listed_at": value})

    @pytest.mark.parametrize(
        ("fixture_name", "model", "field"),
        [
            ("tick_kwargs", MarketTick, "exchange_time"),
            ("tick_kwargs", MarketTick, "received_at"),
            ("trade_kwargs", Trade, "executed_at"),
            ("trade_kwargs", Trade, "received_at"),
            ("candle_kwargs", Candle, "start"),
            ("event_kwargs", MarketEvent, "detected_at"),
        ],
    )
    def test_bytes_epoch_rejected_in_every_model(
        self, request: pytest.FixtureRequest, fixture_name: str, model: type[Any], field: str
    ) -> None:
        kwargs = request.getfixturevalue(fixture_name)
        with pytest.raises(ValidationError):
            model(**{**kwargs, field: b"1767225600"})

    @pytest.mark.parametrize(
        "value", [date(2026, 1, 1), time(12, 0), ["2026-01-01T00:00:00Z"]], ids=repr
    )
    def test_unsupported_type_reported_explicitly(
        self, instrument_kwargs: dict[str, Any], value: Any
    ) -> None:
        with pytest.raises(ValidationError, match="unsupported timestamp type"):
            Instrument(**{**instrument_kwargs, "listed_at": value})

    def test_bytes_epoch_in_unvalidated_nested_instance_rejected(
        self, instrument_kwargs: dict[str, Any], tick_kwargs: dict[str, Any]
    ) -> None:
        # Re-validation passes the nested instance's fields as a mapping, so the model-level
        # binary check rejects it before the field-level timestamp type restriction.
        bad = Instrument.model_construct(**{**instrument_kwargs, "listed_at": b"1767225600"})
        with pytest.raises(ValidationError, match="binary input is not accepted"):
            MarketTick(**{**tick_kwargs, "instrument": bad})

    def test_iso_string_with_offset_still_accepted(self, instrument_kwargs: dict[str, Any]) -> None:
        listed = Instrument(**{**instrument_kwargs, "listed_at": "2026-01-01T01:00:00+01:00"})
        assert listed.listed_at is not None
        assert listed.listed_at.isoformat() == "2026-01-01T00:00:00+00:00"


class TestE3BinaryInputRejected:
    @pytest.mark.parametrize(
        "field", ["symbol", "exchange", "base_asset", "quote_asset", "status", "tick_size"]
    )
    def test_instrument_fields(self, instrument_kwargs: dict[str, Any], field: str) -> None:
        value = str(instrument_kwargs[field]).encode()
        with pytest.raises(ValidationError, match="binary input is not accepted"):
            Instrument(**{**instrument_kwargs, field: value})

    def test_trade_id(self, trade_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="binary input"):
            Trade(**{**trade_kwargs, "trade_id": b"synthetic-1"})

    def test_reason(self) -> None:
        with pytest.raises(ValidationError, match="binary input"):
            DataQuality(status="GAP", reason=bytearray(b"synthetic"))

    def test_instrument_id(self, event_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="binary input"):
            MarketEvent(**{**event_kwargs, "instrument_id": event_kwargs["instrument_id"].encode()})

    def test_metric_name(self) -> None:
        with pytest.raises(ValidationError, match="binary input"):
            MetricValue(name=memoryview(b"delta"), value="1", unit="USDT")


# ---------------------------------------------------------------- A-04
class TestA04InstrumentIdentity:
    def test_metadata_change_keeps_identity_not_snapshot_equality(
        self, bybit_instrument: Instrument
    ) -> None:
        changed = bybit_instrument.replace(status="CLOSED", tick_size="0.01")
        assert changed.instrument_id == bybit_instrument.instrument_id
        assert changed != bybit_instrument
        assert len({bybit_instrument, changed}) == 2

    def test_collections_keyed_by_instrument_id_hold_one_instrument(
        self, bybit_instrument: Instrument
    ) -> None:
        changed = bybit_instrument.replace(status="SETTLING")
        latest = {i.instrument_id: i for i in (bybit_instrument, changed)}
        assert list(latest) == ["BYBIT:USDT_LINEAR_PERPETUAL:BTCUSDT"]
        assert latest[bybit_instrument.instrument_id] is changed


# ---------------------------------------------------------------- A-06
LINE_SEPARATORS = [
    "\n",
    "\r",
    "\r\n",
    "\v",
    "\f",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x85",
    chr(0x2028),
    chr(0x2029),
]


class TestA06ReasonSingleLine:
    @pytest.mark.parametrize("separator", LINE_SEPARATORS, ids=repr)
    def test_quality_reason_rejects_line_separators(self, separator: str) -> None:
        with pytest.raises(ValidationError):
            DataQuality(status="GAP", reason=f"first{separator}second")

    @pytest.mark.parametrize("separator", LINE_SEPARATORS, ids=repr)
    def test_rejection_reason_rejects_line_separators(
        self, event_kwargs: dict[str, Any], separator: str
    ) -> None:
        with pytest.raises(ValidationError):
            MarketEvent(
                **{**event_kwargs, "status": "REJECTED", "rejection_reason": f"a{separator}b"}
            )

    def test_tab_inside_single_line_is_allowed(self) -> None:
        assert DataQuality(status="GAP", reason="gap\tsynthetic").reason == "gap\tsynthetic"


# ---------------------------------------------------------------- A-07
class TestA07SafeModification:
    def test_model_copy_update_is_validated(self, bybit_instrument: Instrument) -> None:
        with pytest.raises(ValidationError, match="greater than zero"):
            bybit_instrument.model_copy(update={"tick_size": Decimal("-1")})

    def test_copy_replace_is_validated(self, bybit_instrument: Instrument) -> None:
        changes: dict[str, Any] = {"tick_size": Decimal("-1")}
        with pytest.raises(ValidationError):
            # typeshed's _SupportsReplace cannot infer pydantic's __replace__ return type.
            copy.replace(bybit_instrument, **changes)  # type: ignore[arg-type]

    def test_replace_is_validated(self, bybit_instrument: Instrument) -> None:
        with pytest.raises(ValidationError):
            bybit_instrument.replace(quote_asset="USDC")

    def test_valid_update_returns_new_validated_record(self, bybit_instrument: Instrument) -> None:
        changed = bybit_instrument.model_copy(update={"tick_size": "0.5"})
        assert changed.tick_size == Decimal("0.5")
        assert isinstance(changed.tick_size, Decimal)
        assert bybit_instrument.tick_size == Decimal("0.10")

    def test_update_with_unknown_field_rejected(self, bybit_instrument: Instrument) -> None:
        with pytest.raises(ValidationError):
            bybit_instrument.model_copy(update={"leverage": "100"})

    def test_copy_without_update_is_equal(self, bybit_instrument: Instrument) -> None:
        assert bybit_instrument.model_copy() == bybit_instrument
        assert bybit_instrument.model_copy(deep=True) == bybit_instrument

    def test_event_status_change_rechecks_invariants(self, event_kwargs: dict[str, Any]) -> None:
        event = MarketEvent(**event_kwargs)
        with pytest.raises(ValidationError, match="rejection_reason is required"):
            event.replace(status="REJECTED")
        rejected = event.replace(status="REJECTED", rejection_reason="synthetic")
        assert rejected.status == "REJECTED"

    def test_audit_probe_copy_into_tick_rejected(
        self, bybit_instrument: Instrument, tick_kwargs: dict[str, Any]
    ) -> None:
        # The audit probe: an invalid copy can no longer be created, so it cannot be nested.
        with pytest.raises(ValidationError, match="greater than zero"):
            bybit_instrument.model_copy(update={"tick_size": Decimal("-1")})
        dumped = {**bybit_instrument.model_dump(), "tick_size": Decimal("-1")}
        with pytest.raises(ValidationError, match="greater than zero"):
            MarketTick(**{**tick_kwargs, "instrument": dumped})

    def test_unvalidated_nested_instrument_rejected(
        self, instrument_kwargs: dict[str, Any], tick_kwargs: dict[str, Any]
    ) -> None:
        bad = Instrument.model_construct(**{**instrument_kwargs, "tick_size": Decimal("-1")})
        with pytest.raises(ValidationError, match="greater than zero"):
            MarketTick(**{**tick_kwargs, "instrument": bad})

    def test_unvalidated_nested_quality_rejected(self, trade_kwargs: dict[str, Any]) -> None:
        bad = DataQuality.model_construct(status=DataQualityStatus.STALE, reason=None)
        with pytest.raises(ValidationError, match="reason is required"):
            Trade(**{**trade_kwargs, "quality": bad})

    def test_unvalidated_nested_metric_rejected(self, event_kwargs: dict[str, Any]) -> None:
        bad = MetricValue.model_construct(name="Bad Name", value=Decimal("1"), unit="USDT")
        with pytest.raises(ValidationError):
            MarketEvent(**{**event_kwargs, "observed_values": [bad]})
