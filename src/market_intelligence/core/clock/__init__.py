"""Time handling primitives. All internal timestamps are timezone-aware UTC."""

from market_intelligence.core.clock.utc import UTC_EPOCH, ensure_utc

__all__ = ["UTC_EPOCH", "ensure_utc"]
