# DEVELOPMENT — praca z repozytorium

Wszystkie polecenia są dla **Windows PowerShell 5.1** i uruchamiane z katalogu głównego
repozytorium. Zostały sprawdzone na Windows 11 x64 z Pythonem 3.14.5 — dowód:
`reports/phase0/command_logs/07_fresh_clone_reproduction.txt`.

Polecenia wywołują interpreter środowiska wprost (`.\.venv\Scripts\python.exe`), więc nie
trzeba aktywować venv ani zmieniać polityki wykonywania skryptów.

## 1. Wymagania
- Windows 11 x64, Git.
- Python **3.14** z launcherem `py` (`py -0p` pokazuje zainstalowane wersje).
  Inne wersje nie były testowane (DEC-002, OQ-06).
- Dostęp do PyPI przy instalacji zależności.

## 2. Instalacja środowiska od zera
```powershell
$env:PYTHONOPTIMIZE = $null
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip==26.2.2
.\.venv\Scripts\python.exe -m pip install -c requirements-dev.lock -e ".[dev]"
```
- `$env:PYTHONOPTIMIZE = $null` usuwa zmienną **tylko w bieżącej sesji PowerShell**.
  Jest konieczne, jeśli w systemie ustawiono `PYTHONOPTIMIZE` (wyłącza instrukcje `assert`,
  przez co testy byłyby puste). Szczegóły w sekcji 9.
- Wersje bezpośrednich zależności są przypięte w `pyproject.toml` (`==`); wszystkie pakiety,
  także przechodnie, w `requirements-dev.lock`, używanym jako plik constraints (`-c`) (DEC-016).
- `-e` instaluje pakiet w trybie editable: zmiany w `src/` działają bez reinstalacji.

## 3. Testy
```powershell
.\.venv\Scripts\python.exe -m pytest
```
Konfiguracja w `pyproject.toml` (`[tool.pytest.ini_options]`): ostrzeżenia traktowane jako
błędy, `--strict-markers`, `--strict-config`. Wybrane testy: `... -m pytest tests\unit\test_candle.py -v`.

## 4. Kontrola stylu i typów
```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy
```
Automatyczne formatowanie: `.\.venv\Scripts\python.exe -m ruff format .`.
mypy działa w trybie `strict` z pluginem `pydantic.mypy` dla `src` i `tests`.

## 5. Test importu pakietu
```powershell
.\.venv\Scripts\python.exe -I -c "import market_intelligence, market_intelligence.core.models as m; print(market_intelligence.__version__, m.SCHEMA_VERSION)"
```
Oczekiwany wynik: `0.0.2 2` (wersja pakietu, wersja schematu danych). Flaga `-I` izoluje interpreter od bieżącego katalogu i zmiennych
`PYTHON*`, więc import działa wyłącznie dzięki instalacji editable. Ten sam test wykonuje
automatycznie `tests/contracts/test_package_import.py`.

## 6. Pełna kontrola przed commitem
Wszystkie poniższe muszą zakończyć się sukcesem (kod wyjścia 0):
```powershell
$env:PYTHONOPTIMIZE = $null
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy
```
Nie wolno wyłączać reguł, testów ani ostrzeżeń wyłącznie po to, by uzyskać zielony wynik.
Pojedyncze `# noqa` / `# type: ignore` są dopuszczalne tylko z kodem reguły i uzasadnieniem.

## 7. Gałęzie i commity
- Gałąź główna: `main`. Praca nad fazą lub zadaniem na gałęzi `phase/<n>-<opis>` lub
  `task/<opis>`, scalana do `main` po audycie.
- Commit = spójna zmiana kodu **razem z** testami i dokumentacją, której dotyczy.
- Komunikat commita: tryb rozkazujący, pierwsza linia ≤ 72 znaki, np.
  `Add Trade value validation`; w treści — uzasadnienie i odniesienia do DEC-xxx.
- Przed commitem: sekcja 6 musi być zielona.
- `git push` i publikowanie repozytorium tylko za zgodą użytkownika.
- Zakończenie końców linii: LF (wymuszone przez `.gitattributes`).

