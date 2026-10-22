# AGENTS.md — punkt wejścia dla każdego programisty i agenta AI

Ten plik obowiązuje każdego wykonawcę (człowieka, Claude, Codex, Copilot, inne).
Historia rozmów z agentami **nie jest** źródłem prawdy — jest nim repozytorium.

## 1. Cel aplikacji
Natywna aplikacja Windows (PySide6) do wykrywania anomalii na kontraktach
**USDT Perpetual** (Bybit V5, Binance USDⓈ-M) z publicznych danych rynkowych.
Brak automatycznego handlu, brak prywatnych kluczy API. Szczegóły: [README.md](README.md).

## 2. Gdzie co jest
| Potrzebujesz | Plik |
|---|---|
| Aktualna faza, wynik testów, następne zadanie | [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md) |
| Architektura i granice modułów | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Który plik zmienić | [docs/MODULE_MAP.md](docs/MODULE_MAP.md) |
| Kontrakty danych | [docs/DATA_CONTRACTS.md](docs/DATA_CONTRACTS.md) |
| Decyzje i otwarte kwestie | [docs/DECISIONS.md](docs/DECISIONS.md) |
| Środowisko, testy, Git | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) |
| Przekazanie pracy | [docs/HANDOFF.md](docs/HANDOFF.md) |

Hierarchia źródeł prawdy (od najwyższej): 1) zatwierdzone wymagania i decyzje
(`docs/DECISIONS.md`, status ACCEPTED); 2) kod, testy, konfiguracja; 3) dokumentacja
techniczna `docs/`; 4) raporty `reports/`; 5) rozmowy z agentami (tylko kontekst).
Przy sprzeczności — **zgłoś rozbieżność**, nie rozstrzygaj jej samodzielnie.

## 3. Uruchomienie środowiska i testów (Windows PowerShell, katalog główny repo)
```powershell
$env:PYTHONOPTIMIZE = $null
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c requirements-dev.lock -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy
```
Pierwsza linia jest wymagana, gdy w systemie ustawiono `PYTHONOPTIMIZE` (wyłącza `assert`).
Szczegóły i diagnostyka: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## 4. Granice modułów
- `src/market_intelligence/core/` — czyste kontrakty i prymitywy, **bez I/O** (sieć, dysk, GUI, baza).
- Kierunek zależności: warstwy zewnętrzne zależą od `core`, nigdy odwrotnie.
- Moduły oznaczone w MODULE_MAP jako PLANOWANE **nie istnieją** — nie zakładaj ich obecności.

## 5. Zakazane bez wyraźnej zgody użytkownika
- Zmiana architektury, decyzji ACCEPTED lub zakresu fazy; rozpoczęcie kolejnej fazy.
- Zmiana kontraktu danych bez procedury z DEVELOPMENT.md (wersja schematu, testy, DATA_CONTRACTS.md).
- Automatyczny trading, obsługa prywatnych kluczy API, zapisywanie sekretów w repozytorium.
- Modyfikacja AGGR; `git push` / publikacja repozytorium; wyłączanie kontroli (testy, Ruff, mypy) w celu uzyskania zielonego wyniku.
- Zmiana globalnego środowiska Python lub ustawień systemowych.

## 6. Aktualizacja dokumentacji
Każda zmiana wymaga oceny, czy zaktualizować: PROJECT_STATE, MODULE_MAP, DATA_CONTRACTS,
ARCHITECTURE, DECISIONS, CHANGELOG, HANDOFF i testy. Aktualizuj razem z kodem, w tym samym
commicie. Nie zmieniaj dokumentów niezwiązanych ze zmianą. Dokumentuj tylko stan faktyczny.

## 7. Zakończenie zadania
Wykonaj checklistę z [docs/HANDOFF.md](docs/HANDOFF.md): wszystkie kontrole zielone,
PROJECT_STATE.md aktualny, raport w `reports/<faza>/`, stan Git opisany. Nie deklaruj
testów, których nie uruchomiono.
