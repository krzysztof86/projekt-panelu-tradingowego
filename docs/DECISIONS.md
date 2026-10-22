# DECISIONS — decyzje techniczne i otwarte kwestie

Statusy: **ACCEPTED** (zatwierdzone przez użytkownika / wymagania), **PROPOSED** (propozycja
wykonawcy, czeka na rozstrzygnięcie użytkownika), **SUPERSEDED** (zastąpione — wskazać następcę).
Decyzji ACCEPTED nie wolno zmieniać bez zgody użytkownika. Zmiana statusu PROPOSED →
ACCEPTED wymaga decyzji użytkownika i wpisu daty. Rekomendacja audytora **nie** zmienia statusu.

Źródło „wymagania FAZY 0”: [requirements/FAZA0_SPECYFIKACJA.md](requirements/FAZA0_SPECYFIKACJA.md).
Audyt 1 FAZY 0: [reports/phase0/audyt1/AUDYT_FAZY0.md](../reports/phase0/audyt1/AUDYT_FAZY0.md)
(usterki A-01–A-07, rekomendacje §6). Korekta 1: [reports/phase0/korekta1/](../reports/phase0/korekta1/).

## Decyzje wymagające rozstrzygnięcia użytkownika

Wszystkie decyzje PROPOSED czekają na rozstrzygnięcie. Kolejność według wpływu na kontrakty:

| Priorytet | Decyzja | Pytanie do użytkownika | Rekomendacja audytu 1 |
|---|---|---|---|
| 1 | DEC-020 | Czy przyjąć dziedzinę Decimal: ≤ 18 miejsc po przecinku, \|x\| < 1E+20? | (nowa — brak; audyt wymagał jawnych granic albo dokładności w całej dziedzinie) |
| 2 | DEC-010 | Czy przyjąć ścisłą równość `value_usdt == price * quantity` (w dziedzinie DEC-020)? | Odrzucić „dokładnie” w poprzednim wykonaniu; wymaga A-01 i zatwierdzenia dziedziny |
| 3 | DEC-022 | Czy przyjąć podniesienie schematu do wersji 2 (alternatywa: zachować 1 jako niewydany)? | (nowa) |
| 4 | DEC-005 | Niemutowalność, `extra="forbid"`, ścisły znacznik wersji | Przyjąć po A-02 i opisie granic A-07 |
| 5 | DEC-021 | Ścieżki tworzenia rekordów, rewalidacja zagnieżdżonych, zakaz `model_construct` | (nowa — realizuje A-07) |
| 6 | DEC-004 | Tylko `datetime`/`str` dla czasu, odrzucanie epoch i danych binarnych | Przyjąć po A-03 |
| 7 | DEC-003 | `Decimal` bez `float`/`bool` | Przyjąć kierunek |
| 8 | DEC-006 | Tożsamość przez `instrument_id`, równość = snapshot | Przyjąć z doprecyzowaniem (wykonane) |
| 9 | DEC-007 | Wyrównanie świec do epoki Unix | `[start,end)` i długość sensowne; wyrównanie — założenie do potwierdzenia |
| 10 | DEC-012 | Znormalizowane statusy kontraktu | Nie zatwierdzać jeszcze mapowania; potrzebna tabela i obsługa nieznanych statusów |
| 11 | DEC-002 | Wsparcie wyłącznie Pythona 3.14 | Warunkowo; potwierdzić zgodność GUI przed fazą GUI |
| 12 | DEC-008, DEC-009, DEC-011, DEC-013, DEC-015 | Rezerwacja pakietów, przyczyna jakości, niezmienniki zdarzenia, źródła, ID zdarzenia | Przyjąć jako niezmienniki rekordu (bez deklaracji kompletnego replay/no-look-ahead) |
| 13 | DEC-016, DEC-018, DEC-019 | Przypinanie zależności, `PYTHONOPTIMIZE` per sesja, LF | Przyjąć (DEC-016 z określeniem zakresu odtwarzalności) |
| 14 | DEC-023, DEC-024, DEC-025 | Zakres kontroli braku I/O, dokumenty wymagań i audytów w repo, test odnośników | (nowe) |

## Rejestr decyzji

