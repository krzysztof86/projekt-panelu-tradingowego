# FAZA 0 — ryzyka, ograniczenia i decyzje oczekujące

## 1. Ryzyka i problemy
| ID | Opis | Wpływ | Działanie / właściciel |
|---|---|---|---|
| R-01 | Systemowa zmienna `PYTHONOPTIMIZE=2` na komputerze deweloperskim wyłącza `assert` we wszystkich programach Python | Testy uruchomione bez `$env:PYTHONOPTIMIZE = $null` nie wystartują (zabezpieczenie); inne projekty na tym komputerze mogą mieć wyłączone asercje | Decyzja właściciela komputera (OQ-13); projekt nie zmienia ustawień systemowych |
| R-02 | Przetestowano wyłącznie Python 3.14.5 | Brak gwarancji dla innych wersji; ryzyko braku kół PySide6 dla 3.14 | Weryfikacja przed fazą GUI (DEC-002, OQ-06) |
| R-03 | Formaty giełdowe nie zostały zweryfikowane z dokumentacją (statusy, strona agresora, wyrównanie świec) | Możliwe korekty kontraktu (`ContractStatus`, DEC-007) w fazie konektorów | OQ-03; treść dokumentacji Binance niedostępna z tego środowiska (HTTP 202, OQ-12) |
| R-04 | Ścisła równość `value_usdt == price * quantity` | Gdyby giełda podawała zaokrągloną wartość, rekord zostałby odrzucony | Konektor wylicza wartość sam (DEC-010) |
| R-05 | Wymóg wyrównania świec do epoki Unix | Świece giełdowe niewyrównane (jeśli istnieją) zostaną odrzucone | Weryfikacja w fazie konektorów (DEC-007) |
| R-06 | Pakiety `core.config` i `core.events` puste | Brak — świadoma rezerwacja | DEC-008 |
| R-07 | Najnowsze wersje narzędzi (Ruff 0.17 sprawdza także Markdown/TOML) | Przyszłe aktualizacje narzędzi mogą zmienić wyniki | Wersje przypięte (DEC-016) |
| R-08 | Kontrola przejęcia bez kontekstu wykonana przez tego samego wykonawcę, który tworzył dokumentację | Możliwe niewykryte luki dla osoby trzeciej | Niezależny audyt (następne zadanie) |

## 2. Ograniczenia FAZY 0 (świadome)
- Brak komunikacji z giełdami, brak danych rynkowych, brak detektorów, GUI, bazy, alertów.
- Brak silnika przejść statusów `MarketEvent`.
- Brak zdalnego repozytorium; nic nie zostało opublikowane.
- Brak licencji (OQ-08).

## 3. Decyzje oczekujące na zatwierdzenie
Wszystkie decyzje w statusie **PROPOSED** w [docs/DECISIONS.md](../../docs/DECISIONS.md):
DEC-002, DEC-003, DEC-004, DEC-005, DEC-006, DEC-007, DEC-008, DEC-009, DEC-010, DEC-011,
DEC-012, DEC-013, DEC-015, DEC-016, DEC-018, DEC-019.
Szczególnej uwagi audytora wymagają reguły walidacji wykraczające dosłownie poza wymagania:
DEC-003 (odrzucanie `float`), DEC-004 (odrzucanie znaczników liczbowych), DEC-007 (wyrównanie
świec), DEC-009 (wymagana przyczyna), DEC-010 (równość wartości), DEC-011 (`VERIFIED` ⇒ `VALID`).

Otwarte kwestie OQ-01 – OQ-13: [docs/DECISIONS.md](../../docs/DECISIONS.md#otwarte-kwestie).
Najważniejsza dla kontynuacji: **OQ-07 — zakres FAZY 1 nie jest zdefiniowany ani zatwierdzony.**
