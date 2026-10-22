# FAZA 0 — korekta 2: raport testów

Data: 2026-10-22. Środowisko: Windows 11 Home x64 (10.0.26200), Python 3.14.5, pip 26.2.2,
pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0, pydantic 2.14.1 (zgodne z `requirements-dev.lock`).
Kontrole z wyłączoną zmienną `PYTHONOPTIMIZE` (DEC-018).

## 1. Kontrole w katalogu roboczym (gałąź `task/faza0-korekta2`)
| # | Polecenie | Wynik | Log |
|---|---|---|---|
| 1 | `python -m pytest -v` | **720 zaliczonych**, 0 niezaliczonych, 0 pominiętych, 0 xfail, 0 błędów; kod 0 | `02_pytest.txt` |
| 2 | `python -m ruff check .` | `All checks passed!`; kod 0 | `03_ruff_check.txt` |
| 3 | `python -m ruff format --check .` | `64 files already formatted` (Python oraz Markdown/TOML); kod 0 | `04_ruff_format_check.txt` |
| 4 | `python -m mypy` | `Success: no issues found in 31 source files`; kod 0 | `05_mypy.txt` |
| 5 | `python -I -c "import market_intelligence, market_intelligence.core.models as m; print(market_intelligence.__version__, m.SCHEMA_VERSION)"` | `0.0.2 2`; kod 0 | `06_import_check.txt` |

`python` = `.\.venv\Scripts\python.exe` (w logach z Git Bash: `./.venv/Scripts/python.exe`).

## 2. Liczba testów wg pliku
| Plik | Testy | Na `f0c36e9` |
|---|---|---|
| `tests/regression/test_audit1_phase0.py` | 208 | 208 |
| `tests/regression/test_audit2_phase0.py` | 122 | — (nowy) |
| `tests/contracts/test_documentation.py` | 63 | 53 |
| `tests/unit/test_candle.py` | 53 | 53 |
| `tests/unit/test_market_event.py` | 51 | 51 |
| `tests/contracts/test_core_boundaries.py` | 48 | 48 |
| `tests/unit/test_instrument.py` | 43 | 43 |
| `tests/unit/test_trade.py` | 37 | 37 |
| `tests/unit/test_primitives.py` | 25 | 25 |
| `tests/unit/test_data_quality.py` | 24 | 24 |
| `tests/contracts/test_serialization.py` | 24 | 24 |
| `tests/unit/test_market_tick.py` | 14 | 14 |
| `tests/contracts/test_package_import.py` | 5 | 5 |
| `tests/contracts/test_synthetic_fixtures.py` | 3 | 3 |
| **Razem** | **720** | **588** |

Liczby obejmują przypadki parametryzowane. Nieuruchomione: **0**. Pominięte: **0**. `test_documentation.py` rośnie z liczbą plików `.md`.

## 3. Zmiany istniejących testów
Porównanie `pytest --collect-only` (588 identyfikatorów na `f0c36e9` → 720): brakuje dokładnie dwóch,
oba to zmiany nazwy, nie usunięcia:

| Identyfikator na `f0c36e9` | Teraz | Powód |
|---|---|---|
| `test_audit1_phase0.py::TestA01ExactProduct::test_product_needing_more_than_18_places_has_no_valid_value` | `…::test_small_product_rounded_to_18_places_rejected` | nazwa i komentarz przeczyły DEC-020; asercje bez zmian ([KOREKTA2_RAPORT.md](KOREKTA2_RAPORT.md) §2) |
| `test_audit1_phase0.py::TestA03TimestampInputTypes::test_unsupported_types_rejected[<memory at 0x…>]` | `…[memoryview(b'2026-01-01T00:00:00Z')]` | identyfikator zawierał adres pamięci (zmienny między uruchomieniami); funkcja `_stable_id` daje stały identyfikator; test bez zmian |

Żaden test nie został usunięty ani osłabiony; konfiguracja pytest, Ruff i mypy bez zmian.

`tests/contracts/test_documentation.py::test_relative_links_resolve` pomija teraz kod Markdown (w
linii i bloki) przy wyszukiwaniu odnośników, bo Markdown nie tworzy w nim linków; wcześniej wzorzec
formatu czasu w kodzie był zgłaszany jako uszkodzony link. Odnośniki w zwykłym tekście są nadal
sprawdzane — mutacja M11 (uszkodzony link w AGENTS.md) jest wykrywana; jedno rzeczywiste wystąpienie
takiego „linku” w zwykłym tekście (`FAZA0_KOREKTA2_DECYZJE.md`) oznaczono jako kod.

## 4. Próby przed/po
`command_logs/08_probes_before_after.txt` (skrypt na końcu pliku): K1-01 i warianty — przed:
przyjmowane jako epoch, po: `ValidationError` („numeric timestamps are not accepted”); zapisy spoza
profilu — po: `ValidationError` („timestamp text must have the form …”); profil RFC 3339 —
przyjmowany na obu ścieżkach; `1E-10 × 1E-10` — przed: odrzucane, po: przyjmowane (`1E-20`).
Próby audytu 1 na korekcie 2: `command_logs/10_audit1_probes.txt`.

## 5. Test mutacyjny
16 cofnięć (5 poprawek korekty 2: M12–M16; 11 poprawek korekty 1: M1–M11, zaktualizowanych do obecnego kodu), zestaw bazowy 720 zaliczonych — **16/16 wykrytych**, od 1 do 18 niezaliczonych testów na mutację (M10: 249 niezaliczonych i 98 błędów, bo blokowany zapis dotyka każdego pola czasu); pliki przywrócone bajt w bajt (`command_logs/09_mutation_check.txt`, zawiera kod skryptu). Nie jest to pełne badanie mutacyjne wszystkich możliwych zmian.

## 6. Odtworzenie w czystym środowisku
**ZALICZONE.** Nowy klon gałęzi `task/faza0-korekta2` w commicie `73263fa`, nowe `.venv`, Windows PowerShell 5.1, polecenia skopiowane dosłownie z DEVELOPMENT.md §2–§6 (`command_logs/07_clean_reproduction.txt`):

| Krok | Wynik |
|---|---|
| `py -3.14 -m venv .venv`; `pip install --upgrade pip==26.2.2`; `pip install -c requirements-dev.lock -e ".[dev]"` | kod 0 |
| `pytest` | **720 zaliczonych**, 0 niezaliczonych, 0 pominiętych |
| `ruff check .` / `ruff format --check .` | bez uwag / 64 pliki sformatowane |
| `mypy` | bez błędów (31 plików) |
| test importu `-I` | `0.0.2 2` |
| zainstalowane pakiety vs `requirements-dev.lock` | identyczne (17 pakietów) |
| próby korekty 2 (K1-01 i warianty, profil RFC 3339, `1E-10 × 1E-10`) | jak w `08_probes_before_after.txt` (AFTER): epoch odrzucany, profil przyjmowany, `1E-20` przyjmowane |
| próby audytu 1 | 12 × `ValidationError`; A-04 — równość snapshotów (zamierzone) |
| `git status` po wszystkich krokach | czysty |

Wszystkie 11 kodów wyjścia: 0.