### DEC-001 — Architektura i stos technologiczny
- Data: 2026-10-22 · Status: **ACCEPTED** (wymagania FAZY 0 §2)
- Problem: wybór architektury i narzędzi.
- Decyzja: modularny monolit w układzie `src/`; Python na Windows 11; Pydantic v2, pytest,
  mypy, Ruff, `pyproject.toml`; docelowo PySide6 (GUI) i SQLite; dokumentacja Markdown w Git.
- Uzasadnienie: wymagania użytkownika; pojedyncza aplikacja desktopowa.
- Konsekwencje: PySide6 i SQLite nie są jeszcze zależnościami (instalacja w fazach, które ich użyją).

### DEC-002 — Wersja Pythona
- Data: 2026-10-22, zmieniona w korekcie 1 · Status: **PROPOSED**
- Problem: jedyny dostępny i przetestowany interpreter to Python 3.14.5.
- Decyzja: `requires-python = ">=3.14,<3.15"` (korekta 1; wcześniej `>=3.14`, co obejmowało
  nieprzetestowane przyszłe wydania); mypy i Ruff celują w 3.14.
- Uzasadnienie: deklarować wyłącznie przetestowaną gałąź wydań.
- Konsekwencje: przejście na 3.15 wymaga świadomej zmiany i testów; przed fazą GUI potwierdzić
  dostępność kół PySide6 dla 3.14 (OQ-06).

### DEC-003 — Reprezentacja wartości finansowych
- Data: 2026-10-22 · Status: **PROPOSED** (użycie `Decimal` — ACCEPTED jako wymaganie §6)
- Problem: uniknięcie utraty precyzji.
- Decyzja: `Decimal`; wejście tylko `Decimal`/`int`/`str`; `float` i `bool` odrzucane;
  NaN/±Infinity odrzucane; JSON jako string. Dziedzina wartości: DEC-020.
- Uzasadnienie: `float` wprowadza błąd binarny niezauważalnie; giełdy podają liczby jako tekst.
- Konsekwencje: konektory muszą przekazywać tekst z API bez konwersji przez `float`.

### DEC-004 — Czas i typy wejścia
- Data: 2026-10-22, rozszerzona w korekcie 1 · Status: **PROPOSED** (UTC i odrzucanie czasu naiwnego — ACCEPTED jako wymaganie §6)
- Problem: niejednoznaczność stref i jednostek czasu; obejście zakazu epoch przez `bytes` (A-03).
- Decyzja: pola czasu przyjmują **wyłącznie** świadome `datetime` lub `str` ISO 8601 z
  przesunięciem; normalizacja do UTC; odrzucanie liczb, tekstów numerycznych, `date`, `time`
  i innych typów. Dane binarne (`bytes`, `bytearray`, `memoryview`) są odrzucane w każdym polu
  każdego kontraktu (walidator modelu bazowego).
- Uzasadnienie: jednostki epoch musiałyby być zgadywane — wymagania zabraniają założeń.
  Odrzucanie danych binarnych w jednym miejscu zamyka całą klasę obejść (czas, liczby, teksty,
  enumy — luki E-1–E-3 z korekty 1), zamiast łatać pola pojedynczo.
- Konsekwencje: konwersja epoch → `datetime` i dekodowanie bajtów w konektorach, jawnie.

### DEC-005 — Niemutowalność, nieznane pola, wersjonowanie schematu
- Data: 2026-10-22, zmieniona w korekcie 1 · Status: **PROPOSED**
- Decyzja: `frozen=True`, `extra="forbid"`; `schema_version` w rekordach najwyższego poziomu
  (Instrument, MarketTick, Candle, Trade, MarketEvent) jako **liczba całkowita** — `bool`,
  `float`, `Decimal`, `str` odrzucane na ścieżce Python i JSON (A-02); obiekty wartości
  (`DataQuality`, `MetricValue`) bez własnej wersji. Ścieżki tworzenia rekordów: DEC-021.
- Uzasadnienie: wymagania (niemutowalność, wersjonowanie); wykrywanie literówek i danych z
  innego schematu; znacznik wersji nie może być wynikiem koercji typu.
- Konsekwencje: każda niekompatybilna zmiana kontraktu podnosi `SCHEMA_VERSION` (DEC-022);
  strategia migracji danych zapisanych w SQLite — do ustalenia przy module storage.

