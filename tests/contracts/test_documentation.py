"""Documentation references point to files that exist (audit recommendation, section 5).

Checks every ``*.md`` file tracked in the repository layout (excluding ``.venv`` and
caches): relative Markdown links ``[text](target)`` with optional ``#anchor``, and
repository paths written in backticks. External ``http(s)`` links are not fetched.
Paths of PLANNED modules are written without a leading ``src/``/``core/`` prefix in
docs/MODULE_MAP.md, so they are intentionally not checked.

Excluded: ``reports/**/audyt*/`` — verbatim copies of external audit materials, which are
kept unedited (their own README.md is checked).
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_PARTS = {".venv", ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def _is_external_audit_copy(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    in_audit_dir = parts[0] == "reports" and any(p.startswith("audyt") for p in parts[:-1])
    return in_audit_dir and path.name != "README.md"


MARKDOWN_FILES = sorted(
    path
    for path in ROOT.rglob("*.md")
    if not EXCLUDED_PARTS & set(path.relative_to(ROOT).parts) and not _is_external_audit_copy(path)
)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
REPO_PATH = re.compile(r"`((?:src|docs|tests|reports|\.github)/[^`*<>\s]+)`")
PACKAGE_PATH = re.compile(r"`(core/[^`*<>\s]+\.py)`")
TOP_LEVEL_FILE = re.compile(
    r"`((?:AGENTS|CLAUDE|README|CHANGELOG)\.md|pyproject\.toml|requirements-dev\.lock"
    r"|\.gitignore|\.gitattributes|\.env\.example)`"
)
HEADING = re.compile(r"^#+\s+(.*)$", re.MULTILINE)


def _slug(heading: str) -> str:
    return re.sub(r"[^\w\- ]", "", heading.lower()).strip().replace(" ", "-")


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def test_markdown_files_found() -> None:
    assert len(MARKDOWN_FILES) >= 15


@pytest.mark.parametrize("path", MARKDOWN_FILES, ids=_relative)
def test_relative_links_resolve(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        file_part, _, anchor = target.partition("#")
        resolved = (path.parent / file_part).resolve() if file_part else path
        assert resolved.exists(), f"{_relative(path)}: broken link {target}"
        if anchor and resolved.suffix == ".md":
            slugs = {_slug(h) for h in HEADING.findall(resolved.read_text(encoding="utf-8"))}
            assert anchor in slugs, f"{_relative(path)}: missing anchor {target}"


@pytest.mark.parametrize("path", MARKDOWN_FILES, ids=_relative)
def test_backticked_paths_exist(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    candidates = [*REPO_PATH.findall(text), *TOP_LEVEL_FILE.findall(text)]
    candidates += [f"src/market_intelligence/{p}" for p in PACKAGE_PATH.findall(text)]
    for token in candidates:
        candidate = token.rstrip(".,;:)").split("::")[0]
        assert (ROOT / candidate).exists(), f"{_relative(path)}: path not found {candidate}"
