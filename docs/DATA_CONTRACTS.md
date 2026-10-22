# DATA_CONTRACTS — kontrakty danych, schemat w wersji 2

Kod: `src/market_intelligence/core/models/`. Import publiczny:
`from market_intelligence.core.models import Instrument, MarketTick, Candle, Trade, DataQuality, MarketEvent`.

Historia schematu: wersja 1 — FAZA 0 (commit `470eb03`), nieprzyjęta w audycie, nigdy nie
zapisywana poza fixture'ami testowymi; wersja 2 — korekta 1 FAZY 0 (zaostrzenie walidacji,
DEC-022). Zmiany: [CHANGELOG.md](../CHANGELOG.md).

## 1. Zasady wspólne
| Zasada | Realizacja | Decyzja |
|---|---|---|
| Niemutowalność | `frozen=True`; próba przypisania → `ValidationError`; instancje hashowalne. Równość (`==`, `hash`) porównuje **cały rekord** (snapshot), nie tożsamość domenową | DEC-005, DEC-006 |
| Nieznane pola | `extra="forbid"` → `ValidationError` | DEC-005 |
| Wersja schematu | `schema_version` = liczba całkowita `2` w `Instrument`, `MarketTick`, `Candle`, `Trade`, `MarketEvent`. **Odrzucane**: inne wartości oraz `bool`, `float` (także `2.0`), `Decimal`, `str` — w danych Python i JSON. `DataQuality` i `MetricValue` są obiektami wartości wersjonowanymi przez rekord nadrzędny | DEC-005, DEC-022 |
| Wartości finansowe | `Decimal`. Wejście: `Decimal`, `int` lub `str`. **Odrzucane**: `float`, `bool`, NaN, ±Infinity (także jako tekst) i wartości spoza dziedziny (§1.1) | DEC-003, DEC-020 |
| Arytmetyka | Jedyne obliczenie w kontraktach (`Trade`: `price * quantity`) jest dokładne i **niezależne od aktywnego kontekstu `decimal`** (precyzja, zaokrąglanie, pułapki, zakres wykładników); błąd arytmetyki zgłaszany jako `ValidationError` | DEC-010 |
| JSON | `Decimal` serializowany jako **string** (`"0.10"`), dokładna reprezentacja zachowana (także zera końcowe i wykładnik); czas jako ISO 8601 z `Z` | DEC-003 |
| Czas | Wejście **wyłącznie** `datetime` ze strefą lub `str` ISO 8601 z przesunięciem; normalizacja do UTC. **Odrzucane**: czas naiwny, liczby (epoch s/ms), teksty numeryczne, `date`, `time` i każdy inny typ | DEC-004 |
| Dane binarne | `bytes`, `bytearray`, `memoryview` są odrzucane w **każdym** polu każdego kontraktu; dekodowanie należy do wywołującego | DEC-004 |
| Brak danych ≠ zero | Pola opcjonalne mają wartość `None` (brak informacji). Pola wymagane nie mają wartości domyślnych — brak pola → błąd; `0` jest wartością, nie brakiem | — |
| Enumeracje | Wielkie litery, wewnętrzne identyfikatory. Pisownia giełdowa (np. `"Buy"`, `"Trading"`) jest odrzucana — mapuje ją konektor | DEC-012 |
| Tworzenie zmienionego rekordu | §1.2 | DEC-021 |

### 1.1 Dziedzina wartości `Decimal` (DEC-020)
Każde pole `Decimal` w każdym kontrakcie (ceny, ilości, obrót, tick size, wartości metryk):
- najwyżej **18 cyfr po przecinku**, liczone z reprezentacji wejściowej (także zera końcowe:
  `"1.0000000000000000000"` jest odrzucane);
- wartość bezwzględna **< 1E+20** (najwyżej 20 cyfr części całkowitej);
- zatem najwyżej 38 cyfr znaczących (odpowiednik `DECIMAL(38, 18)`).

Uzasadnienie granic: 18 miejsc to najmniejsza jednostka typowych tokenów (np. 1 wei = 1E-18
ETH) — żadna kwota kryptowalutowa nie wymaga więcej; publiczne kontrakty USDT perpetual mają
kroki ceny i ilości z kilkoma–kilkunastoma miejscami. 1E+20 USDT przekracza o rzędy wielkości
każdy obrót rynkowy. 38 cyfr to maksymalna precyzja typu DECIMAL w popularnych bazach SQL.
Granice są **jawne**: naruszenie daje `ValidationError` z komunikatem, nic nie jest zaokrąglane
ani obcinane.

Konsekwencja dla `Trade`: jeśli dokładny iloczyn `price * quantity` wymaga więcej niż 18
miejsc po przecinku (suma miejsc ceny i ilości > 18 po usunięciu zer końcowych) lub
przekracza 1E+20, nie istnieje poprawna wartość `value_usdt` i rekord jest odrzucany.
Wpływ na dane giełdowe — do potwierdzenia przy konektorach (OQ-03).

