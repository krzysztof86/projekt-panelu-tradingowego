from datetime import datetime, timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from market_intelligence.core.models import (
    DataQuality,
    DetectorId,
    EventDirection,
    EventStatus,
    MarketEvent,
)


class TestValidEvents:
    def test_candidate(self, event_kwargs: dict[str, Any]) -> None:
        event = MarketEvent(**event_kwargs)
        assert event.status is EventStatus.CANDIDATE
        assert event.detector_id is DetectorId.D1
        assert event.rejection_reason is None
        assert event.observed_values[0].name == "price_change"

    @pytest.mark.parametrize("detector", list(DetectorId))
    def test_every_detector(self, event_kwargs: dict[str, Any], detector: DetectorId) -> None:
        assert MarketEvent(**{**event_kwargs, "detector_id": detector}).detector_id is detector

    @pytest.mark.parametrize("direction", list(EventDirection))
    def test_every_direction(self, event_kwargs: dict[str, Any], direction: EventDirection) -> None:
        assert MarketEvent(**{**event_kwargs, "direction": direction}).direction is direction

    @pytest.mark.parametrize(
        "status", [EventStatus.CANDIDATE, EventStatus.ANALYZING, EventStatus.EXPIRED]
    )
    def test_statuses_without_reason(
        self, event_kwargs: dict[str, Any], status: EventStatus
    ) -> None:
        assert MarketEvent(**{**event_kwargs, "status": status}).status is status

    def test_negative_metric_allowed(self, event_kwargs: dict[str, Any]) -> None:
        observed = [{"name": "price_change", "value": "-2.5", "unit": "PERCENT"}]
        event = MarketEvent(**{**event_kwargs, "direction": "DOWN", "observed_values": observed})
        assert event.observed_values[0].value < 0

    def test_multiple_metrics(self, event_kwargs: dict[str, Any]) -> None:
        observed = [
            {"name": "price_change", "value": "1.2", "unit": "PERCENT"},
            {"name": "cumulative_delta", "value": "-350000", "unit": "USDT"},
        ]
        event = MarketEvent(**{**event_kwargs, "detector_id": "D3", "observed_values": observed})
        assert [m.name for m in event.observed_values] == ["price_change", "cumulative_delta"]

    def test_detected_at_equal_to_window_end(self, event_kwargs: dict[str, Any]) -> None:
        event = MarketEvent(**event_kwargs)
        assert event.detected_at == event.window_end


class TestVerifiedVersusRejected:
    def test_verified(self, event_kwargs: dict[str, Any]) -> None:
        event = MarketEvent(**{**event_kwargs, "status": "VERIFIED"})
        assert event.status is EventStatus.VERIFIED
        assert event.rejection_reason is None

    def test_rejected(self, event_kwargs: dict[str, Any]) -> None:
        event = MarketEvent(
            **{**event_kwargs, "status": "REJECTED", "rejection_reason": "synthetic: data gap"}
        )
        assert event.status is EventStatus.REJECTED
        assert event.rejection_reason == "synthetic: data gap"

    def test_verified_and_rejected_differ(self, event_kwargs: dict[str, Any]) -> None:
        verified = MarketEvent(**{**event_kwargs, "status": "VERIFIED"})
        rejected = MarketEvent(
            **{**event_kwargs, "status": "REJECTED", "rejection_reason": "synthetic: data gap"}
        )
        assert verified != rejected
        assert verified.status is not rejected.status

    def test_rejected_requires_reason(self, event_kwargs: dict[str, Any]) -> None:
        with pytest.raises(ValidationError, match="rejection_reason is required"):
            MarketEvent(**{**event_kwargs, "status": "REJECTED"})

    @pytest.mark.parametrize("status", ["CANDIDATE", "ANALYZING", "VERIFIED", "EXPIRED"])
    def test_reason_only_for_rejected(self, event_kwargs: dict[str, Any], status: str) -> None:
        with pytest.raises(ValidationError, match="only allowed when status is REJECTED"):
            MarketEvent(**{**event_kwargs, "status": status, "rejection_reason": "synthetic"})

    def test_verified_requires_valid_quality(self, event_kwargs: dict[str, Any]) -> None:
        stale = DataQuality(status="STALE", reason="synthetic: no ticks for 30 s")
        with pytest.raises(ValidationError, match="requires VALID data quality"):
            MarketEvent(**{**event_kwargs, "status": "VERIFIED", "quality": stale})

    def test_rejected_with_degraded_quality(self, event_kwargs: dict[str, Any]) -> None:
        gap = DataQuality(status="GAP", reason="synthetic: missing candle")
        event = MarketEvent(
            **{**event_kwargs, "status": "REJECTED", "rejection_reason": "data gap", "quality": gap}
        )
        assert not event.quality.is_valid


