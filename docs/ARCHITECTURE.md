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
1. `core` nie importuje niczego z innych modułów projektu i **nie wykonuje aplikacyjnego I/O**
   (sieć, pliki, procesy, baza, GUI). Zasada dotyczy operacji wykonywanych przez kod `core`;
   mechanizmy importu samego Pythona (odczyt plików modułów) nie są nią objęte (DEC-023).
   Kontrola jest **ograniczona** i składa się z trzech testów:
   - `tests/contracts/test_package_import.py::test_core_import_does_not_load_io_libraries` —
     po imporcie wszystkich pakietów `core` w `sys.modules` nie ma bibliotek sieci, GUI, bazy
     i procesów (sprawdza tylko zależności po imporcie);
   - `tests/contracts/test_core_boundaries.py` — statyczna lista dozwolonych importów w `core`
     (wybrane moduły standardowe, `pydantic`, `market_intelligence.core`), zakaz wywołań
     `open`/`exec`/`eval`/`compile`/`__import__` oraz zakaz `model_construct` w `src/`;
   - ten sam plik — strażnik czasu wykonania: `open`, `io.open`, `os.open`, `os.system`,
     `subprocess.Popen` i funkcje `socket` są zablokowane podczas walidacji, serializacji,
     kopiowania i zapytań do wszystkich kontraktów.
   Testy nie dowodzą braku każdej możliwej operacji I/O (np. przez bibliotekę z listy dozwolonych);
   rozszerzenie listy dozwolonych importów jest zmianą wymagającą przeglądu.
2. Moduły zewnętrzne zależą od `core`; wymiana danych między modułami odbywa się wyłącznie
   przez kontrakty z `core.models`.
3. Konektory odpowiadają za mapowanie formatów giełdowych (np. `"Buy"`, ms epoch, statusy)
   na kontrakty. Kontrakty nie akceptują formatów giełdowych (DEC-004, DEC-012).
4. Detektory nie wykonują I/O — dostają kontrakty, zwracają `MarketEvent`. To warunek
   deterministycznego odtwarzania.

## 4. Moduły istniejące (FAZA 0)
| Moduł | Rola |
|---|---|
| `core.models` | Niemutowalne kontrakty danych z walidacją (schemat w wersji 2) |
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
- **Liczby finansowe**: `Decimal` w jawnej dziedzinie (DEC-020); obliczenia dokładne i niezależne
  od kontekstu `decimal`; JSON jako string (bez utraty precyzji).
- **Niemutowalność**: kontrakty są zamrożone (`frozen=True`), nieznane pola odrzucane; zmienione
  rekordy powstają wyłącznie przez walidowane ścieżki (DEC-021).
- **Wersjonowanie**: każdy rekord najwyższego poziomu ma całkowitoliczbowe `schema_version`.
- **Tożsamość instrumentu**: `instrument_id` (giełda, typ rynku, symbol) — brak niejawnego
  łączenia giełd; równość modeli = równość snapshotu (DEC-006).
- **Determinizm**: identyfikatory zdarzeń dostarcza producent, model nie losuje (DEC-015).
- **Bezpieczeństwo**: brak sekretów w repozytorium; tylko publiczne API.

## 7. Gwarancje modelu a własności przyszłego systemu
| Własność | Gwarantuje kontrakt (dziś, testowane) | Wymaga przyszłego modułu (PLANOWANE) |
|---|---|---|
| Poprawność pojedynczego rekordu | walidacja pól i niezmienników na każdej ścieżce tworzenia (DEC-021) | — |
| Tożsamość instrumentu | format i porównywanie `instrument_id` | kluczowanie kolekcji i historii przez `instrument_id` (storage, scanner) |
| Brak I/O | ograniczone kontrole `core` (§3, DEC-023) | izolacja I/O w konektorach i storage |
| Brak look-ahead | tylko `detected_at >= window_end` (deklarowane czasy) | testy detektorów na danych z przyszłości (DETECTORS.md §5) |
| Deterministyczne ID | `event_id` wymagany, nie losowany przez model | algorytm ID i testy replay (OQ-09) |
| Przejścia statusów | spójność statusu i przyczyny w jednym rekordzie | silnik zdarzeń (OQ-09) |
