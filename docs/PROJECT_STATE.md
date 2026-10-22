# PROJECT_STATE — aktualny stan prac

> Jedyne autorytatywne podsumowanie stanu projektu. Aktualizowane przy każdym przekazaniu pracy.

| Pole | Wartość |
|---|---|
| Ostatnia aktualizacja | 2026-10-22 |
| Aktualna faza | **FAZA 0 — korekta 1 zakończona, oczekuje na ponowny niezależny audyt.** FAZA 0 **nie została przyjęta** (audyt 1: „wymaga poprawek”). |
| Ostatni ukończony etap | Korekta 1 FAZY 0: usterki A-01–A-07 audytu 1 i luki E-1–E-4 |
| Następne zatwierdzone zadanie | **Ponowny niezależny audyt FAZY 0** (materiały: sekcja „Raporty”). Następnie rozstrzygnięcie decyzji PROPOSED przez użytkownika. FAZA 1 **nie jest zatwierdzona** i nie ma zdefiniowanego zakresu (OQ-07). |
| Ostatni zweryfikowany commit | patrz sekcja 5 |
| Raporty | Korekta 1: [reports/phase0/korekta1/](../reports/phase0/korekta1/) — zacznij od `KOREKTA1_RAPORT.md`. Audyt 1: [reports/phase0/audyt1/](../reports/phase0/audyt1/). FAZA 0: [reports/phase0/](../reports/phase0/). |
| Wymagania | [requirements/FAZA0_SPECYFIKACJA.md](requirements/FAZA0_SPECYFIKACJA.md), [requirements/FAZA0_KOREKTA1_ZLECENIE.md](requirements/FAZA0_KOREKTA1_ZLECENIE.md) |

## 1. Działająca implementacja
- Pakiet `market_intelligence` 0.0.2 (instalacja editable), Python 3.14 (`>=3.14,<3.15`).
- Kontrakty danych, schemat w wersji 2: `Instrument`, `MarketTick`, `Candle`, `Trade`,
  `DataQuality`, `MarketEvent` (+ `MetricValue`) z walidacją — [DATA_CONTRACTS.md](DATA_CONTRACTS.md).
  Dziedzina Decimal (≤ 18 miejsc, |x| < 1E+20), dokładna i niezależna od kontekstu arytmetyka
  `Trade`, ścisły znacznik wersji, walidowane tworzenie zmienionych rekordów.
- `core.clock.ensure_utc`.
- Testy jednostkowe, kontraktowe, regresji audytu, granic `core` i odnośników dokumentacji;
  konfiguracja Ruff i mypy (strict).

## 2. Niezrealizowane (PLANOWANE)
Konektory Bybit/Binance (REST/WebSocket), Market Data Quality, storage SQLite, detektory D1–D3,
silnik statusów zdarzeń, replay, Market Scanner L1, GUI PySide6. Pakiety `core.config` i
`core.events` są puste (zarezerwowane).

## 3. Wynik testów (2026-10-22, Windows 11 x64, Python 3.14.5)
| Kontrola | Wynik |
|---|---|
| pytest | **588 zaliczonych**, 0 niezaliczonych, 0 pominiętych (przed korektą: 277) |
| Ruff lint | bez uwag |
| Ruff format check | bez uwag |
| mypy (strict) | bez błędów (30 plików) |
| Import pakietu (`-I`) | `0.0.2 2` |
| Test mutacyjny korekty | 11/11 cofniętych poprawek wykrytych |
| Odtworzenie w czystym klonie | patrz sekcja 5 i `KOREKTA1_TESTY.md` §6 |

Szczegóły i polecenia: [reports/phase0/korekta1/KOREKTA1_TESTY.md](../reports/phase0/korekta1/KOREKTA1_TESTY.md).

## 4. Znane błędy, blokery, ryzyka
- Znane błędy: brak otwartych znanych błędów kodu. Usterki A-01–A-07 audytu 1 są usunięte
  **w ocenie wykonawcy** — ich zamknięcie potwierdza ponowny audyt.
- Blokery: brak dla ponownego audytu. Dla kolejnej fazy: brak zatwierdzonego zakresu (OQ-07)
  i nierozstrzygnięte decyzje wpływające na kontrakty (DEC-020, DEC-010, DEC-022, DEC-021).
- Ryzyka: dziedzina Decimal vs rzeczywiste dane giełd (OQ-14); koszt rewalidacji (OQ-15);
  kontrole braku I/O są ograniczone (DEC-023).
- Środowisko: systemowa zmienna `PYTHONOPTIMIZE=2` wyłącza `assert`; kontrole wymagają
  `$env:PYTHONOPTIMIZE = $null` (DEC-018, OQ-13).
- Pełna lista: [reports/phase0/korekta1/KOREKTA1_RAPORT.md](../reports/phase0/korekta1/KOREKTA1_RAPORT.md) §7,
  [reports/phase0/FAZA0_RYZYKA.md](../reports/phase0/FAZA0_RYZYKA.md).

## 5. Stan Git
- Gałąź robocza: `task/faza0-korekta1` (od `main` = `2fcc5f7`); `main` i `origin/main` bez zmian; **brak push**.
- OCZEKUJE — uzupełniane w kolejnym commicie dokumentacyjnym, po odtworzeniu w czystym klonie (odtworzenie wymaga commita do sklonowania).

## 6. Otwarte decyzje
- Decyzje **PROPOSED** — wszystkie czekają na rozstrzygnięcie użytkownika; uszeregowana lista z
  rekomendacjami audytu: [DECISIONS.md](DECISIONS.md), sekcja „Decyzje wymagające rozstrzygnięcia
  użytkownika”. ACCEPTED pozostają wyłącznie DEC-001, DEC-014, DEC-017 (wymagania).
- Otwarte kwestie: OQ-01 – OQ-15 — [DECISIONS.md](DECISIONS.md#otwarte-kwestie).
