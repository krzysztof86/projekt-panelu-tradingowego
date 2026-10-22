# DECISIONS — decyzje techniczne i otwarte kwestie

Statusy: **ACCEPTED** (zatwierdzone przez użytkownika / wymagania), **PROPOSED** (propozycja
wykonawcy, czeka na rozstrzygnięcie użytkownika), **SUPERSEDED** (zastąpione — wskazać następcę).
Decyzji ACCEPTED nie wolno zmieniać bez zgody użytkownika. Zmiana statusu PROPOSED →
ACCEPTED wymaga decyzji użytkownika i wpisu daty. Rekomendacja audytora **nie** zmienia statusu.

Źródło „wymagania FAZY 0”: [requirements/FAZA0_SPECYFIKACJA.md](requirements/FAZA0_SPECYFIKACJA.md).
Audyt 1 FAZY 0: [reports/phase0/audyt1/AUDYT_FAZY0.md](../reports/phase0/audyt1/AUDYT_FAZY0.md)
(usterki A-01–A-07, rekomendacje §6). Korekta 1: [reports/phase0/korekta1/](../reports/phase0/korekta1/).
Audyt 2: [reports/phase0/audyt2/AUDYT_FAZY0_KOREKTA1.md](../reports/phase0/audyt2/AUDYT_FAZY0_KOREKTA1.md)
(K1-01, §9). Korekta 2: [reports/phase0/korekta2/](../reports/phase0/korekta2/). Decyzje użytkownika
z korekty 2: [requirements/FAZA0_KOREKTA2_DECYZJE.md](requirements/FAZA0_KOREKTA2_DECYZJE.md).
Audyt 3: [reports/phase0/audyt3/AUDYT_FAZY0_KOREKTA2.md](../reports/phase0/audyt3/AUDYT_FAZY0_KOREKTA2.md)
(K2-A01). Korekta 3: [reports/phase0/korekta3/](../reports/phase0/korekta3/) — poprawka obsługi błędu,
bez zmiany decyzji.

## Decyzje wymagające rozstrzygnięcia użytkownika

**Rozstrzygnięte 2026-10-22 (korekta 2, ACCEPTED):** DEC-004, DEC-005, DEC-010, DEC-020 (wariant
rozdzielonych dziedzin), DEC-021, DEC-022 oraz nowa DEC-026 — warunki 2 i 3 audytu 2 w zakresie
decyzji wpływających na kontrakt.

Nadal **PROPOSED** (kolejność według wpływu na kontrakty):

| Priorytet | Decyzja | Pytanie do użytkownika | Rekomendacja audytu 1 |
|---|---|---|---|
| 1 | DEC-003 | `Decimal` bez `float`/`bool` | Przyjąć kierunek |
| 2 | DEC-006 | Tożsamość przez `instrument_id`, równość = snapshot | Przyjąć z doprecyzowaniem (wykonane) |
| 3 | DEC-009 | Przyczyna wymagana dla jakości ≠ VALID; `ReasonText` jednoliniowy | Przyjąć; poprawić A-06 (wykonane) |
| 4 | DEC-011 | Niezmienniki pojedynczego `MarketEvent` | Przyjąć jako niezmienniki rekordu |
| 5 | DEC-007 | Wyrównanie świec do epoki Unix | `[start,end)` i długość sensowne; wyrównanie — założenie do potwierdzenia |
| 6 | DEC-012 | Znormalizowane statusy kontraktu | Nie zatwierdzać jeszcze mapowania; potrzebna tabela i obsługa nieznanych statusów |
| 7 | DEC-002 | Wsparcie wyłącznie Pythona 3.14 | Warunkowo; potwierdzić zgodność GUI przed fazą GUI |
| 8 | DEC-008, DEC-013, DEC-015 | Rezerwacja pakietów, źródła danych, ID zdarzenia | Przyjąć (bez deklaracji kompletnego replay) |
| 9 | DEC-016, DEC-018, DEC-019 | Przypinanie zależności, `PYTHONOPTIMIZE` per sesja, LF | Przyjąć (DEC-016 z określeniem zakresu odtwarzalności) |
| 10 | DEC-023, DEC-024, DEC-025 | Zakres kontroli braku I/O, dokumenty wymagań i audytów w repo, test odnośników | (brak; audyt 2: kontrole przydatne, ograniczone, nie są blokerem) |

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
- Data: 2026-10-22, rozszerzona w korektach 1 i 2 · Status: **ACCEPTED** — zatwierdzona przez użytkownika 2026-10-22 ([requirements/FAZA0_KOREKTA2_DECYZJE.md](requirements/FAZA0_KOREKTA2_DECYZJE.md))
- Problem: niejednoznaczność stref i jednostek czasu; obejście zakazu epoch przez `bytes` (A-03)
  i przez tekst bez części całkowitej, np. `".5"` (K1-01, audyt 2).
