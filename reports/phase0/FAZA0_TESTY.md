# FAZA 0 — raport testów

Data wykonania: 2026-10-22. Środowisko: Windows 11 Home x64 (10.0.26200), Python 3.14.5,
pip 26.2.2, pytest 9.1.1, Ruff 0.17.1, mypy 2.4.0, pydantic 2.14.1.
Wszystkie kontrole uruchomiono z wyłączoną zmienną `PYTHONOPTIMIZE` (DEC-018).

## 1. Kontrole w katalogu roboczym
Logi (ścieżki lokalne zastąpione `<REPO>`): `command_logs/02_…06_*.txt`.

| # | Polecenie | Wynik | Log |
|---|---|---|---|
| 1 | `python -m pytest -v` | **277 zaliczonych**, 0 niezaliczonych, 0 pominiętych, 0 xfail, 0 błędów; kod wyjścia 0 | `02_pytest.txt` |
| 2 | `python -m ruff check .` | `All checks passed!`; kod 0 | `03_ruff_check.txt` |
| 3 | `python -m ruff format --check .` | `42 files already formatted` (27 plików Python + pliki Markdown/TOML, które Ruff 0.17 również sprawdza); kod 0 | `04_ruff_format_check.txt` |
| 4 | `python -m mypy` | `Success: no issues found in 27 source files`; kod 0 | `05_mypy.txt` |
| 5 | `python -I -c "import market_intelligence, market_intelligence.core.models as m; print(market_intelligence.__version__, m.SCHEMA_VERSION)"` | `0.0.1 1`; kod 0 | `06_import_check.txt` |

`python` = `.\.venv\Scripts\python.exe` (w logach z Git Bash: `./.venv/Scripts/python.exe`).

## 2. Liczba testów wg pliku
| Plik | Testy |
|---|---|
| `tests/unit/test_candle.py` | 53 |
| `tests/unit/test_market_event.py` | 51 |
| `tests/unit/test_instrument.py` | 43 |
| `tests/unit/test_trade.py` | 37 |
| `tests/unit/test_primitives.py` | 25 |
| `tests/unit/test_data_quality.py` | 24 |
| `tests/contracts/test_serialization.py` | 22 |
| `tests/unit/test_market_tick.py` | 14 |
| `tests/contracts/test_package_import.py` | 5 |
| `tests/contracts/test_synthetic_fixtures.py` | 3 |
| **Razem** | **277** |

Liczby obejmują przypadki parametryzowane. Testy nieuruchomione: **0**. Pominięte: **0**.

## 3. Odtworzenie od zera z czystego klonu (Windows PowerShell 5.1)
Polecenia z [docs/DEVELOPMENT.md](../../docs/DEVELOPMENT.md) §2–§6 wykonane w nowym klonie
repozytorium (nowe `.venv`, instalacja z `requirements-dev.lock`).
Wynik i log: sekcja 3a poniżej oraz `command_logs/07_fresh_clone_reproduction.txt`.

### 3a. Wynik
OCZEKUJE — uzupełniane po pierwszym commicie (odtworzenie wymaga commita do sklonowania)

## 4. Test mutacyjny (kontrola jakości testów)
Wyłączenie każdej z 8 kluczowych reguł walidacji powodowało niepowodzenie 1–11 testów.
Szczegóły: `command_logs/09_mutation_check.txt`. Wykonany na 275 testach (przed dodaniem
2 testów naiwnych granic świecy); kod źródłowy po teście przywrócony i zweryfikowany.

## 5. Obserwacje
- Pierwsze uruchomienie pytest zakończyło się błędem konfiguracji
  (`PytestConfigWarning: assertions … will be ignored`), ponieważ systemowa zmienna
  `PYTHONOPTIMIZE=2` wyłącza `assert`. To zamierzone zachowanie zabezpieczenia
  (`filterwarnings = error`). Po wyłączeniu zmiennej dla procesu wszystkie testy przeszły.
- Żaden test nie łączy się z siecią; dane testowe są syntetyczne (`DataSource.SYNTHETIC`).
