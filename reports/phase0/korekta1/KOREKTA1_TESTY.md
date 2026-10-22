# FAZA 0 — korekta 1: raport testów

Data: 2026-10-22. Środowisko: Windows 11 Home x64 (10.0.26200), Python 3.14.5, pip 26.2.2,
pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0, pydantic 2.14.1 (zgodne z `requirements-dev.lock`).
Wszystkie kontrole uruchomiono z wyłączoną zmienną `PYTHONOPTIMIZE` (DEC-018).

## 1. Kontrole w katalogu roboczym (gałąź `task/faza0-korekta1`)
Logi (ścieżki lokalne zastąpione `<REPO>`/`<USER_HOME>`): `command_logs/02…06_*.txt`.

| # | Polecenie | Wynik | Log |
|---|---|---|---|
| 1 | `python -m pytest -v` | **588 zaliczonych**, 0 niezaliczonych, 0 pominiętych, 0 xfail, 0 błędów; kod 0 | `02_pytest.txt` |
| 2 | `python -m ruff check .` | `All checks passed!`; kod 0 | `03_ruff_check.txt` |
| 3 | `python -m ruff format --check .` | `57 files already formatted` (pliki Python oraz Markdown/TOML, które Ruff 0.17 także sprawdza); kod 0 | `04_ruff_format_check.txt` |
| 4 | `python -m mypy` | `Success: no issues found in 30 source files`; kod 0 | `05_mypy.txt` |
| 5 | `python -I -c "import market_intelligence, market_intelligence.core.models as m; print(market_intelligence.__version__, m.SCHEMA_VERSION)"` | `0.0.2 2`; kod 0 | `06_import_check.txt` |

`python` = `.\.venv\Scripts\python.exe` (w logach z Git Bash: `./.venv/Scripts/python.exe`).

## 2. Liczba testów wg pliku
| Plik | Testy | Przed korektą |
|---|---|---|
| `tests/regression/test_audit1_phase0.py` | 208 | — (nowy) |
| `tests/unit/test_candle.py` | 53 | 53 |
| `tests/contracts/test_documentation.py` | 53 | — (nowy) |
| `tests/unit/test_market_event.py` | 51 | 51 |
| `tests/contracts/test_core_boundaries.py` | 48 | — (nowy) |
| `tests/unit/test_instrument.py` | 43 | 43 |
| `tests/unit/test_trade.py` | 37 | 37 |
| `tests/unit/test_primitives.py` | 25 | 25 |
| `tests/unit/test_data_quality.py` | 24 | 24 |
| `tests/contracts/test_serialization.py` | 24 | 22 |
| `tests/unit/test_market_tick.py` | 14 | 14 |
| `tests/contracts/test_package_import.py` | 5 | 5 |
| `tests/contracts/test_synthetic_fixtures.py` | 3 | 3 |
| **Razem** | **588** | **277** |

Testy nieuruchomione: **0**. Pominięte: **0**. Liczba `test_documentation.py` rośnie z liczbą plików `.md`.

Liczby obejmują przypadki parametryzowane. Przed korektą (commit `2fcc5f7`): **277**.

## 3. Zmiany istniejących testów (zlecenie pkt 5: bez osłabiania i usuwania)
Porównanie identyfikatorów testów `2fcc5f7` → korekta (`pytest --collect-only`): z 277
identyfikatorów brakuje dokładnie dwóch; żaden test nie został usunięty bez zastępstwa.

| Test (wersja audytowana) | Co się stało | Dlaczego nie jest to osłabienie |
|---|---|---|
| `test_package_import.py::test_core_has_no_io_dependencies` | zmiana nazwy na `test_core_import_does_not_load_io_libraries` | zakres rozszerzony: import wszystkich pakietów `core` zamiast `core.models`, 13 zamiast 10 zakazanych modułów; nazwa i opis odpowiadają faktycznemu zakresowi (A-05) |
| `test_serialization.py::test_decimal_survives_json_exactly[123456789012345678901234567890.123456789]` | parametr zastąpiony granicami dziedziny `0.000000000000000001` i `99999999999999999999.999999999999999999` | wartość z 30 cyframi całkowitymi jest poza dziedziną DEC-020; jej odrzucenie testuje `TestA01FinancialDomain`; nowe parametry sprawdzają serializację na obu granicach (38 cyfr) |
| `test_serialization.py::TestSchemaVersion::test_current_version` | oczekiwanie `1` → `2` | zmiana wersji schematu (DEC-022) |
| `test_serialization.py::TestSchemaVersion::test_other_versions_rejected` | parametry `[0, 2, "1", None]` → `[0, 1, 3, "2", None]` | `2` jest teraz wersją bieżącą; dodano odrzucenie wersji poprzedniej `1` i następnej `3`; tekst `"2"` zastępuje `"1"` |
| `test_package_import.py::test_import_in_isolated_interpreter` | oczekiwana wersja schematu z `SCHEMA_VERSION` zamiast literału `"1"` | sprawdza to samo, bez duplikowania stałej |
| `test_trade.py::TestValue::test_high_precision_product_is_exact` | nowe wartości: 38 cyfr znaczących, 18 miejsc (było 37 cyfr, 19 miejsc) | poprzedni iloczyn wypadł poza dziedzinę; nowy jest dłuższy i nadal odrzucany przez zaokrąglenie 28-cyfrowe |

Fixture `synthetic_contract_samples.json`: `schema_version` 1 → 2 (dane nadal syntetyczne).
Konfiguracja pytest, Ruff i mypy **bez zmian** (żadne reguły nie zostały wyłączone). Jedyny nowy
`# type: ignore[arg-type]` dotyczy stubów `copy.replace` w teście i jest opisany komentarzem.

## 4. Regresje audytu
208 testów w `tests/regression/test_audit1_phase0.py`, 48 w `test_core_boundaries.py`,
`test_documentation.py` — mapowanie ustaleń: [docs/TEST_PLAN.md](../../../docs/TEST_PLAN.md) §7.
Próby audytora po korekcie: wszystkie 12 prób dotyczących usterek kończą się `ValidationError`
z jawnym komunikatem; próba A-04 daje celowo ten sam wynik (równość snapshotów)
(`command_logs/08_audit_probes_before_after.txt`).

## 5. Test mutacyjny
Każdą z 11 poprawek cofnięto osobno (zestaw bazowy: 588 zaliczonych) — **11/11 wykrytych**, od 1 do 18 niezaliczonych testów na mutację; pliki przywrócone bajt w bajt (`command_logs/09_mutation_check.txt`, zawiera kod skryptu). Nie jest to pełne badanie mutacyjne wszystkich możliwych zmian.

## 6. Odtworzenie w czystym środowisku
OCZEKUJE — uzupełniane w kolejnym commicie dokumentacyjnym, po odtworzeniu w czystym klonie (odtworzenie wymaga commita do sklonowania).
