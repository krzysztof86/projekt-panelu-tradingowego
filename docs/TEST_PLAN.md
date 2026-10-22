# TEST_PLAN — zakres testów i kryteria odbioru

## 1. Zasady
- Framework: pytest (konfiguracja w `pyproject.toml`); ostrzeżenia = błędy.
- Dane testowe są **syntetyczne**: rekordy mają `source = SYNTHETIC`, pliki fixture'ów
  nazywają się `synthetic_*.json` i zawierają `"synthetic": true` (sprawdzane testem).
- Brak dostępu do sieci i giełd w testach.
- Testy nie mogą być wyłączane, pomijane (`skip`) ani oznaczane `xfail` w celu uzyskania zielonego wyniku.

## 2. Struktura
| Katalog | Zawartość |
|---|---|
| `tests/conftest.py` | Wspólne syntetyczne fixture'y (instrumenty, kwargs każdego modelu) |
| `tests/unit/` | Walidacja pojedynczych modeli i prymitywów |
| `tests/contracts/` | Serializacja JSON, wersja schematu, fixture'y JSON, import po instalacji editable, granice `core` (importy, wywołania, strażnik I/O w czasie wykonania), odnośniki dokumentacji |
| `tests/regression/` | Regresje ustaleń audytów: `test_audit1_phase0.py` (A-01–A-07, E-1–E-4) |
| `tests/fixtures/` | `synthetic_contract_samples.json` — przykładowe rekordy wszystkich kontraktów |

## 3. Pokrycie wymagań FAZY 0
| Wymaganie | Testy |
|---|---|
| Poprawne instrumenty Bybit i Binance | `unit/test_instrument.py::TestValidInstruments` |
| Identyczne symbole na różnych giełdach | `unit/test_instrument.py::TestIdentity::test_same_symbol_on_different_exchanges_is_different` |
| Odrzucenie Spot i COIN-M | `unit/test_instrument.py::TestScope::test_rejects_other_market_types` |
| Niewłaściwa waluta kwotowana | `unit/test_instrument.py::TestScope::test_rejects_other_quote_assets` |
| Nieprawidłowe ceny, ilości, obrót | `unit/test_market_tick.py::test_rejects_invalid_price`, `unit/test_trade.py::test_rejects_invalid_amounts`, `unit/test_candle.py::TestTurnover`, `TestOhlcConsistency::test_rejects_non_positive_or_non_finite_prices`, `unit/test_instrument.py::TestTickSize` |
| NaN i Infinity | `unit/test_primitives.py::TestDecimalFields::test_rejects_nan_and_infinity` oraz przypadki w testach modeli |
| Niespójne OHLC | `unit/test_candle.py::TestOhlcConsistency` |
| Obsługa UTC | `unit/test_primitives.py::TestEnsureUtc`, `TestDatetimeFields::test_normalizes_to_utc`, `unit/test_market_tick.py::test_timestamps_normalized_to_utc` |
| Odrzucenie naiwnego datetime | `TestEnsureUtc::test_rejects_naive`, `TestDatetimeFields::test_rejects_naive` (`test_primitives`); `test_rejects_naive_timestamps` (`test_market_tick`, `test_trade`); `TestWindow::test_rejects_naive` (`test_market_event`); `TestInterval::test_rejects_naive_bounds`, `TestHalfOpenInterval::test_contains_rejects_naive` (`test_candle`) |
| Brak opcjonalnego czasu giełdowego | `unit/test_market_tick.py::test_exchange_time_is_optional`, `contracts/test_serialization.py::test_missing_exchange_time_serialized_as_null` |
| Zachowanie Decimal przy serializacji | `contracts/test_serialization.py::test_decimal_survives_json_exactly`, `test_trade_value_precision_survives_json` |
| Kierunek agresora BUY/SELL | `unit/test_trade.py::test_aggressor_side`, `test_rejects_non_canonical_side` |
| Walidacja jakości danych | `unit/test_data_quality.py` |
| Poprawne i niepoprawne alerty | `unit/test_market_event.py::TestValidEvents`, `TestInvalidFields` |
| Poprawność przedziałów czasowych | `unit/test_candle.py::TestInterval`, `TestHalfOpenInterval`; `unit/test_market_event.py::TestWindow` |
| Rozróżnienie VERIFIED i REJECTED | `unit/test_market_event.py::TestVerifiedVersusRejected` |
| Import pakietu po instalacji editable | `contracts/test_package_import.py` + polecenie z DEVELOPMENT.md §5 |
| Brak danych ≠ zero | `unit/test_candle.py::TestTurnover::test_missing_is_not_zero`, `test_none_is_not_zero`, `test_zero_is_valid` |
| Wersjonowanie schematu | `contracts/test_serialization.py::TestSchemaVersion` |
| Niemutowalność, nieznane pola | `unit/test_instrument.py::TestImmutability` |

