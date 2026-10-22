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
        ValueError: if ``value`` is naive (no timezone or no UTC offset), or if the UTC
            equivalent falls outside the ``datetime`` range (year 1 to 9999), e.g.
            ``0001-01-01T00:00:00+01:00``. Inside contracts this becomes a ``ValidationError``.
    """
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise ValueError("naive datetime is not accepted; timezone information is required")
    try:
        return value.astimezone(UTC)
    except OverflowError as exc:
        raise ValueError(
            f"{value.isoformat()} has no representable UTC equivalent "
            "(outside the datetime range of years 1 to 9999)"
        ) from exc