### DEC-006 — Tożsamość instrumentu
- Data: 2026-10-22, doprecyzowana w korekcie 1 · Status: **PROPOSED**
- Decyzja: tożsamość domenowa = `instrument_id` = `<EXCHANGE>:<MARKET_TYPE>:<SYMBOL>`; symbol
  przechowywany dosłownie; `:` i białe znaki zabronione w symbolu; brak kontroli
  `symbol == base + quote`. **Równość modeli (`==`, `hash`) oznacza równość całego snapshotu**
  metadanych, nie tożsamość (A-04); kolekcje instrumentów kluczuje się przez `instrument_id`.
- Uzasadnienie: brak niejawnego łączenia giełd; zachowanie semantyki symboli; snapshoty metadanych
  w czasie (zmiana statusu, tick size) są różnymi rekordami tego samego instrumentu.
- Konsekwencje: `MarketEvent` odwołuje się do instrumentu przez `instrument_id` (OQ-11); `__eq__`
  nie jest zmieniany.

### DEC-007 — Świece
- Data: 2026-10-22 · Status: **PROPOSED** (semantyka `[start, end)` — ACCEPTED jako wymaganie §5)
- Decyzja: `end - start == interval.duration`; `start` wyrównany do wielokrotności interwału
  od epoki Unix; interwały: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d.
- Uzasadnienie: wykrywanie błędnie zbudowanych świec; interwały o stałej długości.
- Konsekwencje: wyrównanie do epoki jest założeniem wymagającym potwierdzenia w dokumentacji
  giełd (OQ-03); interwały tygodniowe/miesięczne nieobsługiwane.

### DEC-008 — Zarezerwowane pakiety `core.config`, `core.events`; zawartość `core.clock`
- Data: 2026-10-22 · Status: **PROPOSED**
- Problem: wymagana struktura zawiera katalogi bez zadań w FAZIE 0; zakaz tworzenia atrap.
- Decyzja: `core.config` i `core.events` zawierają tylko `__init__.py` z opisem; `core.clock`
  zawiera `ensure_utc` i `UTC_EPOCH` używane przez kontrakty.
- Konsekwencje: MODULE_MAP oznacza `config` i `events` jako ZAREZERWOWANE.

### DEC-009 — Przyczyna w DataQuality i tekst jednoliniowy
- Data: 2026-10-22, doprecyzowana w korekcie 1 · Status: **PROPOSED**
- Decyzja: `reason` wymagane dla każdego statusu poza `VALID`; dozwolone dla `VALID`.
  `ReasonText` (także `MarketEvent.rejection_reason`) jest jednoliniowy: zabronione są wszystkie
  separatory linii w rozumieniu `str.splitlines()` — LF, CR, CR LF, VT, FF, U+001C–U+001E,
  U+0085, U+2028, U+2029 (A-06 i luka E-4); tabulator dozwolony.
- Uzasadnienie: stan zdegradowany zawsze wyjaśniony; tekst jednoliniowy bezpieczny dla logów i GUI.

### DEC-010 — Wartość transakcji
- Data: 2026-10-22, zmieniona w korekcie 1 · Status: **PROPOSED**
- Problem (A-01): poprzednie wykonanie (`localcontext(prec=100)`) nie zapewniało dokładności dla
  danych o więcej niż 100 cyfrach i dziedziczyło zaokrąglanie, pułapki i zakres wykładników z
  kontekstu wywołującego (wycieki `decimal.Inexact`, `decimal.Overflow`).
- Decyzja: `Trade.value_usdt` musi być równe `price * quantity` dokładnie. Iloczyn liczony w
  prywatnym kontekście o precyzji = suma liczby cyfr czynników (iloczyn n- i m-cyfrowy ma ≤ n+m
  cyfr, więc nie ma zaokrąglenia), z pełnym zakresem wykładników i wszystkimi pułapkami;
  kontekst wywołującego nie jest używany ani zmieniany. Każdy błąd arytmetyki → `ValidationError`.
  Dodatkowo dane wejściowe są ograniczone dziedziną DEC-020.
- Uzasadnienie: dla kontraktu liniowego USDT wartość = cena × ilość aktywa bazowego; reguła musi
  dawać ten sam wynik dla tego samego rekordu w każdym środowisku.
- Konsekwencje: konektor wylicza wartość sam; zaokrąglona wartość z giełdy zostałaby odrzucona;
  iloczyn wymagający > 18 miejsc po przecinku nie ma poprawnej wartości (DEC-020).

