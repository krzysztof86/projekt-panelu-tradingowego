# ARCHITECTURE

Status dokumentu: stan po FAZIE 0. Elementy oznaczone **PLANOWANE** nie istnieją w kodzie.

## 1. Kontekst
Aplikacja desktopowa Windows wykrywa anomalie na kontraktach USDT linear perpetual
(Bybit V5, Binance USDⓈ-M) na podstawie **publicznych** danych rynkowych. Nie składa zleceń,
nie używa prywatnych kluczy API. AGGR jest osobnym, niezależnym narzędziem (brak integracji).

## 2. Styl architektury
**Modularny monolit** (DEC-001): jeden proces, jeden pakiet Pythona `market_intelligence`
w układzie `src/`, podzielony na moduły o jawnych granicach. Uzasadnienie:
- jedna aplikacja desktopowa dla jednego użytkownika — brak potrzeby usług rozproszonych;
- deterministyczne odtwarzanie (replay) jest prostsze w jednym procesie;
- granice modułów pozwalają w przyszłości wydzielić część bez przepisywania kontraktów.

Stos: Python 3.14, Pydantic v2 (kontrakty), pytest, mypy (strict), Ruff; docelowo PySide6
(GUI) i SQLite (przechowywanie) — **jeszcze nie są zależnościami projektu**.

## 3. Warstwy i kierunek zależności
```
            ┌──────────────────────────────────────────────┐
            │ gui (PySide6)                     PLANOWANE  │
            └──────────────────────┬───────────────────────┘
            ┌──────────────────────▼───────────────────────┐
            │ scanner L1 · detectors D1–D3 · replay         │
            │                                   PLANOWANE  │
            └───────┬──────────────────────────────┬───────┘
     ┌──────────────▼─────────────┐   ┌────────────▼───────────────┐
     │ connectors (Bybit,Binance) │   │ storage (SQLite)           │
     │ quality       PLANOWANE    │   │                 PLANOWANE  │
     └──────────────┬─────────────┘   └────────────┬───────────────┘
            ┌───────▼──────────────────────────────▼───────┐
            │ core: models · clock          ISTNIEJE        │
            │       config · events         ZAREZERWOWANE   │
            └──────────────────────────────────────────────┘
```
Zasady:
1. `core` nie importuje niczego z innych modułów projektu i **nie wykonuje I/O**
   (sieć, pliki, baza, GUI). Sprawdza to test `test_core_has_no_io_dependencies`.
2. Moduły zewnętrzne zależą od `core`; wymiana danych między modułami odbywa się wyłącznie
   przez kontrakty z `core.models`.
3. Konektory odpowiadają za mapowanie formatów giełdowych (np. `"Buy"`, ms epoch, statusy)
   na kontrakty. Kontrakty nie akceptują formatów giełdowych (DEC-004, DEC-012).
4. Detektory nie wykonują I/O — dostają kontrakty, zwracają `MarketEvent`. To warunek
   deterministycznego odtwarzania.

## 4. Moduły istniejące (FAZA 0)
| Moduł | Rola |
|---|---|
| `core.models` | Niemutowalne kontrakty danych z walidacją (schemat w wersji 1) |
| `core.clock` | Normalizacja czasu do UTC (`ensure_utc`, `UTC_EPOCH`) |
| `core.config` | Zarezerwowany, pusty (DEC-008) |
| `core.events` | Zarezerwowany, pusty (DEC-008) |

Szczegóły interfejsów: [MODULE_MAP.md](MODULE_MAP.md). Kontrakty: [DATA_CONTRACTS.md](DATA_CONTRACTS.md).

## 5. Moduły planowane (PLANOWANE — brak kodu, zakres do zatwierdzenia)
| Moduł | Rola |
|---|---|
| connectors | Publiczne REST/WebSocket Bybit V5 i Binance USDⓈ-M → kontrakty |
| quality | Market Data Quality: ustalanie `DataQuality` (STALE, GAP, WARMUP…) |
| storage | Historia danych i zdarzeń w SQLite |
| detectors | D1, D2, D3 — patrz [DETECTORS.md](DETECTORS.md) |
| events (engine) | Cykl życia `MarketEvent` (przejścia statusów) |
| replay | Deterministyczne odtwarzanie z historii |
| scanner | Market Scanner L1 (zakres do doprecyzowania, OQ-01) |
| gui | Interfejs PySide6 |

## 6. Zasady przekrojowe
- **Czas**: wewnętrznie wyłącznie świadome strefy `datetime` w UTC; brak czasu naiwnego.
- **Liczby finansowe**: `Decimal`; JSON jako string (bez utraty precyzji).
- **Niemutowalność**: kontrakty są zamrożone (`frozen=True`), nieznane pola odrzucane.
- **Wersjonowanie**: każdy rekord najwyższego poziomu ma `schema_version`.
- **Tożsamość instrumentu**: (giełda, typ rynku, symbol) — brak niejawnego łączenia giełd.
- **Determinizm**: identyfikatory zdarzeń dostarcza producent, model nie losuje (DEC-015).
- **Bezpieczeństwo**: brak sekretów w repozytorium; tylko publiczne API.