- Decyzja: pola czasu przyjmują **wyłącznie** świadome `datetime` albo tekst w profilu RFC 3339
  `YYYY-MM-DDTHH:MM:SS[.ffffff](Z|+HH:MM|-HH:MM)` (szczegóły: DATA_CONTRACTS §1.3), sprawdzany
  listą dozwolonych zapisów przed parsowaniem; normalizacja do UTC; odrzucanie liczb, tekstów
  numerycznych, każdego innego zapisu tekstowego, `date`, `time` i innych typów. Dane binarne
  (`bytes`, `bytearray`, `memoryview`) są odrzucane w każdym polu każdego kontraktu.
- Uzasadnienie: jednostki epoch musiałyby być zgadywane — wymagania zabraniają założeń. Czarna
  lista formatów okazała się niekompletna (K1-01); lista dozwolonych zapisów wyklucza każdy zapis,
  którego kontrakt nie deklaruje, w tym ciche obcinanie ułamka poniżej mikrosekundy.
- Konsekwencje: konwersja epoch → `datetime` i dekodowanie bajtów w konektorach, jawnie; teksty z
  innych źródeł (spacja zamiast `T`, `+0100`, bez sekund) wymagają jawnej normalizacji przed kontraktem.

### DEC-005 — Niemutowalność, nieznane pola, wersjonowanie schematu
- Data: 2026-10-22, zmieniona w korekcie 1 · Status: **ACCEPTED** — zatwierdzona przez użytkownika 2026-10-22 ([requirements/FAZA0_KOREKTA2_DECYZJE.md](requirements/FAZA0_KOREKTA2_DECYZJE.md))
- Decyzja: `frozen=True`, `extra="forbid"`; `schema_version` w rekordach najwyższego poziomu
  (Instrument, MarketTick, Candle, Trade, MarketEvent) jako **liczba całkowita** — `bool`,
  `float`, `Decimal`, `str` odrzucane na ścieżce Python i JSON (A-02); obiekty wartości
  (`DataQuality`, `MetricValue`) bez własnej wersji. Ścieżki tworzenia rekordów: DEC-021.
- Uzasadnienie: wymagania (niemutowalność, wersjonowanie); wykrywanie literówek i danych z
  innego schematu; znacznik wersji nie może być wynikiem koercji typu.
- Konsekwencje: zasady podnoszenia `SCHEMA_VERSION`: DEC-022 i DEC-026; strategia migracji danych
  zapisanych w SQLite — do ustalenia przy module storage.

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
- Data: 2026-10-22, zmieniona w korekcie 1 · Status: **ACCEPTED** — zatwierdzona przez użytkownika 2026-10-22 ([requirements/FAZA0_KOREKTA2_DECYZJE.md](requirements/FAZA0_KOREKTA2_DECYZJE.md))
- Problem (A-01): poprzednie wykonanie (`localcontext(prec=100)`) nie zapewniało dokładności dla
  danych o więcej niż 100 cyfrach i dziedziczyło zaokrąglanie, pułapki i zakres wykładników z
  kontekstu wywołującego (wycieki `decimal.Inexact`, `decimal.Overflow`).
- Decyzja: `Trade.value_usdt` musi być równe `price * quantity` **dokładnie, bez tolerancji**.
  Iloczyn liczony w prywatnym kontekście o precyzji = suma liczby cyfr czynników (iloczyn n- i
  m-cyfrowy ma ≤ n+m cyfr, więc nie ma zaokrąglenia), z pełnym zakresem wykładników i wszystkimi
  pułapkami; kontekst wywołującego nie jest używany ani zmieniany. Każdy błąd arytmetyki →
  `ValidationError`. Dziedziny czynników i iloczynu: DEC-020.
- Uzasadnienie: dla kontraktu liniowego USDT wartość = cena × ilość aktywa bazowego; reguła musi
  dawać ten sam wynik dla tego samego rekordu w każdym środowisku.
- Konsekwencje: konektor wylicza wartość sam. Jeśli źródło podaje wartość zaokrągloną, nie wolno
  wprowadzać ukrytej tolerancji — trzeba ją zapisać osobno albo jawnie określić sposób uzyskania
  `value_usdt` (zalecenie audytu 2, §5).

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
- Data: 2026-10-22 (korekta 1), zmieniona w korekcie 2 · Status: **ACCEPTED** — zatwierdzona przez użytkownika 2026-10-22 ([requirements/FAZA0_KOREKTA2_DECYZJE.md](requirements/FAZA0_KOREKTA2_DECYZJE.md)), wariant
  „Rozdzielić dziedziny”
- Problem (A-01): kontrakt dopuszczał dowolną liczbę cyfr i dowolne wykładniki. Audyt 2 (§5):
  wspólne 18 miejsc dla czynników i iloczynu odrzucało iloczyny poprawnych czynników
  (`1E-10 × 1E-10 = 1E-20`).
- Decyzja: dwie dziedziny z jawnymi granicami — czynniki i wartości proste (ceny, ilości,
  `tick_size`, obrót, OHLC, metryki): ≤ 18 miejsc po przecinku, \|x\| < 1E+20; iloczyn
  (`Trade.value_usdt`): ≤ 36 miejsc, \|x\| < 1E+20. Miejsca liczone z reprezentacji wejściowej
  (z zerami końcowymi). Stałe `MAX_DECIMAL_PLACES`, `MAX_PRODUCT_DECIMAL_PLACES`, `MAX_INTEGER_DIGITS`.