### DEC-011 — Niezmienniki MarketEvent
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `window_start < window_end <= detected_at`; `rejection_reason` ⇔ `REJECTED`;
  `VERIFIED` wymaga jakości `VALID`; wartości jako krotki `MetricValue(name, value, unit)`,
  min. 1, unikalne nazwy.
- Uzasadnienie: spójność deklarowanych czasów, jednoznaczność statusów, wiele metryk dla D3.
- Konsekwencje (doprecyzowane w korekcie 1): to niezmienniki **pojedynczego rekordu**; nie
  dowodzą braku look-ahead w detektorze ani deterministycznego ID (DATA_CONTRACTS.md §8).

### DEC-012 — Znormalizowany status kontraktu
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `ContractStatus` = `PRE_LAUNCH`, `TRADING`, `SETTLING`, `CLOSED`; mapowanie
  statusów giełdowych w konektorach.
- Konsekwencje: mapowanie jest stratne i niezweryfikowane; przed konektorami potrzebna jawna
  tabela mapowania i reguła dla nieznanych statusów (OQ-03).

### DEC-013 — Źródło danych
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `DataSource` = `REST`, `WEBSOCKET`, `REPLAY`, `SYNTHETIC`; dane testowe zawsze `SYNTHETIC`.

### DEC-014 — Dokumentacja niezależna od agenta AI
- Data: 2026-10-22 · Status: **ACCEPTED** (wymagania FAZY 0 §9)
- Decyzja: `AGENTS.md` jedynym punktem wejścia; `CLAUDE.md` i `.github/copilot-instructions.md`
  tylko wskazują AGENTS.md; hierarchia źródeł prawdy jak w AGENTS.md §2; stan wyłącznie w
  `docs/PROJECT_STATE.md`.

### DEC-015 — Identyfikator zdarzenia
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `event_id` (UUID) wymagany i dostarczany przez producenta; model niczego nie losuje.
- Uzasadnienie: warunek konieczny (nie wystarczający) deterministycznego odtwarzania. Schemat
  wyznaczania (np. UUIDv5 z danych zdarzenia) — OQ-09.

### DEC-016 — Przypinanie zależności
- Data: 2026-10-22, doprecyzowana w korekcie 1 · Status: **PROPOSED**
- Decyzja: bezpośrednie zależności przypięte `==` w `pyproject.toml`; komplet (z przechodnimi)
  w `requirements-dev.lock` używanym jako constraints; build backend `setuptools==84.2.1`.
- Zakres odtwarzalności: przypięte są **wersje** pakietów środowiska uruchomieniowego i
  deweloperskiego. **Nie** są przypięte: skróty (hashes) artefaktów, zależności izolowanego
  środowiska budowania poza samym setuptools, wersja `pip` używana do instalacji (zalecana w
  DEVELOPMENT.md, nie wymuszana), interpreter (tylko gałąź 3.14).
- Wersje: pydantic 2.14.1, pytest 9.1.1, mypy 2.4.0, ruff 0.17.1, pip 26.2.2.

### DEC-017 — Wyłączenia z zakresu projektu
- Data: 2026-10-22 · Status: **ACCEPTED** (wymagania FAZY 0 §1, §10)
- Decyzja: brak automatycznego tradingu, brak prywatnych kluczy API, AGGR poza projektem
  (bez modyfikacji), wyłącznie publiczne API Bybit V5 i Binance USDⓈ-M.

### DEC-018 — Kontrole z włączonymi asercjami
- Data: 2026-10-22 · Status: **PROPOSED**
- Problem: w środowisku deweloperskim systemowa zmienna `PYTHONOPTIMIZE=2` wyłącza `assert`.
- Decyzja: kontrole uruchamiane po `$env:PYTHONOPTIMIZE = $null` (tylko sesja); pytest z
  `filterwarnings = error` przerywa uruchomienie, gdy asercje są wyłączone. Bez zmian w systemie.

### DEC-019 — Końce linii
- Data: 2026-10-22 · Status: **PROPOSED**
- Decyzja: `.gitattributes` z `* text=auto eol=lf`.