### 1.2 Tworzenie zmienionych rekordów (DEC-021)
| Ścieżka | Zachowanie |
|---|---|
| `Model(...)`, `model_validate`, `model_validate_json` | pełna walidacja (ścieżka dla danych niezaufanych) |
| `record.replace(**zmiany)` | nowy rekord z pełną walidacją (ścieżka zalecana) |
| `record.model_copy(update=...)`, `copy.replace(record, ...)` | pełna walidacja (przeciążone w `ContractModel`) |
| `record.model_copy()` bez `update` | kopia ważnego rekordu, bez zmian |
| rekord zagnieżdżony przekazany do innego kontraktu | **zawsze ponownie walidowany** (`revalidate_instances="always"`) |
| `Model.model_construct(...)` | **bez walidacji — zakazane w `src/`** (test `test_model_construct_not_used_in_src`); dopuszczalne tylko w testach do symulowania błędnych danych |

`frozen=True` chroni przed przypisaniem do pól, ale nie jest granicą bezpieczeństwa: kod
Pythona może obejść każdą ochronę (np. `object.__setattr__`). Gwarancją jest walidacja na
powyższych ścieżkach.

Wspólne typy (`core/models/types.py`):
| Typ | Znaczenie |
|---|---|
| `FiniteDecimal` | skończony `Decimal` w dziedzinie §1.1 (może być ujemny/zero) |
| `PositiveDecimal` | jak wyżej, `> 0` |
| `NonNegativeDecimal` | jak wyżej, `>= 0` |
| `UtcDatetime` | świadomy strefy, znormalizowany do UTC; wejście tylko `datetime`/`str` |
| `ExchangeSymbol` | 1–64 znaki bez białych znaków i `:`; zachowany dosłownie (bez zmiany wielkości liter) |
| `AssetCode` | 1–32 znaki bez białych znaków i `:` |
| `ReasonText` | 1–500 znaków, bez białych znaków na początku/końcu, **jedna linia**: zabronione separatory linii w rozumieniu `str.splitlines()` — LF, CR, CR LF, VT, FF, U+001C, U+001D, U+001E, U+0085, U+2028, U+2029. Tabulator wewnątrz tekstu jest dozwolony |

Stałe: `MAX_DECIMAL_PLACES = 18`, `MAX_INTEGER_DIGITS = 20` (`core/models/types.py`).

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
| `schema_version` | `2` | wersja schematu | tylko liczba całkowita `2` |
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

**Tożsamość a równość (A-04, DEC-006):** tożsamością domenową instrumentu jest wyłącznie
`instrument_id`. Porównanie modeli (`==`, `hash`, zbiory) dotyczy całego snapshotu metadanych:
dwa rekordy tego samego instrumentu różniące się np. `status` lub `tick_size` mają równe
`instrument_id`, ale są nierówne i w zbiorze `set` występują dwukrotnie. Konsumenci (storage,
scanner, detektory) muszą identyfikować instrumenty i budować klucze kolekcji przez
`instrument_id`; porównanie całych modeli oznacza „ten sam snapshot”.
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
| `schema_version` | `2` | | |
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
| `schema_version` | `2` | | |
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
| `schema_version` | `2` | | |
| `instrument` | `Instrument` | | |
| `trade_id` | `TradeId` (str) | identyfikator giełdowy | 1–128 znaków bez białych znaków; liczba (int) odrzucana — konektor przekazuje tekst |
| `price` | `PositiveDecimal` | USDT za 1 jednostkę aktywa bazowego | `> 0` |
| `quantity` | `PositiveDecimal` | jednostki aktywa bazowego | `> 0` |
| `value_usdt` | `PositiveDecimal` | USDT | `== price * quantity` dokładnie, w całej dziedzinie §1.1, niezależnie od kontekstu `decimal` wywołującego (DEC-010) |
| `aggressor_side` | `AggressorSide` | strona takera | `BUY` / `SELL` |
| `executed_at` | `UtcDatetime` | czas wykonania (giełda) | wymagany |
| `received_at` | `UtcDatetime` | czas odbioru | wymagany |
| `source` | `DataSource` | | |
| `quality` | `DataQuality` | | |

## 8. MarketEvent (`market_event.py`)
| Pole | Typ | Walidacja |
|---|---|---|
| `schema_version` | `2` | |
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
pojedynczego rekordu. Zmiana statusu przez `replace`/`model_copy(update=...)` ponownie sprawdza
wszystkie niezmienniki (np. `REJECTED` bez przyczyny jest odrzucany).

**Granice gwarancji modelu (audyt, §4):** kontrakt sprawdza tylko **deklarowane** wartości
pojedynczego rekordu. `detected_at >= window_end` nie dowodzi, że detektor nie użył danych
z przyszłości, a wymagany `event_id` nie gwarantuje deterministycznego sposobu jego
wyznaczenia. Te własności należą do przyszłych detektorów i silnika replay i wymagają
osobnych testów ([DETECTORS.md](DETECTORS.md) §5, OQ-09).

## 9. Przykład JSON (dane syntetyczne)
Kompletne, walidowane przykłady wszystkich rekordów: `tests/fixtures/synthetic_contract_samples.json`.
```json
{"schema_version":2,"exchange":"BYBIT","symbol":"BTCUSDT","market_type":"USDT_LINEAR_PERPETUAL",
 "base_asset":"BTC","quote_asset":"USDT","status":"TRADING","tick_size":"0.10","listed_at":null}
```

## 10. Zmiana kontraktu
Procedura: [DEVELOPMENT.md](DEVELOPMENT.md), sekcja 8.1.
