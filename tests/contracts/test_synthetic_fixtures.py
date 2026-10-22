"""Stored JSON fixtures validate against the current contracts and are marked synthetic."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from market_intelligence.core.models import (
    SCHEMA_VERSION,
    Candle,
    DataSource,
    Instrument,
    MarketEvent,
    MarketTick,
    Trade,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
FIXTURE_FILES = sorted(FIXTURES_DIR.glob("*.json"))
SECTIONS: dict[str, type[BaseModel]] = {
    "instruments": Instrument,
    "market_ticks": MarketTick,
    "candles": Candle,
    "trades": Trade,
    "market_events": MarketEvent,
}


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def test_fixture_files_exist() -> None:
    assert FIXTURE_FILES, f"no JSON fixtures in {FIXTURES_DIR}"


@pytest.mark.parametrize("path", FIXTURE_FILES, ids=lambda p: p.name)
def test_fixture_is_marked_synthetic(path: Path) -> None:
    assert path.name.startswith("synthetic_")
    data = _load(path)
    assert data["synthetic"] is True
    assert "SYNTHETIC" in data["description"]
    assert data["schema_version"] == SCHEMA_VERSION


@pytest.mark.parametrize("path", FIXTURE_FILES, ids=lambda p: p.name)
def test_fixture_records_validate(path: Path) -> None:
    data = _load(path)
    validated = 0
    for section, model in SECTIONS.items():
        for record in data.get(section, []):
            instance = model.model_validate_json(json.dumps(record))
            source = getattr(instance, "source", DataSource.SYNTHETIC)
            assert source is DataSource.SYNTHETIC
            validated += 1
    assert validated > 0
