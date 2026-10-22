# DECISIONS — decyzje techniczne i otwarte kwestie

Statusy: **ACCEPTED** (zatwierdzone przez użytkownika / wymagania), **PROPOSED** (propozycja
wykonawcy, czeka na zatwierdzenie w audycie), **SUPERSEDED** (zastąpione — wskazać następcę).
Decyzji ACCEPTED nie wolno zmieniać bez zgody użytkownika. Zmiana statusu PROPOSED →
ACCEPTED wymaga zatwierdzenia przez użytkownika/audytora i wpisu daty.

Źródło „wymagania FAZY 0” oznacza specyfikację zadania FAZY 0 przekazaną przez użytkownika
(2026-10-22); jej istotna treść jest odzwierciedlona w tym pliku i w ARCHITECTURE.md.

## Rejestr decyzji

### DEC-001 — Architektura i stos technologiczny
- Data: 2026-10-22 · Status: **ACCEPTED** (wymagania FAZY 0)
- Problem: wybór architektury i narzędzi.
- Decyzja: modularny monolit w układzie `src/`; Python na Windows 11; Pydantic v2, pytest,
  mypy, Ruff, `pyproject.toml`; docelowo PySide6 (GUI) i SQLite; dokumentacja Markdown w Git.
- Uzasadnienie: wymagania użytkownika; pojedyncza aplikacja desktopowa.
- Konsekwencje: PySide6 i SQLite nie są jeszcze zależnościami (instalacja w fazach, które ich użyją).

### DEC-002 — Wersja Pythona
- Data: 2026-10-22 · Status: **PROPOSED**
- Problem: jedyny dostępny interpreter to Python 3.14.5.
- Decyzja: `requires-python = ">=3.14"`; mypy i Ruff celują w 3.14.
- Uzasadnienie: deklarować tylko wersję faktycznie przetestowaną.
- Konsekwencje: przed fazą GUI należy potwierdzić dostępność kół PySide6 dla 3.14 (OQ-06).

### DEC-003 — Reprezentacja wartości finansowych
- Data: 2026-10-22 · Status: **PROPOSED** (użycie `Decimal` jest wymaganiem — ACCEPTED; szczegóły poniżej są propozycją)
- Problem: uniknięcie utraty precyzji.
- Decyzja: `Decimal`; wejście tylko `Decimal`/`int`/`str`; `float` i `bool` odrzucane;
  NaN/±Infinity odrzucane; JSON jako string.
- Uzasadnienie: `float` wprowadza błąd binarny niezauważalnie; giełdy podają liczby jako tekst.
- Konsekwencje: konektory muszą przekazywać tekst z API bez konwersji przez `float`.

### DEC-004 — Czas
- Data: 2026-10-22 · Status: **PROPOSED** (UTC i odrzucanie czasu naiwnego — ACCEPTED jako wymaganie)
- Problem: niejednoznaczność stref i jednostek czasu.
- Decyzja: tylko świadome `datetime`/ISO 8601 z przesunięciem, normalizacja do UTC;
  odrzucanie znaczników liczbowych (s/ms/µs) i tekstów numerycznych.
- Uzasadnienie: jednostki epoch musiałyby być zgadywane — wymagania zabraniają założeń.
- Konsekwencje: konwersja epoch → `datetime` w konektorach, jawnie.

### DEC-005 — Niemutowalność, nieznane pola, wersjonowanie schematu
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `frozen=True`, `extra="forbid"`; `schema_version: Literal[1]` w rekordach
  najwyższego poziomu (Instrument, MarketTick, Candle, Trade, MarketEvent); obiekty wartości
  (`DataQuality`, `MetricValue`) bez własnej wersji.
- Uzasadnienie: wymagania (niemutowalność, wersjonowanie); wykrywanie literówek i danych z innego schematu.
- Konsekwencje: każda niekompatybilna zmiana kontraktu podnosi `SCHEMA_VERSION`; strategia migracji danych zapisanych w SQLite — do ustalenia przy module storage.

### DEC-006 — Tożsamość instrumentu
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: tożsamość = (exchange, market_type, symbol); `instrument_id` =
  `<EXCHANGE>:<MARKET_TYPE>:<SYMBOL>`; symbol przechowywany dosłownie; `:` i białe znaki
  zabronione w symbolu; brak kontroli `symbol == base + quote`.
- Uzasadnienie: brak niejawnego łączenia giełd; zachowanie semantyki symboli giełdowych.
- Konsekwencje: `MarketEvent` odwołuje się do instrumentu przez `instrument_id` (OQ-11).

### DEC-007 — Świece
- Data: 2026-10-22 · Status: **PROPOSED** (semantyka `[start, end)` — ACCEPTED jako wymaganie)
- Decyzja: `end - start == interval.duration`; `start` wyrównany do wielokrotności interwału
  od epoki Unix; interwały: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d.
- Uzasadnienie: wykrywanie błędnie zbudowanych świec; interwały o stałej długości.
- Konsekwencje: założenie wyrównania do epoki dla świec giełdowych wymaga potwierdzenia w dokumentacji giełd (OQ-03 obejmuje weryfikację formatów); interwały tygodniowe/miesięczne nieobsługiwane.

### DEC-008 — Zarezerwowane pakiety `core.config`, `core.events`; zawartość `core.clock`
- Data: 2026-10-22 · Status: **PROPOSED**
- Problem: wymagana struktura zawiera katalogi bez zadań w FAZIE 0; zakaz tworzenia atrap.
- Decyzja: `core.config` i `core.events` zawierają tylko `__init__.py` z opisem; `core.clock`
  zawiera `ensure_utc` i `UTC_EPOCH` używane przez kontrakty.