### DEC-020 — Dziedzina wartości Decimal
- Data: 2026-10-22 (korekta 1) · Status: **PROPOSED**
- Problem (A-01): kontrakt dopuszczał dowolną liczbę cyfr i dowolne wykładniki, więc żadna stała
  precyzja nie zapewniała poprawnych obliczeń, a skrajne wartości (np. `1e999999`) nie miały
  sensu rynkowego. Audyt wymagał jawnych granic albo dokładności w całej dziedzinie — korekta
  realizuje **oba** warunki (DEC-010 jest dokładne niezależnie od granic).
- Decyzja: każde pole `Decimal` w kontraktach: najwyżej 18 cyfr po przecinku (z zerami
  końcowymi), wartość bezwzględna < 1E+20; stałe `MAX_DECIMAL_PLACES`, `MAX_INTEGER_DIGITS`.
- Uzasadnienie: 18 miejsc = najmniejsza jednostka typowych tokenów (1 wei = 1E-18 ETH); kroki
  ceny i ilości kontraktów USDT perpetual mają kilka–kilkanaście miejsc; 1E+20 USDT o rzędy
  wielkości przekracza każdy obrót; 38 cyfr = maksymalna precyzja DECIMAL w popularnych bazach SQL.
- Konsekwencje: wartości spoza dziedziny → jawny `ValidationError` (nic nie jest zaokrąglane);
  `Trade` z iloczynem wymagającym > 18 miejsc jest odrzucany; przyszłe detektory muszą
  kwantyzować wartości metryk do 18 miejsc; zgodność z rzeczywistymi danymi giełd — OQ-14.
- Alternatywy: (a) brak granic + dokładna arytmetyka (dopuszcza wartości bez sensu rynkowego);
  (b) inne granice, np. 28 miejsc; (c) osobna, szersza dziedzina dla `MetricValue`.

### DEC-021 — Bezpieczne tworzenie i zmiana rekordów
- Data: 2026-10-22 (korekta 1) · Status: **PROPOSED**
- Problem (A-07): `model_copy(update=...)` i `model_construct` tworzyły rekordy bez walidacji,
  a zagnieżdżone instancje nie były ponownie walidowane.
- Decyzja: `ContractModel.replace(**zmiany)` — nowy rekord z pełną walidacją;
  `model_copy(update=...)` (a więc też `copy.replace`) przeciążone tak, by walidować;
  `revalidate_instances="always"` — każdy zagnieżdżony kontrakt jest walidowany ponownie;
  `model_construct` zakazany w `src/` (test AST), dopuszczalny tylko w testach.
- Uzasadnienie: jedna, zawsze walidowana ścieżka dla danych niezaufanych; `frozen` nie jest
  granicą bezpieczeństwa.
- Konsekwencje: koszt ponownej walidacji zagnieżdżonych rekordów (do oceny przy strumieniach
  transakcji; możliwa zmiana polityki tylko decyzją).

### DEC-022 — Schemat danych w wersji 2, pakiet 0.0.2
- Data: 2026-10-22 (korekta 1) · Status: **PROPOSED**
- Problem: korekta zaostrza walidację (DEC-004, DEC-005, DEC-009, DEC-020, DEC-021); procedura
  DEVELOPMENT.md §8.1 wymaga wtedy podniesienia `SCHEMA_VERSION`.
- Decyzja: `SCHEMA_VERSION = 2`; rekordy z `schema_version = 1` są odrzucane; wersja pakietu 0.0.2.
- Uzasadnienie: zgodność z własną procedurą wersjonowania; jednoznaczne odróżnienie rekordów
  sprzed i po korekcie.
- Konsekwencje: schemat 1 nie był przyjęty ani zapisywany poza fixture'ami (brak migracji).
- Alternatywa: zachować wersję 1 jako niewydaną i uznać korektę za część jej definicji
  (wymaga wyjątku od procedury §8.1 — decyzja użytkownika).

### DEC-023 — Zakres gwarancji „brak I/O w core”
- Data: 2026-10-22 (korekta 1) · Status: **PROPOSED**
- Problem (A-05): pojedynczy test `sys.modules` był przedstawiany szerzej niż sprawdzał.
- Decyzja: „brak I/O” dotyczy operacji **aplikacyjnych** (pliki, sieć, procesy) wykonywanych
  przez kod `core`, nie mechanizmów importu Pythona. Kontrolują to trzy ograniczone testy:
  (1) skan `sys.modules` po imporcie wszystkich pakietów `core`; (2) statyczna granica importów
  (lista dozwolonych modułów) i zakaz wywołań `open`/`exec`/`eval`/`compile`/`__import__`;
  (3) strażnik czasu wykonania blokujący `open`, `io.open`, `os.open`, `os.system`,
  `subprocess.Popen`, `socket.*` podczas walidacji, serializacji i kopiowania wszystkich kontraktów.