## 4. Kontrole statyczne
| Kontrola | Polecenie (PowerShell) |
|---|---|
| Testy | `.\.venv\Scripts\python.exe -m pytest` |
| Lint | `.\.venv\Scripts\python.exe -m ruff check .` |
| Format | `.\.venv\Scripts\python.exe -m ruff format --check .` |
| Typy | `.\.venv\Scripts\python.exe -m mypy` |
| Import | `.\.venv\Scripts\python.exe -I -c "import market_intelligence, market_intelligence.core.models as m; print(market_intelligence.__version__, m.SCHEMA_VERSION)"` |

Przed uruchomieniem: `$env:PYTHONOPTIMIZE = $null` (DEVELOPMENT.md §9).

## 5. Kryteria odbioru FAZY 0
1. Wszystkie testy zaliczone; 0 niezaliczonych, 0 pominiętych.
2. Ruff lint i format check bez uwag; mypy strict bez błędów.
3. Test importu zwraca `0.0.2 2`.
4. Odtworzenie środowiska od zera z czystego klonu repozytorium wg DEVELOPMENT.md daje ten sam wynik.
5. Wyniki zapisane w raporcie fazy (`reports/phase0/FAZA0_TESTY.md`; po korekcie 1:
   `reports/phase0/korekta1/KOREKTA1_TESTY.md`) z logami w katalogu `command_logs/` raportu.
6. Wszystkie testy regresji ustaleń audytu zaliczone (§7); żadne ustalenie nie jest zamknięte bez testu
   albo jawnego uzasadnienia w raporcie korekty.

## 6. Dodatkowa weryfikacja jakości testów
Test mutacyjny (ręczny): wyłączenie każdej kluczowej reguły walidacji musi spowodować
niepowodzenie co najmniej jednego testu. Wynik FAZY 0: `reports/phase0/command_logs/09_mutation_check.txt`.
Wynik korekty 1 (cofnięcie każdej poprawki osobno, 11 mutacji):
`reports/phase0/korekta1/command_logs/09_mutation_check.txt`. Test mutacyjny jest wykonywany na
zielonym zestawie bazowym; nie jest pełnym badaniem mutacyjnym wszystkich możliwych zmian.

## 7. Regresje audytu 1 FAZY 0
Plik: `tests/regression/test_audit1_phase0.py`. Ustalenia: `reports/phase0/audyt1/AUDYT_FAZY0.md`.

| Ustalenie | Klasa testów | Co sprawdza |
|---|---|---|
| A-01 dziedzina | `TestA01FinancialDomain` | próby audytora (101 miejsc, `1e999999`) → `ValidationError`; granice dziedziny przyjmowane, przekroczenia odrzucane; wartości ujemne metryk |
| A-01 dokładność | `TestA01ExactProduct` | iloczyn 38 cyfr; wynik zaokrąglony kontekstem 28 cyfr odrzucony; 6 wrogich kontekstów `decimal` (precyzja, zaokrąglanie, pułapki, wykładniki) — ten sam wynik i tylko `ValidationError`; kontekst wywołującego niezmieniony; 300 losowych przypadków z wyrocznią `Fraction` |
| A-02 | `TestA02SchemaVersion` | 5 modeli × ścieżka Python i JSON × `true`, `false`, `1.0`, `2.0`, `0`, `1`, `3`, `"2"`, `null`; `Decimal` |
| A-03 | `TestA03TimestampInputTypes` | `bytes` (epoch i ISO), `bytearray`, `memoryview`, `date`, `time`, `Decimal`, lista; `bytes` w każdym modelu; jawny komunikat dla nieobsługiwanych typów |
| A-04 | `TestA04InstrumentIdentity` | zmiana metadanych przy stałym `instrument_id`: równe ID, różne snapshoty, kolekcja kluczowana ID |
| A-05 | `tests/contracts/test_core_boundaries.py` | lista dozwolonych importów, zakazane wywołania, brak `model_construct` w `src/`, strażnik I/O w czasie wykonania |
| A-06 | `TestA06ReasonSingleLine` | 11 separatorów linii z `str.splitlines()` w `DataQuality.reason` i `MarketEvent.rejection_reason`; tabulator dozwolony |
| A-07 | `TestA07SafeModification` | `model_copy(update=...)`, `copy.replace`, `replace` walidują; nieznane pola odrzucane; zagnieżdżone instancje z `model_construct` (Instrument, DataQuality, MetricValue) odrzucane; zmiana statusu zdarzenia sprawdza niezmienniki |
| E-1, E-3 | `TestE3BinaryInputRejected`, `TestA03TimestampInputTypes` | dane binarne (także ISO jako `bytes`) w polach czasu, tekstowych, enumach, liczbach i identyfikatorach |
| E-2 | `TestA02SchemaVersion::test_decimal_marker_rejected` | `Decimal` jako znacznik wersji |
| E-4 | `TestA06ReasonSingleLine` | separatory Unicode (U+0085, U+2028, U+2029, VT, FF, U+001C–U+001E) |
| Rekomendacja §5 | `tests/contracts/test_documentation.py` | odnośniki względne, kotwice i ścieżki w backtickach we wszystkich `.md` |
