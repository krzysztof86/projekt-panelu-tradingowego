# MODULE_MAP — mapa kodu

Ścieżki względem `src/market_intelligence/`. **ISTNIEJE** = kod w repozytorium;
**ZAREZERWOWANY** = pusty pakiet; **PLANOWANE** = nie istnieje (proponowana ścieżka).

## Szybkie wyszukiwanie: „chcę zmienić…”
| Zmiana | Plik |
|---|---|
| Pole/walidację instrumentu | `core/models/instrument.py` |
| Świecę, OHLC, interwały `[start, end)` | `core/models/candle.py`, interwały: `core/models/enums.py` (`CandleInterval`) |
| Transakcję | `core/models/trade.py` |
| Tick ceny | `core/models/market_tick.py` |
| Jakość danych | `core/models/data_quality.py` |
| Zdarzenie / metryki | `core/models/market_event.py` |
| Wartości enumeracji | `core/models/enums.py` |
| Reguły Decimal / dziedzinę / czasu / symboli / tekstu przyczyny | `core/models/types.py` |
| Normalizację UTC | `core/clock/utc.py` |
| Wersję schematu, wspólną konfigurację modeli, `replace`/`model_copy`, odrzucanie danych binarnych | `core/models/base.py` |
| Dokładne obliczenie wartości transakcji | `core/models/trade.py` (`_exact_product`) |
| Dozwolone importy w `core` (kontrola granic) | `tests/contracts/test_core_boundaries.py` (`ALLOWED_TOP_LEVEL_IMPORTS`) |
| Eksport publicznego API modeli | `core/models/__init__.py` |
| Wersję pakietu | `__init__.py` **i** `pyproject.toml` (muszą być zgodne — test) |

## Moduły istniejące

### `market_intelligence` (`__init__.py`) — ISTNIEJE
- Odpowiedzialność: pakiet główny; `__version__`.
- Interfejs: `__version__: str`.
- Zależności: brak. Testy: `tests/contracts/test_package_import.py`. Dokumentacja: README.md.

### `core` (`core/__init__.py`) — ISTNIEJE
- Odpowiedzialność: warstwa bez aplikacyjnego I/O — kontrakty i prymitywy.
- Ograniczenia: tylko importy z listy dozwolonych; brak wywołań `open`/`exec`/`eval`; brak I/O
  w czasie wykonania (ograniczone kontrole, DEC-023).
- Testy: `tests/contracts/test_core_boundaries.py`,
  `tests/contracts/test_package_import.py::test_core_import_does_not_load_io_libraries`.
- Dokumentacja: ARCHITECTURE.md §3.

### `core.clock` (`core/clock/utc.py`) — ISTNIEJE
- Odpowiedzialność: normalizacja czasu do UTC.
- Interfejs: `ensure_utc(value: datetime) -> datetime`; `UTC_EPOCH: datetime`.
- Wejście/wyjście: świadomy `datetime` → `datetime` w UTC; naiwny lub bez odpowiednika w UTC
  (poza latami 1–9999) → `ValueError` (nigdy `OverflowError`).
- Zależności: biblioteka standardowa.
- Testy: `tests/unit/test_primitives.py::TestEnsureUtc`,
  `tests/regression/test_audit3_phase0.py` (+ pośrednio wszystkie testy czasu).
- Dokumentacja: DATA_CONTRACTS.md §1, DEC-004.

### `core.models.base` — ISTNIEJE
- Odpowiedzialność: bazowa konfiguracja kontraktów, wersja schematu, bezpieczne tworzenie
  zmienionych rekordów, odrzucanie danych binarnych.
- Interfejs: `ContractModel` (`replace(**zmiany)`, walidujące `model_copy(update=...)`),
  `VersionedContractModel`, `SCHEMA_VERSION` (=2), `SchemaVersion` (ścisła liczba całkowita).
- Ograniczenia: `revalidate_instances="always"`; `model_construct` zakazany w `src/` (DEC-021).
- Zależności: pydantic. Testy: `tests/contracts/test_serialization.py::TestSchemaVersion`,
  `tests/unit/test_instrument.py::TestImmutability`, `tests/regression/test_audit1_phase0.py`
  (`TestA02SchemaVersion`, `TestA07SafeModification`, `TestE3BinaryInputRejected`).
  Dokumentacja: DATA_CONTRACTS.md §1.2, DEC-005, DEC-021, DEC-022.

### `core.models.types` — ISTNIEJE
- Odpowiedzialność: typy pól z walidacją i dziedzina wartości Decimal.
- Interfejs: `FiniteDecimal`, `PositiveDecimal`, `NonNegativeDecimal`, `UtcDatetime`,
  `PositiveProductDecimal`, `ExchangeSymbol`, `AssetCode`, `ReasonText`; stałe `MAX_DECIMAL_PLACES` (18),
  `MAX_PRODUCT_DECIMAL_PLACES` (36), `MAX_INTEGER_DIGITS` (20).
- Wejście: `Decimal|int|str` (liczby, ≤ 18 miejsc po przecinku — iloczyn `value_usdt` ≤ 36,
  \|x\| < 1E+20), wyłącznie `datetime` lub tekst w profilu RFC 3339 (czas, lista dozwolonych
  zapisów `_RFC3339`). Wyjście: `Decimal`, `datetime` UTC.
