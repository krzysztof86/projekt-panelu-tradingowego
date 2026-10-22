# PROJECT_STATE — aktualny stan prac

> Jedyne autorytatywne podsumowanie stanu projektu. Aktualizowane przy każdym przekazaniu pracy.

| Pole | Wartość |
|---|---|
| Ostatnia aktualizacja | 2026-10-22 |
| Aktualna faza | **FAZA 0 — korekta 2 zakończona, oczekuje na ponowny niezależny audyt.** FAZA 0 **nie została przyjęta** (audyt 2: „nie rekomenduję jeszcze bezwarunkowego odbioru”). |
| Ostatni ukończony etap | Korekta 2 FAZY 0: K1-01 audytu 2, profil RFC 3339, rozdzielona dziedzina Decimal, decyzje użytkownika |
| Następne zatwierdzone zadanie | **Ponowny niezależny audyt FAZY 0** (materiały: „Raporty”), następnie decyzja użytkownika o odbiorze. FAZA 1 **nie jest zatwierdzona** i nie ma zdefiniowanego zakresu (OQ-07). |
| Ostatni zweryfikowany commit | `73263fa` (szczegóły: sekcja 5) |
| Raporty | Korekta 2: [reports/phase0/korekta2/](../reports/phase0/korekta2/) — zacznij od `KOREKTA2_RAPORT.md`. Audyt 2: [reports/phase0/audyt2/](../reports/phase0/audyt2/). Wcześniejsze: korekta 1, audyt 1, FAZA 0 w [reports/phase0/](../reports/phase0/). |
| Wymagania i decyzje użytkownika | [requirements/](requirements/) — specyfikacja FAZY 0, zlecenie korekty 1, decyzje z korekty 2 |

## 1. Działająca implementacja
- Pakiet `market_intelligence` 0.0.2 (instalacja editable), Python 3.14 (`>=3.14,<3.15`).
- Kontrakty danych, schemat w wersji 2: `Instrument`, `MarketTick`, `Candle`, `Trade`,
  `DataQuality`, `MarketEvent` (+ `MetricValue`) z walidacją — [DATA_CONTRACTS.md](DATA_CONTRACTS.md).
  Dziedziny Decimal (czynniki ≤ 18 miejsc, `value_usdt` ≤ 36 miejsc, |x| < 1E+20), dokładna i
  niezależna od kontekstu arytmetyka `Trade`, ścisły znacznik wersji, czas tylko jako `datetime`
  lub tekst w profilu RFC 3339, walidowane tworzenie zmienionych rekordów.
- `core.clock.ensure_utc`.
- Testy jednostkowe, kontraktowe, regresji audytów 1 i 2, granic `core` i odnośników dokumentacji;
  konfiguracja Ruff i mypy (strict).

## 2. Niezrealizowane (PLANOWANE)
Konektory Bybit/Binance (REST/WebSocket), Market Data Quality, storage SQLite, detektory D1–D3,
silnik statusów zdarzeń, replay, Market Scanner L1, GUI PySide6. Pakiety `core.config` i
`core.events` są puste (zarezerwowane).

## 3. Wynik testów (2026-10-22, Windows 11 x64, Python 3.14.5)
| Kontrola | Wynik |
|---|---|
| pytest | **720 zaliczonych**, 0 niezaliczonych, 0 pominiętych (na `f0c36e9`: 588) |
| Ruff lint | bez uwag |
| Ruff format check | bez uwag |
| mypy (strict) | bez błędów (31 plików) |
| Import pakietu (`-I`) | `0.0.2 2` |
| Test mutacyjny korekty 2 | 16/16 cofniętych poprawek wykrytych |
| Odtworzenie w czystym klonie | zaliczone (commit `73263fa`, PowerShell 5.1, 720 testów) |

Szczegóły i polecenia: [reports/phase0/korekta2/KOREKTA2_TESTY.md](../reports/phase0/korekta2/KOREKTA2_TESTY.md).

## 4. Znane błędy, blokery, ryzyka
- Znane błędy: brak otwartych znanych błędów kodu. K1-01 audytu 2 usunięte **w ocenie wykonawcy** —
  zamknięcie potwierdza ponowny audyt.
- Blokery: brak dla ponownego audytu. Dla odbioru FAZY 0: wynik ponownego audytu i decyzja
  użytkownika. Dla kolejnej fazy: brak zatwierdzonego zakresu (OQ-07).
- Ryzyka: dziedziny Decimal vs rzeczywiste dane giełd (OQ-14); koszt rewalidacji (OQ-15);
  kontrole braku I/O są ograniczone (DEC-023); profil czasu węższy niż ISO 8601 — normalizacja w
  konektorach.
- Środowisko: systemowa zmienna `PYTHONOPTIMIZE=2` wyłącza `assert`; kontrole wymagają
  `$env:PYTHONOPTIMIZE = $null` (DEC-018, OQ-13).
- Szczegóły: [reports/phase0/korekta2/KOREKTA2_RAPORT.md](../reports/phase0/korekta2/KOREKTA2_RAPORT.md) §4.

## 5. Stan Git
- Gałąź robocza: `task/faza0-korekta2` (od `task/faza0-korekta1` = `f0c36e9`); `main` = `origin/main` = `2fcc5f7`; `origin/task/faza0-korekta1` = `f0c36e9`. Gałąź `task/faza0-korekta2` wypchnięta na
  `origin/task/faza0-korekta2` 2026-10-22 na polecenie użytkownika (bez scalania do `main`).
- Ostatni zweryfikowany commit: **`73263fac89e0d721414522d0ca6afa4ed08dfdb3`** (`73263fa`) — kod, testy i dokumentacja korekty 2;
  odtworzony w czystym klonie. Kolejne commity zmieniają tylko ten plik i `reports/phase0/korekta2/`
  — sprawdzenie: `git diff --stat 73263fa HEAD`.
- Scalenie do `main` i każdy kolejny `git push`: wyłącznie na polecenie użytkownika.
- Drzewo robocze po przekazaniu: czyste (`git status`).

## 6. Decyzje
- **ACCEPTED:** DEC-001, DEC-014, DEC-017 (wymagania); DEC-004, DEC-005, DEC-010, DEC-020,
  DEC-021, DEC-022, DEC-026 (użytkownik, 2026-10-22).
- **PROPOSED** (czekają na rozstrzygnięcie użytkownika; audyt 2 nie wskazał ich jako blokujących):
  lista z rekomendacjami — [DECISIONS.md](DECISIONS.md), sekcja „Decyzje wymagające rozstrzygnięcia
  użytkownika”.
- Otwarte kwestie: OQ-01 – OQ-15 — [DECISIONS.md](DECISIONS.md#otwarte-kwestie).