class TestWindow:
    def test_rejects_empty_window(self, event_kwargs: dict[str, Any]) -> None:
        start = event_kwargs["window_start"]
        with pytest.raises(ValidationError, match="window_start must be earlier"):
            MarketEvent(**{**event_kwargs, "window_end": start, "detected_at": start})

    def test_rejects_inverted_window(self, event_kwargs: dict[str, Any]) -> None:
        end = event_kwargs["window_end"]
        with pytest.raises(ValidationError, match="window_start must be earlier"):
            MarketEvent(**{**event_kwargs, "window_start": end + timedelta(seconds=1)})

    def test_rejects_detection_before_window_end(self, event_kwargs: dict[str, Any]) -> None:
        early = event_kwargs["window_end"] - timedelta(milliseconds=1)
        with pytest.raises(ValidationError, match="detected_at must not be earlier"):
            MarketEvent(**{**event_kwargs, "detected_at": early})

    @pytest.mark.parametrize("field", ["detected_at", "window_start", "window_end"])
    def test_rejects_naive(self, event_kwargs: dict[str, Any], field: str) -> None:
        naive = datetime(2026, 1, 5, 12, 0)  # noqa: DTZ001 - naive on purpose
        with pytest.raises(ValidationError, match="naive datetime"):
            MarketEvent(**{**event_kwargs, field: naive})


class TestInvalidFields:
    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("event_id", "not-a-uuid"),
            ("instrument_id", "BTCUSDT"),
            ("instrument_id", "OKX:USDT_LINEAR_PERPETUAL:BTCUSDT"),
            ("instrument_id", "BYBIT:SPOT:BTCUSDT"),
            ("instrument_id", "BYBIT:USDT_LINEAR_PERPETUAL:"),
            ("detector_id", "D4"),
            ("detector_version", "1.0"),
            ("detector_version", "v1.0.0"),
            ("config_version", ""),
            ("config_version", "has space"),
            ("direction", "SIDEWAYS"),
            ("status", "CONFIRMED"),
            ("observed_values", []),
            ("reference_values", []),
        ],
    )
    def test_rejects(self, event_kwargs: dict[str, Any], field: str, value: Any) -> None:
        with pytest.raises(ValidationError):
            MarketEvent(**{**event_kwargs, field: value})

    @pytest.mark.parametrize("field", ["observed_values", "reference_values"])
    def test_rejects_duplicate_metric_names(self, event_kwargs: dict[str, Any], field: str) -> None:
        metric = {"name": "price_change", "value": "1", "unit": "PERCENT"}
        with pytest.raises(ValidationError, match="duplicate metric names"):
            MarketEvent(**{**event_kwargs, field: [metric, metric]})

    @pytest.mark.parametrize(
        "metric",
        [
            {"name": "price_change", "value": "NaN", "unit": "PERCENT"},
            {"name": "price_change", "value": 1.5, "unit": "PERCENT"},
            {"name": "PriceChange", "value": "1", "unit": "PERCENT"},
            {"name": "price_change", "value": "1", "unit": "percent"},
            {"name": "price_change", "value": "1"},
        ],
    )
    def test_rejects_invalid_metric(
        self, event_kwargs: dict[str, Any], metric: dict[str, Any]
    ) -> None:
        with pytest.raises(ValidationError):
            MarketEvent(**{**event_kwargs, "observed_values": [metric]})

    def test_event_id_required(self, event_kwargs: dict[str, Any]) -> None:
        del event_kwargs["event_id"]
        with pytest.raises(ValidationError):
            MarketEvent(**event_kwargs)
