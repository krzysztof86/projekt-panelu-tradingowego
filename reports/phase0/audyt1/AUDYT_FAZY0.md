# Niezależny audyt FAZY 0 — Market Intelligence Desktop

Data: 22 października 2026 r.  
Repozytorium: krzysztof86/projekt-panelu-tradingowego.  
Badany commit: `2fcc5f76fc171a6f7b10b5e5333ebd11df16c226`.  
Bazowy commit implementacji: `470eb03ad9bf21a4a9b175a63e5ea3b3d870f55c`.

## Decyzja

**WYMAGA POPRAWEK — nie przyjmuję FAZY 0 bez zastrzeżeń i nie rekomenduję rozpoczęcia FAZY 1 w obecnym stanie.**

Architektura, rozdzielenie zakresów i dokumentacja przekazania stanowią dobry fundament. Nie potrzeba przepisywać projektu. Istnieją jednak odtworzone błędy w centralnych walidatorach i luki testów. Zielone 277 testów nie uzasadnia deklaracji, że wszystkie niezmienniki kontraktów są spełnione.

Warunkiem odbioru są poprawki A-01–A-03, uporządkowanie dokumentacji wskazanej poniżej oraz ponowne kontrole z testami regresji. Osobnym warunkiem rozpoczęcia FAZY 1 pozostaje zatwierdzenie jej zakresu. Ten audyt nie zmienia statusów decyzji w repozytorium i nie rozpoczyna kolejnej fazy.

## 1. Zakres i metoda

Odczytałem pięć załączników: FAZA0_RAPORT.md, FAZA0_ZMIANY.md, FAZA0_TESTY.md, FAZA0_RYZYKA.md i FAZA0_HANDOFF_AUDIT.md. Wszystkie są identyczne z odpowiednikami w badanym repozytorium. Zweryfikowałem kod wszystkich modeli i prymitywów, testy, konfigurację, syntetyczne fixture'y, dokumentację techniczną i dokumenty przekazania oraz logi autora.

Repozytorium pobrałem do osobnej kopii audytowej. Przygotowałem lokalne środowisko Python 3.14.5, pip 26.2.2 i zainstalowałem projekt według jego instrukcji, z przypiętymi zależnościami. Uruchomiłem pełne kontrole i 13 dodatkowych prób diagnostycznych. Próby powstały poza repozytorium.

**Nie zmieniłem żadnego śledzonego pliku projektu.** Końcowe `git diff --exit-code` i `git status --porcelain` potwierdziły brak zmian. Nie wykonywałem push, komentarzy ani innych zapisów w GitHubie.

Porównanie bazy implementacji z badanym commitem potwierdza wyłącznie zmiany w PROJECT_STATE i reports/phase0: osiem plików, dwa późniejsze commity. Kod, testy i konfiguracja są takie same jak w bazie. Raport wspomina o „kolejnym commicie”, a obecna historia zawiera dwa późniejsze commity dokumentacyjne; nie ma to wpływu na wynik kontroli kodu.

Ograniczenie: oryginalna, pełna specyfikacja FAZY 0 nie jest dostępna w odczytanej rozmowie ani jako osobny dokument repozytorium. DECISIONS odtwarza jej „istotną treść”. Mogę potwierdzić zgodność z dostępnymi kontraktami i kryteriami w repozytorium, ale nie pełną zgodność z niedostępnym oryginałem.

## 2. Niezależnie wykonane kontrole

| Kontrola | Wynik audytu |
|---|---|
| Czysta kopia i instalacja według DEVELOPMENT | Powodzenie; Python 3.14.5 |
| pytest | **277 passed**, 0 failed, 0 skipped, 0 errors w końcowym uruchomieniu |
| Ruff check | All checks passed |
| Ruff format --check | 47 files already formatted |
| mypy strict | Brak błędów, 27 plików |
| Import izolowany | `0.0.1 1` |
| Zależności | Lista pip freeze zgodna z requirements-dev.lock |
| Zgodność pięciu załączników z repo | 5/5 identycznych |
| Brak zmian śledzonych plików | Potwierdzony |

Pierwsza próba pytest dała 276 passed i jeden błąd przygotowania katalogu tymczasowego w sandboxie. Po wskazaniu zapisywalnego TEMP ponownie uruchomiłem cały zestaw: 277 passed w 1,77 s. Nie zmieniałem testów ani ich konfiguracji i niczego nie pomijałem. To problem środowiska audytowego, nie defekt projektu.

