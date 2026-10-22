"""Anomaly event produced by a detector (detectors themselves are PLANNED)."""

from typing import Annotated, Self
from uuid import UUID

from pydantic import Field, model_validator

from market_intelligence.core.models.base import ContractModel, VersionedContractModel
from market_intelligence.core.models.data_quality import DataQuality
from market_intelligence.core.models.enums import DetectorId, EventDirection, EventStatus
from market_intelligence.core.models.instrument import InstrumentId
from market_intelligence.core.models.types import FiniteDecimal, ReasonText, UtcDatetime

MetricName = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")]
MetricUnit = Annotated[str, Field(pattern=r"^[A-Z][A-Z0-9_]{0,31}$")]
DetectorVersion = Annotated[str, Field(pattern=r"^\d+\.\d+\.\d+$")]
ConfigVersion = Annotated[str, Field(pattern=r"^[A-Za-z0-9._:-]{1,64}$")]


class MetricValue(ContractModel):
    """Named numeric value with its unit, e.g. ``price_change`` in ``PERCENT``."""

    name: MetricName
    value: FiniteDecimal
    unit: MetricUnit


def _require_unique_names(values: tuple[MetricValue, ...], field: str) -> None:
    names = [metric.name for metric in values]
    if len(names) != len(set(names)):
        raise ValueError(f"{field} contains duplicate metric names")


class MarketEvent(VersionedContractModel):
    """Detected market anomaly.

    Invariants (DEC-011):
    - ``window_start < window_end <= detected_at`` (ordering of the declared times only; it
      does not prove that a detector used no future data);
    - ``rejection_reason`` is present if and only if ``status`` is ``REJECTED``;
    - ``VERIFIED`` requires ``quality`` to be ``VALID``.

    ``event_id`` is supplied by the producer and never generated here, so replay can
    reproduce identical events (DEC-015). No status transition logic exists yet.
    """

    event_id: UUID
    instrument_id: InstrumentId
    detector_id: DetectorId
    detector_version: DetectorVersion
    config_version: ConfigVersion
    detected_at: UtcDatetime
    window_start: UtcDatetime
    window_end: UtcDatetime
    direction: EventDirection
    observed_values: tuple[MetricValue, ...] = Field(min_length=1)
    reference_values: tuple[MetricValue, ...] = Field(min_length=1)
    quality: DataQuality
    status: EventStatus
    rejection_reason: ReasonText | None = None

    @model_validator(mode="after")
    def _check_window(self) -> Self:
        if self.window_start >= self.window_end:
            raise ValueError("window_start must be earlier than window_end")
        if self.detected_at < self.window_end:
            raise ValueError("detected_at must not be earlier than window_end")
        return self

    @model_validator(mode="after")
    def _check_metrics(self) -> Self:
        _require_unique_names(self.observed_values, "observed_values")
        _require_unique_names(self.reference_values, "reference_values")
        return self

    @model_validator(mode="after")
    def _check_status(self) -> Self:
        is_rejected = self.status is EventStatus.REJECTED
        if is_rejected and self.rejection_reason is None:
            raise ValueError("rejection_reason is required when status is REJECTED")
        if not is_rejected and self.rejection_reason is not None:
            raise ValueError("rejection_reason is only allowed when status is REJECTED")
        if self.status is EventStatus.VERIFIED and not self.quality.is_valid:
            raise ValueError("a VERIFIED event requires VALID data quality")
        return self