- Uzasadnienie: dziedzina iloczynu jest iloczynem dziedzin czynników, więc każda para poprawnych
  czynników o iloczynie < 1E+20 ma reprezentowalną wartość. Granice czynników są założeniem
  projektowym (kroki ceny/ilości kontraktów USDT perpetual, 1 wei = 1E-18), **nie** dowodem pokrycia
  danych giełdowych.
- Konsekwencje: wartości spoza dziedziny → jawny `ValidationError` (nic nie jest zaokrąglane);
  przyszłe detektory muszą kwantyzować wartości metryk do 18 miejsc; zgodność z rzeczywistymi
  formatami Bybit/Binance — OQ-14 (otwarte).

### DEC-021 — Bezpieczne tworzenie i zmiana rekordów
- Data: 2026-10-22 (korekta 1) · Status: **ACCEPTED** — zatwierdzona przez użytkownika 2026-10-22 ([requirements/FAZA0_KOREKTA2_DECYZJE.md](requirements/FAZA0_KOREKTA2_DECYZJE.md))
- Problem (A-07): `model_copy(update=...)` i `model_construct` tworzyły rekordy bez walidacji,
  a zagnieżdżone instancje nie były ponownie walidowane.
- Decyzja: `ContractModel.replace(**zmiany)` — nowy rekord z pełną walidacją;
  `model_copy(update=...)` (a więc też `copy.replace`) przeciążone tak, by walidować;
  `revalidate_instances="always"` — każdy zagnieżdżony kontrakt jest walidowany ponownie;
  `model_construct` zakazany w `src/` (test AST), dopuszczalny tylko w testach.
- Uzasadnienie: jedna, zawsze walidowana ścieżka dla danych niezaufanych; `frozen` nie jest
  granicą bezpieczeństwa. `model_copy()` bez aktualizacji kopiuje zaufany, ważny rekord i nie jest
  walidatorem instancji uszkodzonej obejściem API.
- Konsekwencje: koszt ponownej walidacji zagnieżdżonych rekordów — pomiar przed modułem wymagającym
  przepustowości strumienia (OQ-15).

### DEC-022 — Schemat danych w wersji 2, pakiet 0.0.2
- Data: 2026-10-22 (korekta 1) · Status: **ACCEPTED** — zatwierdzona przez użytkownika 2026-10-22 ([requirements/FAZA0_KOREKTA2_DECYZJE.md](requirements/FAZA0_KOREKTA2_DECYZJE.md))
- Problem: korekta 1 zaostrzyła walidację; procedura DEVELOPMENT.md §8.1 wymagała wtedy
  podniesienia `SCHEMA_VERSION`.
- Decyzja: `SCHEMA_VERSION = 2`; rekordy z `schema_version = 1` są odrzucane; wersja pakietu 0.0.2.
- Konsekwencje: schemat 1 nie był przyjęty ani zapisywany poza fixture'ami (brak migracji).
  Dalsze zaostrzenia przed odbiorem FAZY 0 (korekta 2) nie podnoszą wersji — DEC-026.

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

### DEC-026 — Wersja schematu w fazie nieprzyjętej
- Data: 2026-10-22 (korekta 2) · Status: **ACCEPTED** — zatwierdzona przez użytkownika 2026-10-22 ([requirements/FAZA0_KOREKTA2_DECYZJE.md](requirements/FAZA0_KOREKTA2_DECYZJE.md)), wariant „Zostaw 2 + polityka”
- Problem: korekta 2 zaostrza walidację czasu i zmienia dziedzinę `value_usdt`; procedura §8.1
  wymaga podbicia wersji albo jawnego wyjątku (audyt 2, §8).
- Decyzja: schemat fazy **nieprzyjętej** (niewydany, bez trwale zapisanych danych) można korygować
  bez podnoszenia `SCHEMA_VERSION`; podniesienie obowiązuje po odbiorze fazy albo po pierwszym
  trwałym zapisie danych (np. w SQLite). Korekta 2 zachowuje schemat 2 i pakiet 0.0.2.
- Konsekwencje: rekord ze `schema_version = 2` sprzed korekty 2 może nie przejść walidacji po
  korekcie (dotyczy wyłącznie fixture'ów testowych). Procedura: DEVELOPMENT.md §8.1.

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
| OQ-14 | Czy dziedzina DEC-020 (czynniki ≤ 18 miejsc, iloczyn ≤ 36 miejsc, \|x\| < 1E+20) obejmuje wszystkie rzeczywiste ceny, ilości i obroty z Bybit/Binance (sprawdzić na udokumentowanych formatach przed konektorami) | Konektory, Trade |
| OQ-15 | Wydajność `revalidate_instances="always"` przy strumieniach transakcji (DEC-021) | Konektory, replay |
| OQ-16 | Sposób przechowania `Trade.value_usdt` bez utraty dokładności: do 56 cyfr (20 + 36), więc nie `DECIMAL(38, 18)` (audyt 3, §Pozostałe ryzyka 3) | Storage |