Log autora potwierdza zgłoszone wcześniej 277 testów. Różnica 42/47 plików formatowania jest wytłumaczona w logu świeżego klonu dodaniem pięciu raportów, więc nie jest sprzecznością. Ręczny test mutacyjny autora dotyczył 275 testów i ośmiu wybranych reguł; raport uczciwie to wskazuje. Nie powtarzałem mutowania kodu. Wynik „8/8” nie jest pełnym wynikiem mutacyjnym wszystkich możliwych zmian.

Dowody wykonania: [AUDYT_FAZY0_WYNIKI.txt](AUDYT_FAZY0_WYNIKI.txt).  
Odtwarzalne próby dodatkowe: [AUDYT_FAZY0_PROBY.py](AUDYT_FAZY0_PROBY.py). Skrypt należy uruchomić interpreterem środowiska z zainstalowanym projektem; zapisuje obserwacje, nie modyfikuje modeli. Jego kod wyjścia 0 oznacza zakończenie diagnostyki, nie poprawność kontraktów.

## 3. Usterki i rozbieżności

### A-01 — P1: Trade nie sprawdza dokładnego iloczynu i zależy od kontekstu Decimal

Źródło: [trade.py:41](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/2fcc5f76fc171a6f7b10b5e5333ebd11df16c226/src/market_intelligence/core/models/trade.py#L41), DEC-010, test `test_high_precision_product_is_exact`.

Walidator stosuje `localcontext(prec=100)`, chociaż typy wejściowe nie ograniczają liczby cyfr. Ponadto dziedziczy zaokrąglanie, pułapki i granice wykładników z kontekstu wywołującego. Stała precyzja nie zapewnia deklarowanej dokładności. Takie działanie kontekstu opisuje [dokumentacja Decimal](https://docs.python.org/3.14/library/decimal.html).

Odtworzone przypadki, przy pozostałych polach poprawnych i syntetycznych:

- Cena `p = "1." + "0" * 99 + "1"`, ilość `"1"`, wartość `"1"`: **rekord przyjęty**, choć matematyczny iloczyn jest większy od 1.
- Ta sama cena i ilość, wartość równa dokładnie `p`: **ValidationError**, choć wartość jest poprawna.
- Ten sam pierwszy rekord przy ROUND_UP: odrzucony, podczas gdy przy domyślnym zaokrąglaniu jest przyjmowany.
- Ten sam rekord z aktywną pułapką Inexact: wycieka wyjątek `decimal.Inexact`.
- Cena `1e999999`, ilość `10`, dokładna skończona wartość `1e1000000`: wycieka `decimal.Overflow`.

Wpływ: centralna reguła finansowa może przyjąć błędną wartość, odrzucić poprawną, zachowywać się różnie dla tego samego rekordu i zwracać wyjątki inne niż przewidywane błędy walidacji. To przypadki skrajne, ale obecny kontrakt jawnie je dopuszcza; nie twierdzę, że odpowiadają typowym cenom giełdowym.

**Konieczna poprawka przed odbiorem:** jawnie ustalić dopuszczalną liczbę cyfr i zakres wykładników albo zapewnić rzeczywiście dokładny iloczyn w całej dopuszczonej dziedzinie. Uniezależnić wynik od otaczającego kontekstu i określić sposób zgłaszania błędów arytmetyki. Dodać testy ponad 100 cyfr, granic wykładników oraz zmienionych ustawień kontekstu. Obecny test obejmuje tylko 37 cyfr.

### A-02 — P2: schema_version przyjmuje bool i float

Źródło: [base.py:10](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/2fcc5f76fc171a6f7b10b5e5333ebd11df16c226/src/market_intelligence/core/models/base.py#L10), [test_serialization.py](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/2fcc5f76fc171a6f7b10b5e5333ebd11df16c226/tests/contracts/test_serialization.py).

`Literal[1]` w badanej wersji Pydantic przyjmuje `True` oraz `1.0` i normalizuje je do liczby całkowitej 1. Potwierdziłem to zarówno dla danych Python, jak i JSON `true` / `1.0`.

Wpływ: wersjonowanie nie egzekwuje ściśle typu znacznika deklarowanego w kontrakcie i schemacie JSON. Nie oznacza to przyjęcia wersji 2; problem dotyczy akceptacji niewłaściwego typu.

**Konieczna poprawka przed odbiorem:** wymusić znacznik całkowitoliczbowy z wykluczeniem bool i float, albo jawnie zatwierdzić i udokumentować obecną koercję. Rekomenduję ścisły znacznik. Testować wszystkie pięć modeli wersjonowanych, obie ścieżki wejścia i wartości true, false, 1.0, 0, 2, "1", null. Obecne testy pomijają true i 1.0.

### A-03 — P2: liczbowy timestamp można przemycić jako bytes

Źródło: [types.py:47](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/2fcc5f76fc171a6f7b10b5e5333ebd11df16c226/src/market_intelligence/core/models/types.py#L47), DEC-004.

`Instrument(..., listed_at=b"1767225600")` zostaje przyjęty jako `2026-01-01T00:00:00+00:00`. Walidator wstępny sprawdza liczby i tekst str, ale nie bytes; dalszy parser rozpoznaje epoch.

Wpływ: obejście jawnego zakazu zgadywania jednostek epoch. Dotyczy wejścia Python; nie jest to zarzut dotyczący JSON, który nie ma typu bytes.

**Konieczna poprawka przed odbiorem:** ograniczyć wejście do udokumentowanych typów datetime/str albo równie rygorystycznie obsłużyć wszystkie dodatkowe dopuszczane reprezentacje. Dodać testy bytes zawierających epoch i ISO oraz innych nieobsługiwanych typów.

### A-04 — P2, dokumentacja: tożsamość instrumentu nie jest równością całego modelu

Źródło: [instrument.py:25](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/2fcc5f76fc171a6f7b10b5e5333ebd11df16c226/src/market_intelligence/core/models/instrument.py#L25), DEC-006, testy TestIdentity.

Dwa rekordy o tej samej giełdzie, rynku i symbolu, ale innym statusie lub tick_size mają ten sam instrument_id, lecz `a != b`, a zbiór zawiera dwa elementy. To prawidłowa możliwość dla snapshotów metadanych; nie rekomenduję automatycznej zmiany __eq__.

**Wymagane doprecyzowanie przed implementacją konsumentów:** identyfikacja domenowa i klucze kolekcji przez instrument_id; porównanie modeli oznacza równość całych snapshotów. Dodać test zmiany metadanych przy stałym ID. Obecne testy sprawdzają tylko różne giełdy i całkowicie identyczne definicje.

### A-05 — P2, dokumentacja i testy: gwarancja „braku I/O” jest szersza od kontroli

Źródło: [test_package_import.py:45](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/2fcc5f76fc171a6f7b10b5e5333ebd11df16c226/tests/contracts/test_package_import.py#L45), ARCHITECTURE §3.

Test sprawdza obecność kilkunastu nazw bibliotek w sys.modules po imporcie core.models. Nie wykryje np. `open(...)`, I/O uruchomionego dopiero podczas metody ani nie kontroluje wszystkich zarezerwowanych pakietów core. Przegląd bieżącego kodu nie ujawnił własnych operacji I/O w core.

**Poprawka:** opisać test jako ograniczoną kontrolę zależności po imporcie. Przed rozbudową core uzupełnić ją o kontrolę granic importów i celowane próby blokujące własne operacje sieciowe/plikowe podczas wykonywania kodu domenowego. Nie traktować skanowania sys.modules jako dowodu całkowitego braku I/O. Importy bibliotek same mogą korzystać z mechanizmów plikowych Pythona; zasada powinna dotyczyć operacji aplikacyjnych.

### A-06 — P3: ReasonText dopuszcza powrót karetki

Źródło: [types.py:80](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/2fcc5f76fc171a6f7b10b5e5333ebd11df16c226/src/market_intelligence/core/models/types.py#L80), testy DataQuality.

`reason="first\rsecond"` przechodzi, mimo opisu „jedna linia”. Test obejmuje LF, ale nie CR. **Poprawka:** jawnie zdefiniować zakazane separatory linii, odrzucać co najmniej CR i LF, dodać testy CR/CRLF. Niski wpływ; warto zamknąć w tym samym pakiecie korekt.

### A-07 — P2, dokumentacja przekazania: frozen nie oznacza walidacji każdej nowej instancji

Źródło: [base.py](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/2fcc5f76fc171a6f7b10b5e5333ebd11df16c226/src/market_intelligence/core/models/base.py), publiczne API Pydantic.

`i.model_copy(update={"tick_size": Decimal("-1")})` tworzy błędny snapshot; przekazanie go jako instrument do MarketTick nie odrzuca ujemnego tick_size. Odtworzyłem ten wynik. To udokumentowana właściwość API biblioteki, nie dowód, że bieżący kod używa go niepoprawnie. [Dokumentacja Pydantic](https://docs.pydantic.dev/latest/api/base_model/#pydantic.main.BaseModel.model_copy) opisuje brak walidacji danych update.

**Wymagane przed budową silnika zdarzeń:** opisać zaufane i niezaufane ścieżki tworzenia rekordów. Zakazać model_construct i model_copy(update=...) dla danych wymagających walidacji albo udostępnić bezpieczną procedurę tworzenia zmienionego rekordu. Ustalić politykę rewalidacji zagnieżdżonych instancji. Nie trzeba usuwać całego API Pydantic ani twierdzić, że frozen stanowi granicę bezpieczeństwa.

## 4. Ocena modeli

| Element | Ocena |
|---|---|
| Decimal, NaN/Inf, dodatniość | Dobre wspólne typy i testy zwykłych wejść; arytmetyka Trade wymaga A-01 |
| UTC | Normalizacja i odrzucanie czasu naiwnego poprawne w przebadanych ścieżkach; luka typów A-03 |
| Instrument | Rozdzielenie giełd i symbol dosłowny poprawne; doprecyzować A-04 |
| MarketTick | Brak exchange_time reprezentowany przez None; wymagany received_at; brak sztucznego porządkowania zegarów — sensowne |
| Candle | Poprawne OHLC, nieujemny obrót, brak różny od zera, StrictBool, długość i [start,end); wyrównanie giełdowe nadal do weryfikacji |
| Trade | Model i jednostki czytelne; reguła wartości nie zapewnia obiecanej dokładności |
| DataQuality | Status inny niż VALID wymaga powodu; drobna luka tekstu A-06 |
| MarketEvent | Poprawne lokalne warunki okna, powodu odrzucenia, jakości VERIFIED i unikalnych metryk |
| Serializacja | Testowane round-trip, tekstowy Decimal z zachowaniem reprezentacji, UTC, enumy i tuple; A-02 dotyczy odczytu wersji |
| Determinizm | Model nie losuje UUID ani nie odczytuje zegara; nie ma jeszcze implementacji replay ani algorytmu ID |

Warunek detected_at >= window_end sprawdza kolejność deklarowanych czasów. **Nie dowodzi**, że przyszły detektor nie użyje danych z przyszłości. Podobnie samo wymagane UUID nie gwarantuje deterministycznej generacji. Dokumentacja przyszłych detektorów słusznie wymaga osobnych testów tych własności.

## 5. Dokumentacja i niezależne przejęcie

Na podstawie AGENTS → PROJECT_STATE → MODULE_MAP/DEVELOPMENT można bez historii rozmowy ustalić cel, architekturę, istniejące modele, granice modułów, procedurę uruchomienia, bieżącą fazę i brak zgody na kolejną. CLAUDE i instrukcje Copilot wskazują ten sam punkt wejścia. **Niezależne przejęcie i uruchomienie istniejącego projektu udało się.** To zamyka praktyczną część zastrzeżenia R-08 dotyczącą innego wykonawcy, ale nie zastępuje pełnego porównania z brakującą pierwotną specyfikacją.

Korekty dokumentacyjne:

- Dołączyć zatwierdzoną specyfikację FAZY 0 lub wersjonowaną listę wymagań i kryteriów odbioru. Raporty odwołują się do numerów jej sekcji, których następca nie może sprawdzić.
- PROJECT_STATE „Znane błędy: brak” wymaga aktualizacji po przyjęciu wyników tego audytu.
- README ma placeholder adresu klonowania, mimo że zdalny adres jest już znany. Wstawić konkretny adres.
- FAZA0_HANDOFF_AUDIT podaje 14 plików Python w src; faktycznie są **16**, plus 11 w tests = 27. To drobna nieścisłość liczbowa.
- Rozdzielić gwarancje modelu od własności przyszłego systemu: A-04, A-05, A-07, brak look-ahead i deterministyczne ID.
- Jednorazowa kontrola odnośników nie jest narzędziem repozytorium. Dodanie jej jako odtwarzalnego narzędzia jest zaleceniem, nie powodem samodzielnego odrzucenia fazy.
- `requires-python >=3.14` dopuszcza także przyszłe wydania, mimo uzasadnienia „tylko przetestowana wersja”. Doprecyzować deklarację wsparcia; nie trzeba automatycznie zmieniać interpretera.

## 6. Decyzje PROPOSED — rekomendacje audytora

Poniższe są rekomendacjami; nie zmieniałem rejestru decyzji.

| Decyzje | Rekomendacja |
|---|---|
| DEC-003, 004 | Przyjąć kierunek: Decimal bez float/bool, UTC i jawna konwersja epoch; DEC-004 po A-03 |
| DEC-005 | Przyjąć po rozstrzygnięciu A-02 i dopisaniu granic gwarancji A-07 |
| DEC-006 | Przyjąć tożsamość przez instrument_id z doprecyzowaniem równości snapshotów |
| DEC-008, 009 | Przyjąć rezerwację pakietów i wymaganie przyczyny; poprawić A-06 |
| DEC-011, 013, 015 | Przyjąć jako niezmienniki rekordu, źródła i obowiązek dostarczenia ID; nie deklarować kompletnego replay/no-look-ahead |
| DEC-018, 019 | Przyjąć ustawienia per sesja i LF; nie zmieniać zmiennych systemowych |
| DEC-002 | Warunkowo: doprecyzować wsparcie wersji, potwierdzić zgodność GUI przed fazą GUI |
| DEC-007 | [start,end) i stała długość są sensowne; wyrównanie do epoki pozostaje założeniem do potwierdzenia dla wybranych danych giełdowych |
| DEC-010 | W obecnym wykonaniu odrzucić deklarację „dokładnie”; wymaga A-01 i zatwierdzenia dziedziny/liczenia |
| DEC-012 | Nie zatwierdzać jeszcze mapowania statusów jako zweryfikowanego; potrzebna jawna tabela i zachowanie dla nieznanych statusów |
| DEC-016 | Przypięcia odtworzyły się; przyjąć z określeniem zakresu odtwarzalności. Constraints nie są lockiem z hashami wszystkich artefaktów i izolowanego środowiska budowania |

## 7. Giełdy i kwestie przed kolejnymi modułami

W audycie odczytałem oficjalną dokumentację [Bybit Kline](https://bybit-exchange.github.io/docs/v5/market/kline) i [Bybit public Trade](https://bybit-exchange.github.io/docs/v5/websocket/public/trade). Potwierdzają odpowiednio turnover w walucie kwotowanej dla kontraktów USDT i pole S jako stronę takera. To wspiera wybrane jednostki i semantykę agresora, ale nie potwierdza całego mapowania statusów ani wszystkich granic świec.

Otwierane adresy Binance dla Aggregate Trade Streams i Kline przekierowały do nowej struktury serwisu i zwróciły treść ogólną. Nie uznaję na tej podstawie formatów Binance za zweryfikowane. Historyczna obserwacja HTTP 202 autora nie dowodzi dzisiejszej dostępności ani niedostępności treści.

Przed implementacją konektorów trzeba zamknąć OQ-03/OQ-12 i zapisać: filtrowanie USDT perpetual, mapowanie statusów, jednostki, czas epoch, stronę agresora, semantykę pojedynczych versus zagregowanych transakcji, granice i stan zamknięcia świec. Bez połączeń produkcyjnych można przygotować syntetyczne payloady zgodne z udokumentowanymi formatami i testy mapowania.

OQ-04 (pochodzenie i czas odbioru świec), OQ-09 (ID/statusy replay), OQ-10 (metryki/jednostki) i OQ-11 (odwołanie do instrumentu) należy rozstrzygać przed modułami, które od nich zależą. Brak detektorów, bazy i GUI jest zgodny z zakresem FAZY 0; nie jest usterką. Licencja wymaga decyzji właściciela, ale nie blokuje samego audytu walidatorów.

## 8. Warunki ponownego odbioru

1. Naprawić A-01; zatwierdzić precyzję i dziedzinę danych oraz dodać testy regresji także dla kontekstu Decimal.
2. Zamknąć A-02 i A-03 przez zgodność walidacji z zatwierdzonym kontraktem oraz testy obu ścieżek wejścia tam, gdzie istnieją.
3. Doprecyzować A-04, A-05 i A-07; poprawić A-06 oraz istotne nieaktualne stwierdzenia dokumentacji.
4. Zapisać zatwierdzone wymagania i rozstrzygnięcia decyzji wpływających na kontrakty. Zmiany niekompatybilne przeprowadzić według procedury wersjonowania z DEVELOPMENT.
5. Odtworzyć środowisko i ponownie uruchomić pełne kontrole. Liczba testów powinna wzrosnąć o regresje, a nie zostać ograniczona do dotychczasowych 277. Zapisać dokładny commit, wersje, wyniki i logi.
6. Osobno zatwierdzić zakres i kryteria FAZY 1; zamknąć tylko te otwarte kwestie, od których ten zakres rzeczywiście zależy.

**Ocena końcowa: fundament nadaje się do dalszego rozwijania po korektach. Obecna FAZA 0 nie spełnia warunków bezwarunkowego odbioru.**

