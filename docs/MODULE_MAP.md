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
| Reguły Decimal / czasu / symboli | `core/models/types.py` |
| Normalizację UTC | `core/clock/utc.py` |
| Wersję schematu, wspólną konfigurację modeli | `core/models/base.py` |
| Eksport publicznego API modeli | `core/models/__init__.py` |
| Wersję pakietu | `__init__.py` **i** `pyproject.toml` (muszą być zgodne — test) |

## Moduły istniejące

### `market_intelligence` (`__init__.py`) — ISTNIEJE
- Odpowiedzialność: pakiet główny; `__version__`.
- Interfejs: `__version__: str`.
- Zależności: brak. Testy: `tests/contracts/test_package_import.py`. Dokumentacja: README.md.

### `core` (`core/__init__.py`) — ISTNIEJE
- Odpowiedzialność: warstwa bez I/O — kontrakty i prymitywy.
- Ograniczenia: zakaz importu sieci, GUI, bazy danych (test `test_core_has_no_io_dependencies`).
- Dokumentacja: ARCHITECTURE.md §3.

### `core.clock` (`core/clock/utc.py`) — ISTNIEJE
- Odpowiedzialność: normalizacja czasu do UTC.
- Interfejs: `ensure_utc(value: datetime) -> datetime`; `UTC_EPOCH: datetime`.
- Wejście/wyjście: świadomy `datetime` → `datetime` w UTC; naiwny → `ValueError`.
- Zależności: biblioteka standardowa.
- Testy: `tests/unit/test_primitives.py::TestEnsureUtc` (+ pośrednio wszystkie testy czasu).
- Dokumentacja: DATA_CONTRACTS.md §1, DEC-004.

### `core.models.base` — ISTNIEJE
- Odpowiedzialność: bazowa konfiguracja kontraktów i wersja schematu.
- Interfejs: `ContractModel`, `VersionedContractModel`, `SCHEMA_VERSION` (=1), `SchemaVersion`.
- Zależności: pydantic. Testy: `tests/contracts/test_serialization.py::TestSchemaVersion`,
  `tests/unit/test_instrument.py::TestImmutability`. Dokumentacja: DEC-005.

### `core.models.types` — ISTNIEJE
- Odpowiedzialność: typy pól z walidacją.
- Interfejs: `FiniteDecimal`, `PositiveDecimal`, `NonNegativeDecimal`, `UtcDatetime`,
  `ExchangeSymbol`, `AssetCode`, `ReasonText`.
- Wejście: `Decimal|int|str` (liczby), `datetime|str ISO z przesunięciem` (czas). Wyjście: `Decimal`, `datetime` UTC.
- Zależności: pydantic, `core.clock`. Testy: `tests/unit/test_primitives.py`. Dokumentacja: DATA_CONTRACTS.md §1, DEC-003, DEC-004.

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
- Ograniczenia: tylko `USDT_LINEAR_PERPETUAL`, quote `USDT`, symbol dosłownie.
- Testy: `tests/unit/test_instrument.py`. Dokumentacja: DATA_CONTRACTS.md §3, DEC-006.

### `core.models.market_tick` — ISTNIEJE
- Interfejs: `MarketTick`. Zależności: `instrument`, `data_quality`, `types`, `enums`.
- Testy: `tests/unit/test_market_tick.py`. Dokumentacja: DATA_CONTRACTS.md §5.

### `core.models.candle` — ISTNIEJE
- Interfejs: `Candle`, `Candle.contains(moment) -> bool`.
- Ograniczenia: `[start, end)`, długość = interwał, wyrównanie do epoki, spójność OHLC.
- Testy: `tests/unit/test_candle.py`. Dokumentacja: DATA_CONTRACTS.md §6, DEC-007.

### `core.models.trade` — ISTNIEJE
- Interfejs: `Trade`, typ `TradeId`.
- Ograniczenia: `value_usdt == price * quantity`.
- Testy: `tests/unit/test_trade.py`. Dokumentacja: DATA_CONTRACTS.md §7, DEC-010.

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
| `tests/contracts/` | serializacja, schemat, fixture'y, import |
| `tests/fixtures/synthetic_contract_samples.json` | syntetyczne rekordy JSON |
