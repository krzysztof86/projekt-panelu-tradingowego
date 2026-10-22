# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/). Wersje pakietu wg
`pyproject.toml`; wersja schematu danych wg `SCHEMA_VERSION` (docs/DATA_CONTRACTS.md).

## [Unreleased]

## [0.0.2] — 2026-10-22 — FAZA 0, korekta 2 (po audycie 2)
Schemat i pakiet bez zmiany numeru (DEC-026: schemat fazy nieprzyjętej). Ustalenia audytu:
`reports/phase0/audyt2/`; raport korekty: `reports/phase0/korekta2/`; decyzje użytkownika:
`docs/requirements/FAZA0_KOREKTA2_DECYZJE.md`.

### Naprawiono
- K1-01: tekst epoch bez części całkowitej (`.5`, `+.5`, `-.5`) i warianty wykładnicze (`.5e3`)
  nie są już interpretowane jako czas.
- Ciche obcinanie ułamka sekundy poniżej mikrosekundy (np. 9 cyfr) — tekst jest odrzucany.

### Zmieniono
- Pola czasu: tekst sprawdzany listą dozwolonych zapisów — profil RFC 3339
  `YYYY-MM-DDTHH:MM:SS[.ffffff](Z|+HH:MM|-HH:MM)` (DEC-004); odrzucane m.in. spacja zamiast `T`,
  małe `z`, `+0100`, czas bez sekund, godzina 24.
- `Trade.value_usdt`: dziedzina iloczynu do 36 miejsc po przecinku (`PositiveProductDecimal`,
  DEC-020) — iloczyn każdej pary poprawnych czynników < 1E+20 jest reprezentowalny.
- Statusy decyzji DEC-004, 005, 010, 020, 021, 022 → ACCEPTED; nowa DEC-026 (ACCEPTED).
- Dokumentacja dziedziny Decimal bez twierdzeń o pokryciu danych giełdowych; opis
  niezmiennika czasu `MarketEvent` w kodzie zgodny z dokumentacją.

### Dodano
- `tests/regression/test_audit2_phase0.py`; kopia audytu 2 w `reports/phase0/audyt2/`.

## [0.0.2] — 2026-10-22 — FAZA 0, korekta 1 (po audycie 1)
Schemat danych w wersji **2** (niekompatybilny z 1 — zaostrzenie walidacji, DEC-022).
Ustalenia audytu: `reports/phase0/audyt1/`; raport korekty: `reports/phase0/korekta1/`.

### Naprawiono
- A-01: `Trade.value_usdt` sprawdzany dokładnym iloczynem w prywatnym kontekście `decimal`,
  niezależnym od kontekstu wywołującego; błędy arytmetyki jako `ValidationError` (DEC-010).
- A-02: `schema_version` przyjmuje wyłącznie liczbę całkowitą (odrzuca `bool`, `float`,
  `Decimal`, `str`) na ścieżce Python i JSON.
- A-03: pola czasu przyjmują wyłącznie `datetime` lub `str`; `bytes` z epoch nie są już
  interpretowane jako czas.
- A-06: `ReasonText` odrzuca wszystkie separatory linii z `str.splitlines()` (w tym CR).
- A-07: `model_copy(update=...)` i `copy.replace` walidują wynik; zagnieżdżone kontrakty są
  zawsze ponownie walidowane.
- Luki znalezione przy odtwarzaniu audytu: `bytes` z ISO jako czas (E-1), `Decimal` jako
  znacznik wersji (E-2), dane binarne w polach tekstowych/enumach (E-3), separatory Unicode w
  `ReasonText` (E-4).
- Erratum `FAZA0_HANDOFF_AUDIT.md`: 16 (nie 14) plików `.py` w `src/`.

### Dodano
- Dziedzina wartości `Decimal`: ≤ 18 miejsc po przecinku, |x| < 1E+20 (DEC-020).
- `ContractModel.replace(**zmiany)` — walidowane tworzenie zmienionego rekordu (DEC-021).
- Odrzucanie danych binarnych w każdym polu kontraktów (DEC-004).
- Testy regresji `tests/regression/test_audit1_phase0.py`; kontrola granic `core`
  (`tests/contracts/test_core_boundaries.py`); test odnośników dokumentacji
  (`tests/contracts/test_documentation.py`).
- Specyfikacja FAZY 0 i zlecenie korekty w `docs/requirements/`; kopia materiałów audytu w
  `reports/phase0/audyt1/`.

### Zmieniono
- `requires-python` zawężone do `>=3.14,<3.15` (DEC-002).
- Dokumentacja: tożsamość instrumentu vs równość snapshotu (A-04), zakres kontroli braku I/O
  (A-05), granice gwarancji modelu, rejestr decyzji z listą do rozstrzygnięcia przez użytkownika.

## [0.0.1] — 2026-10-22 — FAZA 0
### Dodano
- Struktura repozytorium `src/` (modularny monolit), `pyproject.toml` z przypiętymi wersjami
  zależności, `requirements-dev.lock` (constraints), `.gitignore`, `.gitattributes`, `.env.example`.
- Kontrakty danych, schemat w wersji **1**: `Instrument`, `MarketTick`, `Candle`, `Trade`,
  `DataQuality`, `MarketEvent` (+ `MetricValue`) w `market_intelligence.core.models`.
- Prymityw `ensure_utc` w `market_intelligence.core.clock`.
- Zarezerwowane, puste pakiety `core.config` i `core.events` (DEC-008).
- Testy jednostkowe i kontraktowe (pytest), syntetyczne fixture'y JSON.
- Konfiguracja Ruff (lint + format) i mypy (strict, plugin Pydantic).
- Dokumentacja niezależna od agenta AI: AGENTS.md, CLAUDE.md, `.github/copilot-instructions.md`, `docs/*`.
- Raporty FAZY 0 w `reports/phase0/`.
