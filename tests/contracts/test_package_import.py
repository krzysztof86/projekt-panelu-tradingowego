"""The package is importable from an editable install, independent of the test runner."""

import json
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import market_intelligence
from market_intelligence.core.models import SCHEMA_VERSION

DIST_NAME = "market-intelligence-desktop"
SRC_DIR = Path(__file__).resolve().parents[2] / "src"


def test_version_matches_distribution_metadata() -> None:
    assert market_intelligence.__version__ == metadata.version(DIST_NAME)


def test_installed_as_editable() -> None:
    direct_url = metadata.distribution(DIST_NAME).read_text("direct_url.json")
    assert direct_url is not None, "package is not installed via pip (direct_url.json missing)"
    assert json.loads(direct_url)["dir_info"].get("editable") is True


def test_package_resolves_to_src_layout() -> None:
    assert Path(market_intelligence.__file__).resolve().is_relative_to(SRC_DIR)


def test_import_in_isolated_interpreter(tmp_path: Path) -> None:
    code = (
        "import market_intelligence, market_intelligence.core.models as m; "
        "print(market_intelligence.__version__, m.SCHEMA_VERSION)"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == [market_intelligence.__version__, str(SCHEMA_VERSION)]


def test_core_import_does_not_load_io_libraries() -> None:
    """Limited dependency check (A-05): importing every core package loads no I/O library.

    This inspects ``sys.modules`` only. It does not prove the absence of I/O; see
    ``test_core_boundaries.py`` for the import-boundary scan and the runtime guard.
    """
    code = (
        "import sys, market_intelligence.core, market_intelligence.core.models, "
        "market_intelligence.core.clock, market_intelligence.core.config, "
        "market_intelligence.core.events; "
        "banned = {'socket', 'ssl', 'http', 'urllib', 'sqlite3', 'PySide6', 'requests', "
        "'websockets', 'aiohttp', 'httpx', 'asyncio', 'selectors', 'subprocess'}; "
        "print(sorted(banned & {name.split('.')[0] for name in sys.modules}))"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"
