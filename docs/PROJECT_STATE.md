# PROJECT_STATE — aktualny stan prac

> Jedyne autorytatywne podsumowanie stanu projektu. Aktualizowane przy każdym przekazaniu pracy.

| Pole | Wartość |
|---|---|
| Ostatnia aktualizacja | 2026-10-22 |
| Aktualna faza | **FAZA 0 — korekta 3 zakończona, oczekuje na weryfikację audytora i decyzję użytkownika o odbiorze.** FAZA 0 **nie została przyjęta**. Audyt 3: „Rekomenduję odbiór po jednej dodatkowej poprawce obsługi błędu granicznego czasu” (K2-A01). |
| Ostatni ukończony etap | Korekta 3 FAZY 0: K2-A01 (surowy `OverflowError` przy normalizacji do UTC) |
| Następne zatwierdzone zadanie | **Weryfikacja korekty 3 przez audytora i decyzja użytkownika o odbiorze FAZY 0.** FAZA 1 **nie jest zatwierdzona** i nie ma zdefiniowanego zakresu (OQ-07). |
| Ostatni zweryfikowany commit | `f74cff1` (szczegóły: sekcja 5) |
| Raporty | Korekta 3: [reports/phase0/korekta3/](../reports/phase0/korekta3/) — zacznij od `KOREKTA3_RAPORT.md`. Audyt 3: [reports/phase0/audyt3/](../reports/phase0/audyt3/). Wcześniejsze korekty, audyty i raport FAZY 0: [reports/phase0/](../reports/phase0/). |
| Wymagania i decyzje użytkownika | [requirements/](requirements/) — specyfikacja FAZY 0, zlecenie korekty 1, decyzje z korekty 2 |

## 1. Działająca implementacja
- Pakiet `market_intelligence` 0.0.2 (instalacja editable), Python 3.14 (`>=3.14,<3.15`).
- Kontrakty danych, schemat w wersji 2: `Instrument`, `MarketTick`, `Candle`, `Trade`,
  `DataQuality`, `MarketEvent` (+ `MetricValue`) z walidacją — [DATA_CONTRACTS.md](DATA_CONTRACTS.md).
  Dziedziny Decimal (czynniki ≤ 18 miejsc, `value_usdt` ≤ 36 miejsc, |x| < 1E+20), dokładna i
  niezależna od kontekstu arytmetyka `Trade`, ścisły znacznik wersji, czas tylko jako `datetime`
  lub tekst w profilu RFC 3339, walidowane tworzenie zmienionych rekordów; błędne dane kończą się
  `ValidationError` (także czas bez odpowiednika w UTC).
- `core.clock.ensure_utc`.
- Testy jednostkowe, kontraktowe, regresji audytów 1–3, granic `core` i odnośników dokumentacji;
  konfiguracja Ruff i mypy (strict).

## 2. Niezrealizowane (PLANOWANE)
Konektory Bybit/Binance (REST/WebSocket), Market Data Quality, storage SQLite, detektory D1–D3,
silnik statusów zdarzeń, replay, Market Scanner L1, GUI PySide6. Pakiety `core.config` i
`core.events` są puste (zarezerwowane).

## 3. Wynik testów (2026-10-22, Windows 11 x64, Python 3.14.5)
| Kontrola | Wynik |
|---|---|
| pytest | **778 zaliczonych**, 0 niezaliczonych, 0 pominiętych (na `6c633aa`: 720) |
| Ruff lint | bez uwag |
| Ruff format check | bez uwag |
| mypy (strict) | bez błędów (32 pliki) |
| Import pakietu (`-I`) | `0.0.2 2` |
| Test mutacyjny korekty 3 | 17/17 cofniętych poprawek wykrytych |
| Odtworzenie w czystym klonie | zaliczone (commit `f74cff1`, PowerShell 5.1, 778 testów) |

Szczegóły i polecenia: [reports/phase0/korekta3/KOREKTA3_TESTY.md](../reports/phase0/korekta3/KOREKTA3_TESTY.md).

## 4. Znane błędy, blokery, ryzyka
- Znane błędy: brak otwartych znanych błędów kodu. K2-A01 usunięte **w ocenie wykonawcy** —
  zamknięcie potwierdza audytor.
- Blokery: brak dla weryfikacji. Dla odbioru FAZY 0: weryfikacja korekty 3 i decyzja użytkownika.
  Dla kolejnej fazy: brak zatwierdzonego zakresu (OQ-07).
- Ryzyka (przed zależnymi modułami, nie blokery FAZY 0 wg audytu 3): dziedziny Decimal vs dane
  giełd (OQ-14); koszt rewalidacji (OQ-15); przechowanie `value_usdt` do 56 cyfr (OQ-16);
  kontrole braku I/O są ograniczone (DEC-023); profil czasu węższy niż ISO 8601.
- Środowisko: systemowa zmienna `PYTHONOPTIMIZE=2` wyłącza `assert`; kontrole wymagają
  `$env:PYTHONOPTIMIZE = $null` (DEC-018, OQ-13).
- Szczegóły: [reports/phase0/korekta3/KOREKTA3_RAPORT.md](../reports/phase0/korekta3/KOREKTA3_RAPORT.md) §4.

## 5. Stan Git
- Gałąź robocza: `task/faza0-korekta3` (od `task/faza0-korekta2` = `6c633aa`); `main` = `origin/main` = `2fcc5f7`. Gałąź `task/faza0-korekta3` wypchnięta na
  `origin/task/faza0-korekta3` 2026-10-22 na polecenie użytkownika (bez scalania do `main`).
- Ostatni zweryfikowany commit: **`f74cff1f5137d656619726fdcba7d9866d2b1ad9`** (`f74cff1`) — kod, testy i dokumentacja korekty 3;
  odtworzony w czystym klonie. Kolejne commity zmieniają tylko ten plik i `reports/phase0/korekta3/`
  — sprawdzenie: `git diff --stat f74cff1 HEAD`.
- Scalenie do `main` i każdy kolejny `git push`: wyłącznie na polecenie użytkownika.
- Drzewo robocze po przekazaniu: czyste (`git status`).

## 6. Decyzje
- **ACCEPTED:** DEC-001, DEC-014, DEC-017 (wymagania); DEC-004, DEC-005, DEC-010, DEC-020,
  DEC-021, DEC-022, DEC-026 (użytkownik, 2026-10-22). Korekta 3 nie zmienia żadnej decyzji.
- **PROPOSED** (rozstrzygać przed modułami, które ich potrzebują — audyt 3, warunek 4): lista z
  rekomendacjami — [DECISIONS.md](DECISIONS.md), sekcja „Decyzje wymagające rozstrzygnięcia
  użytkownika”.
- Otwarte kwestie: OQ-01 – OQ-16 — [DECISIONS.md](DECISIONS.md#otwarte-kwestie).
