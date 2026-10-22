# DETECTORS — specyfikacja przyszłych detektorów D1–D3

> **Status: PLANOWANE.** Żaden detektor nie jest zaimplementowany. Dokument ustala wyłącznie
> granice odpowiedzialności i kontrakt wyjściowy. Parametry liczbowe (okna, progi, metody
> wyznaczania wartości referencyjnych) **nie zostały ustalone** i są otwartą kwestią OQ-02.
> Nie wolno ich uzupełniać założeniami bez decyzji zapisanej w [DECISIONS.md](DECISIONS.md).

## 1. Wspólny kontrakt detektora
- Wejście: wyłącznie kontrakty z `market_intelligence.core.models` (`Instrument`,
  `MarketTick`, `Candle`, `Trade`, `DataQuality`). Jeden instrument = jedna giełda;
  detektor nie łączy danych z różnych giełd.
- Wyjście: `MarketEvent` z `detector_id` (`D1`/`D2`/`D3`), `detector_version`
  (semver implementacji) i `config_version` (identyfikator konfiguracji parametrów).
- Brak I/O: detektor nie czyta sieci, plików ani bazy; nie odczytuje zegara systemowego —
  czas pochodzi z danych wejściowych (warunek deterministycznego odtwarzania).
- Przyczynowość: korzysta tylko z danych z okna `[window_start, window_end)` i wcześniejszych;
  `detected_at >= window_end` (wymuszone przez kontrakt).
- `event_id`: deterministyczny, wyznaczany przez producenta (sposób: OQ-09/DEC-015).
- Jakość: zdarzenie przenosi `DataQuality` danych wejściowych. Kontrakt nie pozwala nadać
  statusu `VERIFIED` przy jakości innej niż `VALID`. Zachowanie przy `WARMUP`, `STALE`, `GAP`,
  `INSUFFICIENT_DATA` (czy emitować zdarzenie) — do ustalenia (OQ-02).
- Nowe zdarzenie ma status `CANDIDATE`; przejścia statusów należą do planowanego silnika
  zdarzeń, nie do detektora (OQ-09).
- Detektor nie generuje sygnałów transakcyjnych ani rekomendacji.

## 2. D1 — Price Velocity Detector
- Cel: wykrycie nietypowo szybkiej zmiany ceny w krótkim oknie czasu.
- Dane wejściowe (przewidywane): `MarketTick` lub `Trade` (cena, czas).
- `direction`: `UP` lub `DOWN` zgodnie ze znakiem zmiany ceny.
- `observed_values` / `reference_values`: nazwy i jednostki metryk — do ustalenia (np. zmiana
  ceny w `PERCENT` względem wartości referencyjnej).
- Otwarte: długość okna, definicja „prędkości”, sposób wyznaczenia odniesienia, próg.

## 3. D2 — Relative Volume Detector
- Cel: wykrycie obrotu w oknie nietypowo wysokiego względem historii tego samego instrumentu.
- Dane wejściowe (przewidywane): `Candle.turnover_usdt` lub suma `Trade.value_usdt`.
- `direction`: `NON_DIRECTIONAL`, chyba że zostanie podjęta inna decyzja.
- Otwarte: okno, długość historii referencyjnej, statystyka odniesienia, próg, wpływ
  świec niezamkniętych (`is_closed = false`).

## 4. D3 — Delta/Price Divergence Detector
- Cel: wykrycie rozbieżności między kierunkiem zmiany ceny a deltą agresora
  (wartość transakcji `BUY` minus `SELL`) w tym samym oknie.
- Dane wejściowe (przewidywane): `Trade` (`aggressor_side`, `value_usdt`) i cena.
- `direction`: do ustalenia (np. kierunek ceny lub kierunek delty).
- Otwarte: definicja rozbieżności, okno, normalizacja delty, progi.

## 5. Wymagania testowe dla przyszłej implementacji
- Testy jednostkowe na danych syntetycznych oznaczonych `DataSource.SYNTHETIC`.
- Test determinizmu: te same dane wejściowe → identyczne `MarketEvent` (łącznie z `event_id`).
- Test braku dostępu do przyszłych danych (look-ahead).
- Testy zachowania dla każdego statusu `DataQuality`.
