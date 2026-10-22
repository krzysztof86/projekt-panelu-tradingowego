"""Data quality annotation attached to every market data record and event."""

from typing import Self

from pydantic import model_validator

from market_intelligence.core.models.base import ContractModel
from market_intelligence.core.models.enums import DataQualityStatus
from market_intelligence.core.models.types import ReasonText


class DataQuality(ContractModel):
    """Quality status with an optional reason.

    Every status can carry a reason. Any status other than ``VALID`` requires one,
    so a degraded state is always explained (DEC-009).
    """

    status: DataQualityStatus
    reason: ReasonText | None = None

    @model_validator(mode="after")
    def _reason_required_when_degraded(self) -> Self:
        if self.status is not DataQualityStatus.VALID and self.reason is None:
            raise ValueError(f"reason is required for data quality status {self.status}")
        return self

    @classmethod
    def valid(cls) -> Self:
        return cls(status=DataQualityStatus.VALID)

    @property
    def is_valid(self) -> bool:
        return self.status is DataQualityStatus.VALID
