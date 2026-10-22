# FAZA 0 — raport zmian

Stan wyjściowy: pusty katalog roboczy, brak repozytorium Git. Wszystkie pliki są nowe.
Nie nadpisano ani nie zmodyfikowano żadnego istniejącego projektu.
Poza repozytorium nie zmieniano niczego (globalny Python, zmienne systemowe, konfiguracja Git — bez zmian).

## Konfiguracja projektu
| Plik | Uzasadnienie |
|---|---|
| `pyproject.toml` | Metadane pakietu, przypięte zależności, konfiguracja pytest/Ruff/mypy (DEC-001, DEC-016) |
| `requirements-dev.lock` | Pełna lista przypiętych pakietów (constraints) dla odtwarzalności (DEC-016) |
| `.gitignore` | Wykluczenie venv, cache, `.env`, baz SQLite |
| `.gitattributes` | Końce linii LF (DEC-019) |
| `.env.example` | Wzorzec bez zmiennych; zakaz sekretów (wymaganie struktury) |

## Kod (`src/market_intelligence/`)
| Plik | Uzasadnienie |
|---|---|
| `__init__.py`, `py.typed` | Pakiet główny, wersja, znacznik typów |
| `core/__init__.py` | Warstwa bez I/O |
| `core/clock/__init__.py`, `core/clock/utc.py` | `ensure_utc`, `UTC_EPOCH` (DEC-004, DEC-008) |
| `core/config/__init__.py`, `core/events/__init__.py` | Pakiety zarezerwowane (DEC-008) |
| `core/models/base.py` | Konfiguracja kontraktów, wersja schematu (DEC-005) |
| `core/models/types.py` | Typy pól: Decimal, UTC, symbole, przyczyny (DEC-003, DEC-004) |
| `core/models/enums.py` | Enumeracje kontraktów |
| `core/models/data_quality.py` | `DataQuality` (DEC-009) |
| `core/models/instrument.py` | `Instrument`, `InstrumentId` (DEC-006) |
| `core/models/market_tick.py` | `MarketTick` |
| `core/models/candle.py` | `Candle` (DEC-007) |
| `core/models/trade.py` | `Trade` (DEC-010) |
| `core/models/market_event.py` | `MarketEvent`, `MetricValue` (DEC-011, DEC-015) |
| `core/models/__init__.py` | Publiczne API modeli |

## Testy (`tests/`)
| Plik | Uzasadnienie |
|---|---|
| `conftest.py` | Syntetyczne fixture'y |
| `unit/test_*.py` (7 plików) | Wymagane testy walidacji (TEST_PLAN.md §3) |
| `contracts/test_serialization.py` | JSON, Decimal, wersja schematu |
| `contracts/test_synthetic_fixtures.py` | Fixture'y JSON oznaczone jako syntetyczne i zgodne z kontraktami |
| `contracts/test_package_import.py` | Import po instalacji editable, brak I/O w `core` |
| `fixtures/synthetic_contract_samples.json` | Syntetyczne rekordy wszystkich kontraktów |

## Dokumentacja
| Plik | Uzasadnienie |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | Dokumentacja niezależna od agenta (DEC-014) |
| `README.md`, `CHANGELOG.md` | Uruchomienie od zera, historia zmian |
| `docs/ARCHITECTURE.md`, `DATA_CONTRACTS.md`, `DETECTORS.md`, `EXCHANGE_API.md`, `TEST_PLAN.md`, `DECISIONS.md`, `MODULE_MAP.md`, `PROJECT_STATE.md`, `HANDOFF.md`, `DEVELOPMENT.md` | Wymagane dokumenty techniczne |

## Raporty
`reports/phase0/FAZA0_*.md` i `reports/phase0/command_logs/*.txt` — wyniki wykonania.

Lista plików wg Git: `git show --stat --format= <commit>` (commit wskazany w FAZA0_RAPORT.md).
