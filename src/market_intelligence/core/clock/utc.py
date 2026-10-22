"""UTC normalization.

The project never accepts naive datetimes: a timestamp without timezone information
is ambiguous and is rejected instead of being interpreted as local time or UTC.
"""

from datetime import UTC, datetime
from typing import Final

UTC_EPOCH: Final = datetime(1970, 1, 1, tzinfo=UTC)
"""Unix epoch in UTC; reference point for candle interval alignment."""


def ensure_utc(value: datetime) -> datetime:
    """Return ``value`` converted to UTC.

    Raises:
        ValueError: if ``value`` is naive (no timezone or no UTC offset).
    """
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError("naive datetime is not accepted; timezone information is required")
    return value.astimezone(UTC)
