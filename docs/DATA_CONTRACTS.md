# DATA_CONTRACTS — kontrakty danych, schemat w wersji 1

Kod: `src/market_intelligence/core/models/`. Import publiczny:
`from market_intelligence.core.models import Instrument, MarketTick, Candle, Trade, DataQuality, MarketEvent`.

## 1. Zasady wspólne
| Zasada | Realizacja | Decyzja |
|---|---|---|
| Niemutowalność | `frozen=True`; próba przypisania → `ValidationError`; instancje hashowalne | DEC-005 |
| Nieznane pola | `extra="forbid"` → `ValidationError` | DEC-005 |
| Wersja schematu | `schema_version: Literal[1] = 1` w `Instrument`, `MarketTick`, `Candle`, `Trade`, `MarketEvent`; inna wartość → błąd. `DataQuality` i `MetricValue` są obiektami wartości wersjonowanymi przez rekord nadrzędny | DEC-005 |
| Wartości finansowe | `Decimal`. Wejście: `Decimal`, `int` lub `str`. **Odrzucane**: `float`, `bool`, NaN, ±Infinity (także jako tekst) | DEC-003 |
| JSON | `Decimal` serializowany jako **string** (`"0.10"`), dokładna reprezentacja zachowana (także zera końcowe i wykładnik); czas jako ISO 8601 z `Z` | DEC-003 |
| Czas | Tylko `datetime` ze strefą lub ISO 8601 z przesunięciem; normalizacja do UTC. **Odrzucane**: czas naiwny, liczby (epoch s/ms), teksty numeryczne | DEC-004 |
| Brak danych ≠ zero | Pola opcjonalne mają wartość `None` (brak informacji). Pola wymagane nie mają wartości domyślnych — brak pola → błąd; `0` jest wartością, nie brakiem | — |
| Enumeracje | Wielkie litery, wewnętrzne identyfikatory. Pisownia giełdowa (np. `"Buy"`, `"Trading"`) jest odrzucana — mapuje ją konektor | DEC-012 |

Wspólne typy (`core/models/types.py`):
| Typ | Znaczenie |
|---|---|
| `FiniteDecimal` | skończony `Decimal` (może być ujemny/zero) |
| `PositiveDecimal` | skończony, `> 0` |
| `NonNegativeDecimal` | skończony, `>= 0` |
| `UtcDatetime` | świadomy strefy, znormalizowany do UTC |
| `ExchangeSymbol` | 1–64 znaki bez białych znaków i `:`; zachowany dosłownie (bez zmiany wielkości liter) |
| `AssetCode` | 1–32 znaki bez białych znaków i `:` |
| `ReasonText` | 1–500 znaków, jedna linia, bez białych znaków na początku/końcu |

## 2. Enumeracje (`core/models/enums.py`)
| Enum | Wartości |
|---|---|
| `Exchange` | `BYBIT`, `BINANCE` |
| `MarketType` | `USDT_LINEAR_PERPETUAL` (jedyna; Spot i COIN-M są odrzucane) |
| `ContractStatus` | `PRE_LAUNCH`, `TRADING`, `SETTLING`, `CLOSED` (mapowanie giełdowe: PROPOSED, DEC-012) |
| `DataSource` | `REST`, `WEBSOCKET`, `REPLAY`, `SYNTHETIC` (dane testowe) |
| `DataQualityStatus` | `VALID`, `WARMUP`, `STALE`, `GAP`, `INSUFFICIENT_DATA`, `INVALID` |
| `AggressorSide` | `BUY`, `SELL` (strona zlecenia takera) |
| `CandleInterval` | `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d`; właściwość `.duration` |
| `DetectorId` | `D1`, `D2`, `D3` |
| `EventDirection` | `UP`, `DOWN`, `NON_DIRECTIONAL` |
| `EventStatus` | `CANDIDATE`, `ANALYZING`, `VERIFIED`, `REJECTED`, `EXPIRED` |

## 3. Instrument (`instrument.py`)
| Pole | Typ | Jednostka / znaczenie | Walidacja |
|---|---|---|---|
| `schema_version` | `1` | wersja schematu | tylko `1` |
| `exchange` | `Exchange` | giełda | enum |
| `symbol` | `ExchangeSymbol` | symbol giełdowy, np. `BTCUSDT` | dosłownie, bez normalizacji |
| `market_type` | `MarketType` | rodzaj rynku | tylko `USDT_LINEAR_PERPETUAL` |
| `base_asset` | `AssetCode` | aktywo bazowe | |
| `quote_asset` | `"USDT"` | waluta kwotowana | tylko `"USDT"` |
| `status` | `ContractStatus` | status kontraktu | enum |
| `tick_size` | `PositiveDecimal` | minimalny krok ceny, w USDT | `> 0` |
| `listed_at` | `UtcDatetime \| None` | czas notowania | opcjonalny |

Właściwość (nie serializowana): `instrument_id` = `"<EXCHANGE>:<MARKET_TYPE>:<SYMBOL>"`,
np. `BYBIT:USDT_LINEAR_PERPETUAL:BTCUSDT` (DEC-006). Typ `InstrumentId` waliduje ten format.
Ten sam symbol na dwóch giełdach to dwa różne, nierówne instrumenty.
Nie sprawdza się, czy `symbol == base_asset + quote_asset` (OQ-05).

## 4. DataQuality (`data_quality.py`)
| Pole | Typ | Walidacja |
|---|---|---|
| `status` | `DataQualityStatus` | enum |
| `reason` | `ReasonText \| None` | **wymagane** dla każdego statusu innego niż `VALID` (DEC-009); dozwolone także przy `VALID` |