- Konsekwencje: MODULE_MAP oznacza `config` i `events` jako ZAREZERWOWANE.

### DEC-009 — Przyczyna w DataQuality
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `reason` wymagane dla każdego statusu poza `VALID`; dozwolone dla `VALID`.
- Uzasadnienie: stan zdegradowany zawsze wyjaśniony.

### DEC-010 — Wartość transakcji
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `Trade.value_usdt` musi być równe `price * quantity` dokładnie (precyzja 100 cyfr).
- Uzasadnienie: dla kontraktu liniowego USDT wartość = cena × ilość aktywa bazowego.
- Konsekwencje: konektor wylicza wartość; zaokrąglona wartość z giełdy zostałaby odrzucona.

### DEC-011 — Niezmienniki MarketEvent
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `window_start < window_end <= detected_at`; `rejection_reason` ⇔ `REJECTED`;
  `VERIFIED` wymaga jakości `VALID`; wartości jako krotki `MetricValue(name, value, unit)`,
  min. 1, unikalne nazwy.
- Uzasadnienie: przyczynowość (brak look-ahead), jednoznaczność statusów, wiele metryk dla D3.

### DEC-012 — Znormalizowany status kontraktu
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `ContractStatus` = `PRE_LAUNCH`, `TRADING`, `SETTLING`, `CLOSED`; mapowanie
  statusów giełdowych w konektorach (FAZA z konektorami).
- Konsekwencje: mapowanie jest stratne i niezweryfikowane (OQ-03).

### DEC-013 — Źródło danych
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `DataSource` = `REST`, `WEBSOCKET`, `REPLAY`, `SYNTHETIC`; dane testowe zawsze `SYNTHETIC`.

### DEC-014 — Dokumentacja niezależna od agenta AI
- Data: 2026-10-22 · Status: **ACCEPTED** (wymagania FAZY 0)
- Decyzja: `AGENTS.md` jedynym punktem wejścia; `CLAUDE.md` i `.github/copilot-instructions.md`
  tylko wskazują AGENTS.md; hierarchia źródeł prawdy jak w AGENTS.md §2; stan wyłącznie w
  `docs/PROJECT_STATE.md`.

### DEC-015 — Identyfikator zdarzenia
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `event_id` (UUID) wymagany i dostarczany przez producenta; model niczego nie losuje.
- Uzasadnienie: deterministyczne odtwarzanie. Schemat wyznaczania (np. UUIDv5 z danych zdarzenia) — OQ-09.

### DEC-016 — Przypinanie zależności
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: bezpośrednie zależności przypięte `==` w `pyproject.toml`; komplet (z przechodnimi)
  w `requirements-dev.lock` używanym jako constraints; build backend `setuptools==84.2.1`.
- Wersje: pydantic 2.14.1, pytest 9.1.1, mypy 2.4.0, ruff 0.17.1, pip 26.2.2.

### DEC-017 — Wyłączenia z zakresu projektu
- Data: 2026-10-22 · Status: **ACCEPTED** (wymagania FAZY 0)
- Decyzja: brak automatycznego tradingu, brak prywatnych kluczy API, AGGR poza projektem
  (bez modyfikacji), wyłącznie publiczne API Bybit V5 i Binance USDⓈ-M.

### DEC-018 — Kontrole z włączonymi asercjami
- Data: 2026-10-22 · Status: **PROPOSED**
- Problem: w środowisku FAZY 0 systemowa zmienna `PYTHONOPTIMIZE=2` wyłącza `assert`.
- Decyzja: kontrole uruchamiane po `$env:PYTHONOPTIMIZE = $null` (tylko sesja); pytest z
  `filterwarnings = error` przerywa uruchomienie, gdy asercje są wyłączone. Bez zmian w systemie.

### DEC-019 — Końce linii
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `.gitattributes` z `* text=auto eol=lf`.

## Otwarte kwestie
| ID | Kwestia | Wpływ |
|---|---|---|
| OQ-01 | Definicja i zakres „Market Scanner L1” | Projekt modułu scanner |
| OQ-02 | Parametry D1–D3 (okna, progi, odniesienia, zachowanie przy jakości ≠ VALID) | Implementacja detektorów |
| OQ-03 | Weryfikacja formatów giełdowych z dokumentacją: mapowanie statusów (DEC-012), wyrównanie świec (DEC-007), pola strony agresora | Konektory |
| OQ-04 | Czy świece agregowane lokalnie potrzebują nowej wartości `DataSource` i czy `Candle` potrzebuje `received_at` | Kontrakt Candle |
| OQ-05 | Czy wymuszać `symbol == base_asset + quote_asset` | Kontrakt Instrument |
| OQ-06 | Zakres wersji Pythona (3.12/3.13?) i zgodność PySide6 z 3.14 | Środowisko, GUI |
| OQ-07 | Zakres FAZY 1 — nie zdefiniowany w repozytorium; wymaga zatwierdzenia użytkownika | Planowanie |
| OQ-08 | Licencja projektu | README, publikacja |
| OQ-09 | Reguły przejść statusów `MarketEvent` i schemat deterministycznego `event_id` | Silnik zdarzeń, replay |
| OQ-10 | Słownik jednostek `MetricValue.unit` (obecnie dowolny identyfikator wielkimi literami) | Kontrakt MarketEvent |
| OQ-11 | `MarketEvent` przez `instrument_id` (tekst) vs osadzony `Instrument` | Kontrakt MarketEvent, storage |
| OQ-12 | Treść dokumentacji Binance niezweryfikowana (HTTP 202) | EXCHANGE_API.md |
| OQ-13 | Czy zmienna systemowa `PYTHONOPTIMIZE=2` na komputerze deweloperskim ma zostać (decyzja właściciela komputera) | Środowisko |
