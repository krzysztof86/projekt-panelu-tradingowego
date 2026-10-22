# EXCHANGE_API — źródła danych i dokumentacja giełd

> **Status FAZY 0:** brak jakiejkolwiek komunikacji z giełdami. Ten dokument wskazuje
> oficjalne źródła dla przyszłych konektorów (PLANOWANE). Treść stron dokumentacji
> **nie była analizowana** w FAZIE 0 — wszystkie szczegóły formatów należy zweryfikować
> z oficjalną dokumentacją przed implementacją konektorów.

## 1. Zakres
- Wyłącznie **publiczne** dane rynkowe (bez uwierzytelniania, bez kluczy API).
- Wyłącznie kontrakty USDT linear perpetual.
- Bez składania zleceń i bez endpointów kont.

## 2. Bybit V5 (kategoria `linear`)
| Temat | Oficjalna dokumentacja | Dostępność URL (2026-10-22) |
|---|---|---|
| Wprowadzenie | https://bybit-exchange.github.io/docs/v5/intro | HTTP 200 |
| Instrumenty | https://bybit-exchange.github.io/docs/v5/market/instrument | HTTP 200 |
| Świece REST | https://bybit-exchange.github.io/docs/v5/market/kline | HTTP 200 |
| Transakcje REST | https://bybit-exchange.github.io/docs/v5/market/recent-trade | HTTP 200 |
| Tickery REST | https://bybit-exchange.github.io/docs/v5/market/tickers | HTTP 200 |
| WS transakcje | https://bybit-exchange.github.io/docs/v5/websocket/public/trade | HTTP 200 |
| WS świece | https://bybit-exchange.github.io/docs/v5/websocket/public/kline | HTTP 200 |
| WS ticker | https://bybit-exchange.github.io/docs/v5/websocket/public/ticker | HTTP 200 |
| Limity zapytań | https://bybit-exchange.github.io/docs/v5/rate-limit | HTTP 200 |

## 3. Binance USDⓈ-M Futures
| Temat | Oficjalna dokumentacja | Dostępność URL (2026-10-22) |
|---|---|---|
| Informacje ogólne | https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info | HTTP 202, **NIEZWERYFIKOWANE** |
| Exchange Information | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information | HTTP 202, **NIEZWERYFIKOWANE** |
| Świece REST | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data | HTTP 202, **NIEZWERYFIKOWANE** |
| Transakcje zagregowane REST | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List | HTTP 202, **NIEZWERYFIKOWANE** |
| Ticker ceny REST | https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Price-Ticker | HTTP 202, **NIEZWERYFIKOWANE** |
| Strumienie WS | https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams | HTTP 202, **NIEZWERYFIKOWANE** |
| WS transakcje zagregowane | https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Aggregate-Trade-Streams | HTTP 202, **NIEZWERYFIKOWANE** |
| WS świece | https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Kline-Candlestick-Streams | HTTP 202, **NIEZWERYFIKOWANE** |

HTTP 202 oznacza, że serwis zwrócił stronę kontroli klientów automatycznych; treść nie została
potwierdzona (log: `reports/phase0/command_logs/08_exchange_doc_urls.txt`). Otwarta kwestia OQ-12.

## 4. Mapowanie na kontrakty — obowiązki przyszłych konektorów (PROPOSED)
Poniższe punkty to **założenia do weryfikacji**, nie fakty potwierdzone dokumentacją w FAZIE 0.
| Kontrakt | Obowiązek konektora |
|---|---|
| `Instrument.symbol` | przekazać symbol dosłownie, bez zmiany wielkości liter |
| `Instrument.status` | zmapować status giełdowy na `ContractStatus` (tabela mapowania: DEC-012, OQ-03) |
| `Instrument.market_type` | odfiltrować wszystko poza USDT linear perpetual (Spot, COIN-M/inverse, USDC, kontrakty terminowe z datą) |
| czasy | zamienić epoch (ms) na świadomy `datetime` UTC jawnie, po stronie konektora |
| liczby | przekazywać wartości tekstowe z API jako `str`/`Decimal`, nigdy przez `float` |
| `Trade.aggressor_side` | zmapować stronę takera na `BUY`/`SELL` (pola giełdowe do weryfikacji) |
| `Trade.trade_id` | przekazać jako tekst |
| `Trade.value_usdt` | wyliczyć `price * quantity` w `Decimal` |
| `Candle` | ustawić `[start, end)`, `is_closed`, `turnover_usdt` (obrót w walucie kwotowanej) |
| `source` | `REST` lub `WEBSOCKET` |
