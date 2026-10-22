"""Boundary checks for the I/O-free ``core`` layer (audit finding A-05).

Two complementary, limited checks:

1. Static import boundary: every module in ``src/market_intelligence/core`` imports only
   an explicit allow-list (selected standard library modules, pydantic and other ``core``
   modules) and calls no ``open``/``exec``/``eval``/``__import__``. ``model_construct`` is
   not used anywhere in ``src`` (DEC-021).
2. Runtime guard: application-level file and network entry points are replaced by
   functions that fail the test, then every contract is validated, serialized, copied and
   queried. Python's own import machinery is not blocked; modules are imported before
   the guard is installed.

Neither check proves the absence of every possible I/O; together they cover the
operations the project defines as application I/O (docs/ARCHITECTURE.md §3).
"""

import ast
import builtins
import io
import json
import os
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, NoReturn

import pytest

from market_intelligence.core.clock import ensure_utc
from market_intelligence.core.models import (
    Candle,
    ContractModel,
    Instrument,
    MarketEvent,
    MarketTick,
    Trade,
)

SRC_DIR = Path(__file__).resolve().parents[2] / "src" / "market_intelligence"
CORE_DIR = SRC_DIR / "core"
FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_contract_samples.json"

ALLOWED_TOP_LEVEL_IMPORTS = {
    "collections",
    "datetime",
    "decimal",
    "enum",
    "re",
    "typing",
    "uuid",
    "pydantic",
    "market_intelligence",
}
FORBIDDEN_CALLS = {"open", "exec", "eval", "__import__", "compile"}
CORE_FILES = sorted(CORE_DIR.rglob("*.py"))
SRC_FILES = sorted(SRC_DIR.rglob("*.py"))


def _imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative imports are not used in this project"
            assert node.module is not None
            modules.append(node.module)
    return modules


def _relative(path: Path) -> str:
    return path.relative_to(SRC_DIR.parent).as_posix()


def test_core_files_found() -> None:
    assert len(CORE_FILES) >= 10


@pytest.mark.parametrize("path", CORE_FILES, ids=_relative)
def test_core_imports_only_allowed_modules(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for module in _imported_modules(tree):
        top = module.split(".")[0]
        assert top in ALLOWED_TOP_LEVEL_IMPORTS, f"{_relative(path)} imports {module}"
        if top == "market_intelligence":
            assert module.startswith("market_intelligence.core"), (
                f"{_relative(path)} imports {module} from outside core"
            )


@pytest.mark.parametrize("path", CORE_FILES, ids=_relative)
def test_core_makes_no_forbidden_calls(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in FORBIDDEN_CALLS, f"{_relative(path)} calls {node.func.id}"


@pytest.mark.parametrize("path", SRC_FILES, ids=_relative)
def test_model_construct_not_used_in_src(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr != "model_construct", f"{_relative(path)} uses model_construct"


def _io_attempted(*_args: Any, **_kwargs: Any) -> NoReturn:
    raise AssertionError("application I/O attempted inside core")


@pytest.fixture
def records() -> list[ContractModel]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sections: dict[str, type[ContractModel]] = {
        "instruments": Instrument,
        "market_ticks": MarketTick,
        "candles": Candle,
        "trades": Trade,
        "market_events": MarketEvent,
    }
    return [
        model.model_validate_json(json.dumps(record))
        for section, model in sections.items()
        for record in data[section]
    ]


def test_core_runtime_performs_no_file_or_network_io(
    monkeypatch: pytest.MonkeyPatch, records: list[ContractModel]
) -> None:
    payloads = [(type(record), record.model_dump_json()) for record in records]
    for record in records:  # warm-up: lazy imports and schema caches happen here
        type(record).model_json_schema()

    for target, name in [
        (builtins, "open"),
        (io, "open"),
        (os, "open"),
        (os, "system"),
        (subprocess, "Popen"),
        (socket, "socket"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
    ]:
        monkeypatch.setattr(target, name, _io_attempted)

    for model, payload in payloads:
        record = model.model_validate_json(payload)
        assert model.model_validate_json(record.model_dump_json()) == record
        assert model.model_validate(record.model_dump()) == record
        assert record.model_copy(update={}) == record
        assert record.replace() == record
        model.model_json_schema()
        if isinstance(record, Candle):
            assert record.contains(record.start)
    assert ensure_utc(datetime(2026, 1, 5, tzinfo=UTC)).tzinfo is UTC