Pomocnicze: `DataQuality.valid()`, właściwość `is_valid`.

## 5. MarketTick (`market_tick.py`)
| Pole | Typ | Jednostka | Walidacja |
|---|---|---|---|
| `schema_version` | `1` | | |
| `instrument` | `Instrument` | | |
| `last_price` | `PositiveDecimal` | USDT za 1 jednostkę aktywa bazowego | `> 0` |
| `exchange_time` | `UtcDatetime \| None` | czas giełdowy | opcjonalny; `None` = giełda nie podała (nie jest zastępowany czasem odbioru) |
| `received_at` | `UtcDatetime` | czas odbioru lokalnie | wymagany |
| `source` | `DataSource` | | |
| `quality` | `DataQuality` | | |

Kolejność `exchange_time` / `received_at` nie jest wymuszana (dryf zegarów to kwestia jakości danych).

## 6. Candle (`candle.py`)
| Pole | Typ | Jednostka | Walidacja |
|---|---|---|---|
| `schema_version` | `1` | | |
| `instrument` | `Instrument` | | |
| `interval` | `CandleInterval` | | enum |
| `start` | `UtcDatetime` | początek, **włącznie** | wyrównany do wielokrotności interwału od epoki Unix (DEC-007) |
| `end` | `UtcDatetime` | koniec, **wyłącznie** | `end - start == interval.duration` |
| `open`, `high`, `low`, `close` | `PositiveDecimal` | USDT | `> 0`; `low <= min(open, close)`, `high >= max(open, close)`, `low <= high` |
| `turnover_usdt` | `NonNegativeDecimal` | obrót w USDT | `>= 0`; wymagany (`0` = brak handlu; brak pola/`None` = błąd) |
| `is_closed` | `StrictBool` | świeca zamknięta | tylko `true`/`false` (bez koercji `"true"`, `1`) |
| `source` | `DataSource` | | |
| `quality` | `DataQuality` | | |

Semantyka przedziału `[start, end)`: metoda `contains(moment)` zwraca `start <= moment < end`;
`end` świecy jest `start` kolejnej; moment graniczny należy wyłącznie do kolejnej świecy.

## 7. Trade (`trade.py`)
| Pole | Typ | Jednostka | Walidacja |
|---|---|---|---|
| `schema_version` | `1` | | |
| `instrument` | `Instrument` | | |
| `trade_id` | `TradeId` (str) | identyfikator giełdowy | 1–128 znaków bez białych znaków; liczba (int) odrzucana — konektor przekazuje tekst |
| `price` | `PositiveDecimal` | USDT za 1 jednostkę aktywa bazowego | `> 0` |
| `quantity` | `PositiveDecimal` | jednostki aktywa bazowego | `> 0` |
| `value_usdt` | `PositiveDecimal` | USDT | `== price * quantity` dokładnie (DEC-010) |
| `aggressor_side` | `AggressorSide` | strona takera | `BUY` / `SELL` |
| `executed_at` | `UtcDatetime` | czas wykonania (giełda) | wymagany |
| `received_at` | `UtcDatetime` | czas odbioru | wymagany |
| `source` | `DataSource` | | |
| `quality` | `DataQuality` | | |

## 8. MarketEvent (`market_event.py`)
| Pole | Typ | Walidacja |
|---|---|---|
| `schema_version` | `1` | |
| `event_id` | `UUID` | wymagany, dostarczany przez producenta — brak losowej wartości domyślnej (DEC-015) |
| `instrument_id` | `InstrumentId` | format `<EXCHANGE>:<MARKET_TYPE>:<SYMBOL>` z dozwolonymi enumami |
| `detector_id` | `DetectorId` | `D1`/`D2`/`D3` |
| `detector_version` | str | `MAJOR.MINOR.PATCH` |
| `config_version` | str | 1–64 znaki `[A-Za-z0-9._:-]` |
| `detected_at` | `UtcDatetime` | `>= window_end` |
| `window_start` | `UtcDatetime` | `< window_end` (okno `[window_start, window_end)`) |
| `window_end` | `UtcDatetime` | |
| `direction` | `EventDirection` | |
| `observed_values` | `tuple[MetricValue, ...]` | min. 1, unikalne nazwy |
| `reference_values` | `tuple[MetricValue, ...]` | min. 1, unikalne nazwy |
| `quality` | `DataQuality` | `VERIFIED` wymaga `VALID` |
| `status` | `EventStatus` | |
| `rejection_reason` | `ReasonText \| None` | wymagany **wtedy i tylko wtedy**, gdy `status == REJECTED` |

`MetricValue`: `name` (`^[a-z][a-z0-9_]{0,63}$`), `value` (`FiniteDecimal`, może być ujemny),
`unit` (`^[A-Z][A-Z0-9_]{0,31}$`, np. `USDT`, `PERCENT`, `RATIO`; słownik jednostek: OQ-10).

Silnik zmian statusów **nie istnieje** (PLANOWANE); kontrakt waliduje wyłącznie spójność
pojedynczego rekordu.

## 9. Przykład JSON (dane syntetyczne)
Kompletne, walidowane przykłady wszystkich rekordów: `tests/fixtures/synthetic_contract_samples.json`.
```json
{"schema_version":1,"exchange":"BYBIT","symbol":"BTCUSDT","market_type":"USDT_LINEAR_PERPETUAL",
 "base_asset":"BTC","quote_asset":"USDT","status":"TRADING","tick_size":"0.10","listed_at":null}
```

## 10. Zmiana kontraktu
Procedura: [DEVELOPMENT.md](DEVELOPMENT.md), sekcja 8.1.