## 8. Procedury aktualizacji
### 8.1 Zmiana kontraktu danych (`src/market_intelligence/core/models/`)
1. Sprawdź w `docs/DECISIONS.md`, czy zmiana nie narusza decyzji ACCEPTED (jeśli tak — zgoda użytkownika).
2. Zmiana niekompatybilna wstecz (usunięcie/zmiana pola, zaostrzenie walidacji, zmiana
   formatu JSON) wymaga podniesienia `SCHEMA_VERSION` w `core/models/base.py` i typu `SchemaVersion`.
3. Dodaj/zmień testy w `tests/unit/` i `tests/contracts/` (regresje ustaleń audytów —
   `tests/regression/`); zaktualizuj fixture'y w
   `tests/fixtures/` (dane nadal syntetyczne i tak oznaczone).
4. Zaktualizuj `docs/DATA_CONTRACTS.md`, `docs/MODULE_MAP.md`, `CHANGELOG.md`; nową decyzję
   wpisz do `docs/DECISIONS.md`.
5. Uruchom pełną kontrolę (sekcja 6).

### 8.2 Aktualizacja dokumentacji
Przy każdej zmianie przejdź listę: PROJECT_STATE, MODULE_MAP, DATA_CONTRACTS, ARCHITECTURE,
DECISIONS, CHANGELOG, HANDOFF, powiązane testy. Aktualizuj tylko dokumenty, których zmiana
dotyczy. Dokumentuj stan faktyczny; elementy niezaimplementowane oznaczaj jako PLANOWANE.
Sprawdź, czy odnośniki względne w zmienionych plikach `.md` wskazują istniejące pliki.

### 8.3 Aktualizacja zależności
1. Zmień wersję w `pyproject.toml`.
2. W czystym środowisku: `py -3.14 -m venv .venv-new`, potem
   `.\.venv-new\Scripts\python.exe -m pip install -e ".[dev]"`.
3. Wygeneruj nowy lock: `.\.venv-new\Scripts\python.exe -m pip freeze --exclude-editable`
   i zastąp nim listę pakietów w `requirements-dev.lock` (zachowaj nagłówek z komentarzami).
4. Pełna kontrola (sekcja 6); wpis w `CHANGELOG.md`.

## 9. Diagnostyka problemów środowiskowych
| Objaw | Przyczyna / rozwiązanie |
|---|---|
| `PytestConfigWarning: assertions not in test modules or plugins will be ignored` (błąd uruchomienia pytest) | Ustawiono `PYTHONOPTIMIZE` (w środowisku FAZY 0: na poziomie systemu, wartość `2`). Uruchom `$env:PYTHONOPTIMIZE = $null` w bieżącej sesji. Nie zmieniaj zmiennej systemowej bez zgody właściciela komputera. Sprawdzenie: `.\.venv\Scripts\python.exe -c "import sys; print(sys.flags.optimize)"` → ma być `0`. |
| `py` nie znaleziono / brak 3.14 | Zainstaluj Python 3.14 z python.org z launcherem; sprawdź `py -0p`. |
| `python` otwiera Microsoft Store | Alias WindowsApps. Używaj `py -3.14` lub `.\.venv\Scripts\python.exe`. |
| `ModuleNotFoundError: market_intelligence` | Brak instalacji editable — powtórz krok instalacji z sekcji 2. |
| Błąd `Activate.ps1 cannot be loaded` | Polityka wykonywania skryptów. Aktywacja nie jest potrzebna — używaj pełnej ścieżki `.\.venv\Scripts\python.exe`. |
| `pip` nie może pobrać pakietów | Brak dostępu do PyPI / proxy. Sprawdź `.\.venv\Scripts\python.exe -m pip config list` i ustawienia sieci. |
| Ruff/mypy zgłaszają inne błędy niż w raporcie | Niezgodne wersje narzędzi. Porównaj `.\.venv\Scripts\python.exe -m pip freeze` z `requirements-dev.lock`. |
| Ostrzeżenia Git `LF will be replaced by CRLF` | Informacyjne; `.gitattributes` utrzymuje LF w repozytorium. |