- Konsekwencje: żaden z testów nie dowodzi braku każdego możliwego I/O; nowy import w `core`
  wymaga świadomego rozszerzenia listy dozwolonych modułów (zmiana widoczna w przeglądzie).

### DEC-024 — Wymagania i materiały audytów w repozytorium
- Data: 2026-10-22 (korekta 1) · Status: **PROPOSED**
- Decyzja: zatwierdzone teksty wymagań w `docs/requirements/` (dosłownie); kopie materiałów
  audytów w `reports/phase<N>/audyt<M>/` z sumami SHA-256 oryginałów; zmiany kopii tylko w celu
  usunięcia ścieżek lokalnych, opisane w README katalogu.
- Uzasadnienie: audyt wskazał, że raporty odwoływały się do niedostępnej specyfikacji.

### DEC-025 — Automatyczna kontrola odnośników dokumentacji
- Data: 2026-10-22 (korekta 1) · Status: **PROPOSED**
- Decyzja: test `tests/contracts/test_documentation.py` sprawdza odnośniki względne, kotwice i
  ścieżki repozytorium w backtickach we wszystkich plikach `.md` (z wyjątkiem dosłownych kopii
  audytów zewnętrznych).
- Uzasadnienie: rekomendacja audytu (jednorazowy skrypt nie był narzędziem repozytorium).

## Otwarte kwestie
| ID | Kwestia | Wpływ |
|---|---|---|
| OQ-01 | Definicja i zakres „Market Scanner L1” | Projekt modułu scanner |
| OQ-02 | Parametry D1–D3 (okna, progi, odniesienia, zachowanie przy jakości ≠ VALID) | Implementacja detektorów |
| OQ-03 | Weryfikacja formatów giełdowych z dokumentacją: filtrowanie USDT perpetual, mapowanie statusów (DEC-012) i nieznane statusy, jednostki, epoch, strona agresora, transakcje pojedyncze vs zagregowane, granice i zamknięcie świec (DEC-007) | Konektory |
| OQ-04 | Czy świece agregowane lokalnie potrzebują nowej wartości `DataSource` i czy `Candle` potrzebuje `received_at` | Kontrakt Candle |
| OQ-05 | Czy wymuszać `symbol == base_asset + quote_asset` | Kontrakt Instrument |
| OQ-06 | Zgodność PySide6 z Pythonem 3.14 (DEC-002) | Środowisko, GUI |
| OQ-07 | Zakres i kryteria FAZY 1 — niezdefiniowane, wymagają zatwierdzenia użytkownika | Planowanie |
| OQ-08 | Licencja projektu | README, publikacja |
| OQ-09 | Reguły przejść statusów `MarketEvent` i schemat deterministycznego `event_id` | Silnik zdarzeń, replay |
| OQ-10 | Słownik jednostek `MetricValue.unit` (obecnie dowolny identyfikator wielkimi literami) | Kontrakt MarketEvent |
| OQ-11 | `MarketEvent` przez `instrument_id` (tekst) vs osadzony `Instrument` | Kontrakt MarketEvent, storage |
| OQ-12 | Treść dokumentacji Binance niezweryfikowana (2026-10-22: HTTP 202 u autora; w audycie przekierowanie na treść ogólną) | EXCHANGE_API.md |
| OQ-13 | Czy zmienna systemowa `PYTHONOPTIMIZE=2` na komputerze deweloperskim ma zostać (decyzja właściciela komputera) | Środowisko |
| OQ-14 | Czy dziedzina DEC-020 obejmuje wszystkie rzeczywiste ceny, ilości i iloczyny z Bybit/Binance (sprawdzić na udokumentowanych formatach przed konektorami) | Konektory, Trade |
| OQ-15 | Wydajność `revalidate_instances="always"` przy strumieniach transakcji (DEC-021) | Konektory, replay |
