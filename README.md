# Market Intelligence Desktop

Natywna aplikacja Windows do wykrywania anomalii na kontraktach kryptowalutowych
**USDT Perpetual** na podstawie publicznych danych Bybit V5 i Binance USDⓈ-M Futures.

> **Stan: FAZA 0 — fundament.** Repozytorium zawiera wyłącznie kontrakty danych
> (modele Pydantic), testy i dokumentację. Nie ma jeszcze połączeń z giełdami,
> detektorów, bazy danych ani GUI. Aktualny stan: [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md).

## Docelowy zakres (planowany, jeszcze niezaimplementowany)
- Market Scanner L1.
- D1 — Price Velocity Detector; D2 — Relative Volume Detector; D3 — Delta/Price Divergence Detector.
- Market Data Quality; historia zdarzeń i deterministyczne odtwarzanie.
- Interfejs Windows w PySide6; przechowywanie w SQLite.

Poza zakresem projektu: automatyczne składanie zleceń, prywatne klucze API.
AGGR pozostaje osobnym narzędziem analizy Order Flow.

## Uruchomienie od zera (Windows PowerShell)
Wymagania: Windows 11 x64, Python 3.14 (launcher `py`), Git.

```powershell
git clone https://github.com/krzysztof86/projekt-panelu-tradingowego.git market-intelligence-desktop
cd market-intelligence-desktop
$env:PYTHONOPTIMIZE = $null
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -c requirements-dev.lock -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

Pełna instrukcja (lint, typy, diagnostyka, zasady Git): [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Dokumentacja
| Dokument | Zawartość |
|---|---|
| [AGENTS.md](AGENTS.md) | Zasady pracy dla każdego programisty i agenta AI |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architektura i granice modułów |
| [docs/DATA_CONTRACTS.md](docs/DATA_CONTRACTS.md) | Pola, typy, jednostki, walidacje |
| [docs/DETECTORS.md](docs/DETECTORS.md) | Specyfikacja przyszłych detektorów D1–D3 |
| [docs/EXCHANGE_API.md](docs/EXCHANGE_API.md) | Źródła danych i dokumentacja giełd |
| [docs/TEST_PLAN.md](docs/TEST_PLAN.md) | Zakres testów i kryteria odbioru |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Decyzje i otwarte kwestie |
| [docs/requirements/](docs/requirements/) | Zatwierdzone teksty wymagań (specyfikacja FAZY 0, zlecenia korekt) |
| [docs/MODULE_MAP.md](docs/MODULE_MAP.md) | Mapa kodu |
| [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md) | Aktualny stan prac |
| [docs/HANDOFF.md](docs/HANDOFF.md) | Procedura przekazania pracy |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Środowisko i workflow |
| [CHANGELOG.md](CHANGELOG.md) | Istotne zmiany |

## Licencja
Nie określono (otwarta kwestia OQ-08 w [docs/DECISIONS.md](docs/DECISIONS.md)).