- Ograniczenia: tylko operacje Decimal niezależne od kontekstu.
- Zależności: pydantic, `core.clock`. Testy: `tests/unit/test_primitives.py`,
  `tests/regression/test_audit1_phase0.py` (`TestA01FinancialDomain`, `TestA03TimestampInputTypes`,
  `TestA06ReasonSingleLine`), `tests/regression/test_audit2_phase0.py` (`TestK101NumericText`,
  `TestRfc3339Profile`, `TestDec020ProductDomain`). Dokumentacja: DATA_CONTRACTS.md §1–§1.3,
  DEC-003, DEC-004, DEC-009, DEC-020.

### `core.models.enums` — ISTNIEJE
- Interfejs: `Exchange`, `MarketType`, `ContractStatus`, `DataSource`, `DataQualityStatus`,
  `AggressorSide`, `CandleInterval` (`.duration`), `DetectorId`, `EventDirection`, `EventStatus`.
- Zależności: biblioteka standardowa. Testy: pośrednio w testach modeli. Dokumentacja: DATA_CONTRACTS.md §2.

### `core.models.data_quality` — ISTNIEJE
- Interfejs: `DataQuality(status, reason)`, `DataQuality.valid()`, `.is_valid`.
- Ograniczenia: `reason` wymagane dla statusu ≠ VALID.
- Testy: `tests/unit/test_data_quality.py`. Dokumentacja: DATA_CONTRACTS.md §4, DEC-009.

### `core.models.instrument` — ISTNIEJE
- Interfejs: `Instrument`, `.instrument_id`, typ `InstrumentId`.
- Ograniczenia: tylko `USDT_LINEAR_PERPETUAL`, quote `USDT`, symbol dosłownie. Tożsamość domenowa =
  `instrument_id`; `==`/`hash` porównują cały snapshot (DEC-006).
- Testy: `tests/unit/test_instrument.py`, `tests/regression/test_audit1_phase0.py::TestA04InstrumentIdentity`.
  Dokumentacja: DATA_CONTRACTS.md §3, DEC-006.

### `core.models.market_tick` — ISTNIEJE
- Interfejs: `MarketTick`. Zależności: `instrument`, `data_quality`, `types`, `enums`.
- Testy: `tests/unit/test_market_tick.py`. Dokumentacja: DATA_CONTRACTS.md §5.

### `core.models.candle` — ISTNIEJE
- Interfejs: `Candle`, `Candle.contains(moment) -> bool`.
- Ograniczenia: `[start, end)`, długość = interwał, wyrównanie do epoki, spójność OHLC.
- Testy: `tests/unit/test_candle.py`. Dokumentacja: DATA_CONTRACTS.md §6, DEC-007.

### `core.models.trade` — ISTNIEJE
- Interfejs: `Trade`, typ `TradeId`.
- Ograniczenia: `value_usdt == price * quantity` dokładnie, w prywatnym kontekście `decimal`
  niezależnym od wywołującego.
- Testy: `tests/unit/test_trade.py`, `tests/regression/test_audit1_phase0.py::TestA01ExactProduct`.
  Dokumentacja: DATA_CONTRACTS.md §7, DEC-010, DEC-020.

### `core.models.market_event` — ISTNIEJE
- Interfejs: `MarketEvent`, `MetricValue`.
- Ograniczenia: niezmienniki DEC-011; brak logiki przejść statusów.
- Testy: `tests/unit/test_market_event.py`. Dokumentacja: DATA_CONTRACTS.md §8, DEC-011, DEC-015.

### `core.config` — ZAREZERWOWANY (DEC-008)
Tylko `__init__.py`. Przeznaczenie (PLANOWANE): konfiguracja aplikacji i wersjonowana konfiguracja detektorów (`config_version`).

### `core.events` — ZAREZERWOWANY (DEC-008)
Tylko `__init__.py`. Przeznaczenie (PLANOWANE): cykl życia i historia `MarketEvent`.

## Moduły PLANOWANE (nie istnieją; ścieżki są propozycją do zatwierdzenia)
| Moduł | Proponowana ścieżka | Odpowiedzialność | Wejście → wyjście |
|---|---|---|---|
| Konektor Bybit | `connectors/bybit/` | publiczne REST/WS Bybit V5 | JSON giełdy → kontrakty |
| Konektor Binance | `connectors/binance/` | publiczne REST/WS Binance USDⓈ-M | JSON giełdy → kontrakty |
| Market Data Quality | `quality/` | ocena jakości strumieni | kontrakty → `DataQuality` |
| Storage | `storage/` | SQLite: dane i zdarzenia | kontrakty ↔ baza |
| D1 / D2 / D3 | `detectors/` | wykrywanie anomalii (DETECTORS.md) | kontrakty → `MarketEvent` |
| Silnik zdarzeń | `core/events/` | przejścia statusów | `MarketEvent` → `MarketEvent` |
| Replay | `replay/` | deterministyczne odtwarzanie | historia → strumień kontraktów |
| Scanner L1 | `scanner/` | Market Scanner L1 (OQ-01) | do ustalenia |
| GUI | `gui/` | PySide6 | — |

## Testy i dane
| Ścieżka | Zawartość |
|---|---|
| `tests/conftest.py` | syntetyczne fixture'y |
| `tests/unit/` | testy modeli i prymitywów |
| `tests/contracts/` | serializacja, schemat, fixture'y, import, granice `core` (I/O), odnośniki dokumentacji |
| `tests/regression/` | testy regresji ustaleń audytów (`test_audit1_phase0.py`: A-01–A-07, E-1–E-4; `test_audit2_phase0.py`: K1-01, profil RFC 3339, dziedzina iloczynu; `test_audit3_phase0.py`: K2-A01, wyłącznie `ValidationError` dla danych skrajnych) |
| `tests/fixtures/synthetic_contract_samples.json` | syntetyczne rekordy JSON |
