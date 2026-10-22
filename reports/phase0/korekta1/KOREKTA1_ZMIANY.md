# FAZA 0 — korekta 1: raport zmian

Porównanie z audytowanym commitem: `git diff --stat 2fcc5f7 <commit korekty>`.
Poza repozytorium nie zmieniano niczego (globalny Python, zmienne systemowe, konfiguracja Git).

## Kod (`src/market_intelligence/`)
| Plik | Zmiana | Ustalenie / decyzja |
|---|---|---|
| `__init__.py` | wersja 0.0.2 | DEC-022 |
| `core/models/base.py` | `SCHEMA_VERSION = 2`; ścisły znacznik wersji (`type(v) is int`); `revalidate_instances="always"`; walidator odrzucający dane binarne; `replace()`; walidujące `model_copy(update=...)` | A-02, A-03, A-07, E-2, E-3; DEC-004, DEC-005, DEC-021, DEC-022 |
| `core/models/types.py` | dziedzina Decimal (`MAX_DECIMAL_PLACES`, `MAX_INTEGER_DIGITS`); pola czasu tylko `datetime`/`str`; `ReasonText` jednoliniowy wg `str.splitlines()` | A-01, A-03, A-06, E-1, E-4; DEC-004, DEC-009, DEC-020 |
| `core/models/trade.py` | `_exact_product` — dokładny iloczyn w prywatnym kontekście `decimal` | A-01; DEC-010 |

## Konfiguracja
| Plik | Zmiana | Uzasadnienie |
|---|---|---|
| `pyproject.toml` | `version = "0.0.2"`; `requires-python = ">=3.14,<3.15"` | DEC-022, DEC-002 (audyt §5) |

## Testy
| Plik | Zmiana | Uzasadnienie |
|---|---|---|
| `tests/regression/test_audit1_phase0.py` | **nowy**: 208 testów regresji A-01–A-07, E-1–E-4 | zlecenie pkt 5 |
| `tests/contracts/test_core_boundaries.py` | **nowy**: granica importów, zakazane wywołania, zakaz `model_construct`, strażnik I/O | A-05, A-07 |
| `tests/contracts/test_documentation.py` | **nowy**: odnośniki i ścieżki w dokumentacji | audyt §5 |
| `tests/contracts/test_package_import.py` | oczekiwana wersja schematu z `SCHEMA_VERSION`; `test_core_has_no_io_dependencies` → `test_core_import_does_not_load_io_libraries` (opis zakresu, import wszystkich pakietów `core`, 3 dodatkowe zakazane moduły) | A-05; zakres rozszerzony, nie zawężony |
| `tests/contracts/test_serialization.py` | `SCHEMA_VERSION == 2`; odrzucane wersje `[0, 1, 3, "2", None]` (było `[0, 2, "1", None]`); parametr z 30 cyframi całkowitymi zastąpiony dwiema granicami dziedziny | DEC-022, DEC-020 — szczegóły w KOREKTA1_TESTY.md §3 |
| `tests/unit/test_trade.py` | przykład wysokiej precyzji: 38 cyfr znaczących w dziedzinie (było 37 cyfr i 19 miejsc po przecinku, poza dziedziną) | DEC-020 |
| `tests/fixtures/synthetic_contract_samples.json` | `schema_version` 1 → 2 | DEC-022 |

## Dokumentacja
| Plik | Zmiana |
|---|---|
| `docs/requirements/FAZA0_SPECYFIKACJA.md`, `docs/requirements/FAZA0_KOREKTA1_ZLECENIE.md` | **nowe** — teksty źródłowe wymagań (DEC-024) |
| `docs/DATA_CONTRACTS.md` | schemat 2; dziedzina Decimal (§1.1); ścieżki tworzenia rekordów (§1.2); typy wejścia czasu; dane binarne; tożsamość vs równość; granice gwarancji `MarketEvent` |
| `docs/DECISIONS.md` | lista decyzji do rozstrzygnięcia z rekomendacjami audytu; zmiany DEC-002, 004, 005, 006, 009, 010, 011, 016; nowe DEC-020–DEC-025; OQ-14, OQ-15 |
| `docs/ARCHITECTURE.md` | zakres kontroli braku I/O (§3); §7 gwarancje modelu a własności systemu |
| `docs/MODULE_MAP.md` | nowe API i stałe, nowe testy, `tests/regression/` |
| `docs/TEST_PLAN.md` | kryteria odbioru po korekcie; §7 mapowanie regresji audytu |
| `docs/DEVELOPMENT.md` | oczekiwany wynik importu `0.0.2 2`; `tests/regression/` w procedurze zmiany kontraktu |
| `docs/EXCHANGE_API.md` | potwierdzenia Bybit z audytu; obowiązki konektorów (dziedzina, dane binarne) |
| `docs/HANDOFF.md` | lokalizacja raportów korekt i kopii audytów |
| `docs/PROJECT_STATE.md` | stan po korekcie 1 |
| `AGENTS.md`, `README.md` | odnośnik do `docs/requirements/`; adres repozytorium w README |
| `CHANGELOG.md` | wpis 0.0.2 |
| `reports/phase0/FAZA0_HANDOFF_AUDIT.md` | erratum: 16 plików `.py` w `src/` |

## Raporty i materiały audytu
| Ścieżka | Zawartość |
|---|---|
| `reports/phase0/audyt1/` | kopia materiałów audytu 1 z sumami SHA-256 i opisem jedynej zmiany (usunięte ścieżki lokalne) |
| `reports/phase0/korekta1/` | raport korekty, testy, zmiany, logi poleceń |
