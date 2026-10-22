import pytest
from pydantic import ValidationError

from market_intelligence.core.models import DataQuality, DataQualityStatus

DEGRADED = [status for status in DataQualityStatus if status is not DataQualityStatus.VALID]


def test_valid_without_reason() -> None:
    quality = DataQuality.valid()
    assert quality.status is DataQualityStatus.VALID
    assert quality.reason is None
    assert quality.is_valid


def test_valid_may_carry_reason() -> None:
    quality = DataQuality(status="VALID", reason="synthetic: checked against reference")
    assert quality.reason == "synthetic: checked against reference"


@pytest.mark.parametrize("status", list(DataQualityStatus))
def test_every_status_accepts_reason(status: DataQualityStatus) -> None:
    quality = DataQuality(status=status, reason="synthetic reason")
    assert quality.status is status
    assert quality.reason == "synthetic reason"


@pytest.mark.parametrize("status", DEGRADED)
def test_degraded_status_requires_reason(status: DataQualityStatus) -> None:
    with pytest.raises(ValidationError, match="reason is required"):
        DataQuality(status=status)


@pytest.mark.parametrize("status", DEGRADED)
def test_degraded_status_is_not_valid(status: DataQualityStatus) -> None:
    assert not DataQuality(status=status, reason="synthetic").is_valid


@pytest.mark.parametrize("reason", ["", "   ", " leading", "trailing ", "multi\nline"])
def test_rejects_blank_or_padded_reason(reason: str) -> None:
    with pytest.raises(ValidationError):
        DataQuality(status="STALE", reason=reason)


def test_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        DataQuality(status="OK", reason="synthetic")
