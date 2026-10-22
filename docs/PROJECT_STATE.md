# PROJECT_STATE — aktualny stan prac

> Jedyne autorytatywne podsumowanie stanu projektu. Aktualizowane przy każdym przekazaniu pracy.

| Pole | Wartość |
|---|---|
| Ostatnia aktualizacja | 2026-10-22 |
| Aktualna faza | **FAZA 0 — zakończona, oczekuje na niezależny audyt architektoniczny** |
| Ostatni ukończony etap | FAZA 0: fundament, kontrakty danych, testy, dokumentacja |
| Następne zatwierdzone zadanie | **Niezależny audyt architektoniczny FAZY 0.** FAZA 1 **nie jest zatwierdzona** i nie ma zdefiniowanego zakresu w repozytorium (OQ-07). |
| Ostatni zweryfikowany commit | `470eb03` (szczegóły: sekcja 5) |
| Raporty ostatniej fazy | [reports/phase0/](../reports/phase0/) — zacznij od `FAZA0_RAPORT.md` |

## 1. Działająca implementacja
- Pakiet `market_intelligence` 0.0.1 (instalacja editable), Python 3.14.
- Kontrakty danych, schemat w wersji 1: `Instrument`, `MarketTick`, `Candle`, `Trade`,
  `DataQuality`, `MarketEvent` (+ `MetricValue`) z walidacją — [DATA_CONTRACTS.md](DATA_CONTRACTS.md).
- `core.clock.ensure_utc`.
- Testy jednostkowe i kontraktowe; konfiguracja Ruff i mypy (strict).

## 2. Niezrealizowane (PLANOWANE)
Konektory Bybit/Binance (REST/WebSocket), Market Data Quality, storage SQLite, detektory D1–D3,
silnik statusów zdarzeń, replay, Market Scanner L1, GUI PySide6. Pakiety `core.config` i
`core.events` są puste (zarezerwowane).

## 3. Wynik testów (2026-10-22, Windows 11 x64, Python 3.14.5)
| Kontrola | Wynik |
|---|---|
| pytest | **277 zaliczonych**, 0 niezaliczonych, 0 pominiętych |
| Ruff lint | bez uwag |
| Ruff format check | bez uwag |
| mypy (strict) | bez błędów (27 plików) |
| Import pakietu (`-I`) | `0.0.1 1` |
| Odtworzenie z czystego klonu | zaliczone (commit `470eb03`, PowerShell 5.1) |

Szczegóły i polecenia: [reports/phase0/FAZA0_TESTY.md](../reports/phase0/FAZA0_TESTY.md).

## 4. Znane błędy, blokery, ryzyka
- Znane błędy: brak.
- Blokery: brak dla audytu. Dla kolejnej fazy: brak zatwierdzonego zakresu (OQ-07).
- Środowisko: systemowa zmienna `PYTHONOPTIMIZE=2` wyłącza `assert`; kontrole wymagają
  `$env:PYTHONOPTIMIZE = $null` (DEC-018, OQ-13).
- Pełna lista ryzyk: [reports/phase0/FAZA0_RYZYKA.md](../reports/phase0/FAZA0_RYZYKA.md).

## 5. Stan Git
- Gałąź: `main`, śledzi `origin/main`.
- Zdalne repozytorium: `https://github.com/krzysztof86/projekt-panelu-tradingowego.git`
  (push wykonany 2026-10-22 na polecenie użytkownika). Kolejne `git push` — tylko za zgodą użytkownika (AGENTS.md §5).
- Ostatni zweryfikowany commit: **`470eb03`** (kod, testy, dokumentacja; odtworzony z czystego klonu). Następny commit uzupełnia tylko ten plik i `reports/phase0/` — sprawdzenie: `git diff --stat 470eb03 HEAD`.
- Drzewo robocze po przekazaniu: czyste (`git status`).

## 6. Otwarte decyzje
- Decyzje **PROPOSED** do zatwierdzenia w audycie: DEC-002 – DEC-013, DEC-015,
  DEC-016, DEC-018, DEC-019 — [DECISIONS.md](DECISIONS.md).
- Otwarte kwestie: OQ-01 – OQ-13 — [DECISIONS.md](DECISIONS.md#otwarte-kwestie).
