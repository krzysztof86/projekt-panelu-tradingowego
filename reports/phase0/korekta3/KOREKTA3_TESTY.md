# FAZA 0 — korekta 3: raport testów

Data: 2026-10-22. Środowisko: Windows 11 Home x64 (10.0.26200), Python 3.14.5, pip 26.2.2,
pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0, pydantic 2.14.1 (zgodne z `requirements-dev.lock`).
Kontrole z wyłączoną zmienną `PYTHONOPTIMIZE` (DEC-018).

## 1. Kontrole w katalogu roboczym (gałąź `task/faza0-korekta3`)
| # | Polecenie | Wynik | Log |
|---|---|---|---|
| 1 | `python -m pytest -v` | **778 zaliczonych**, 0 niezaliczonych, 0 pominiętych, 0 xfail, 0 błędów; kod 0 | `02_pytest.txt` |
| 2 | `python -m ruff check .` | `All checks passed!`; kod 0 | `03_ruff_check.txt` |
| 3 | `python -m ruff format --check .` | `70 files already formatted` (Python oraz Markdown/TOML); kod 0 | `04_ruff_format_check.txt` |
| 4 | `python -m mypy` | `Success: no issues found in 32 source files`; kod 0 | `05_mypy.txt` |
| 5 | `python -I -c "import market_intelligence, market_intelligence.core.models as m; print(market_intelligence.__version__, m.SCHEMA_VERSION)"` | `0.0.2 2`; kod 0 | `06_import_check.txt` |

`python` = `.\.venv\Scripts\python.exe` (w logach z Git Bash: `./.venv/Scripts/python.exe`).

## 2. Liczba testów
| Plik | Testy | Na `6c633aa` |
|---|---|---|
| `tests/regression/test_audit1_phase0.py` | 208 | 208 |
| `tests/regression/test_audit2_phase0.py` | 122 | 122 |
| `tests/regression/test_audit3_phase0.py` | 50 | — (nowy) |
| `tests/contracts/test_documentation.py` | 71 | 63 |
| pozostałe (`unit/`, `test_core_boundaries.py`, `test_serialization.py`, `test_package_import.py`, `test_synthetic_fixtures.py`) | 327 | 327 |
| **Razem** | **778** | **720** |

Liczby obejmują przypadki parametryzowane. Nieuruchomione: **0**. Pominięte: **0**. `test_documentation.py` rośnie z liczbą plików `.md`.

## 3. Zmiany istniejących testów
**Brak.** Porównanie `pytest --collect-only` (720 identyfikatorów na `6c633aa` → 778): wszystkie dotychczasowe identyfikatory istnieją; żaden test nie został zmieniony, usunięty ani osłabiony. Konfiguracja pytest, Ruff i mypy bez zmian.

## 4. Skuteczność nowych testów
Nowe testy uruchomione na kodzie sprzed poprawki (`utc.py` z `6c633aa`, odłożony przez `git stash`):
**29 niezaliczonych, 21 zaliczonych** (zaliczone to przypadki poprawnych dat granicznych i danych
skrajnych innych pól, które już wcześniej działały). Po poprawce: wszystkie zaliczone.

Próby przed/po: `command_logs/08_probes_before_after.txt` — przed: 8 wycieków `OverflowError`, po: 0.

## 5. Test mutacyjny
17 cofnięć (M17 — korekta 3: `OverflowError` znowu nieprzechwytywany; M12–M16 — korekta 2; M1–M11 — korekta 1; M10 dostosowana do nowego wcięcia w `utc.py`), zestaw bazowy 778 zaliczonych — **17/17 wykrytych** (M17: 29 niezaliczonych; pozostałe od 1 do 18, M10: 292 niezaliczone i 98 błędów); pliki przywrócone bajt w bajt (`command_logs/09_mutation_check.txt`, zawiera kod skryptu). Nie jest to pełne badanie mutacyjne wszystkich możliwych zmian.

## 6. Odtworzenie w czystym środowisku
**ZALICZONE.** Nowy klon gałęzi `task/faza0-korekta3` w commicie `f74cff1`, nowe `.venv`, Windows PowerShell 5.1, polecenia skopiowane dosłownie z DEVELOPMENT.md §2–§6 (`command_logs/07_clean_reproduction.txt`):

| Krok | Wynik |
|---|---|
| `py -3.14 -m venv .venv`; `pip install --upgrade pip==26.2.2`; `pip install -c requirements-dev.lock -e ".[dev]"` | kod 0 |
| `pytest` | **778 zaliczonych**, 0 niezaliczonych, 0 pominiętych |
| `ruff check .` / `ruff format --check .` | bez uwag / 70 plików sformatowanych |
| `mypy` | bez błędów (32 pliki) |
| test importu `-I` | `0.0.2 2` |
| zainstalowane pakiety vs `requirements-dev.lock` | identyczne (17 pakietów) |
| próby korekty 3 (K2-A01, skan wycieków) | 0 wycieków |
| próby korekty 2 i audytu 1 | wyniki jak w korekcie 2 (epoch odrzucany, profil RFC 3339 przyjmowany, 12 × `ValidationError`) |
| `git status` po wszystkich krokach | czysty |

Wszystkie 12 kodów wyjścia: 0.
