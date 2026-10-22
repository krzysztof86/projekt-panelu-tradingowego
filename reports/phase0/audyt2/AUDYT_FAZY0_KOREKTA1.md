# Ponowny niezależny audyt FAZY 0 — KOREKTA 1
Data: 2026-10-22. Projekt: Market Intelligence Desktop.
Gałąź: task/faza0-korekta1.
Audytowany HEAD: f0c36e9bfe6408a6228eae87a33c04d5afbee61e.
Commit implementacji: 08c6683e89344f0a773e71073cef7f8f8ea1beaa.

## Werdykt
**Nie rekomenduję jeszcze bezwarunkowego odbioru FAZY 0 ani scalenia.**
Korekta usuwa pierwotne obejścia A-01–A-07 i E-1–E-4 w badanym zakresie, a wszystkie 588 testów przechodzą. Niezależna próba wykazała jednak nowe obejście zakazu epoch w polach czasu. Ponadto decyzje określające faktyczny kontrakt nadal mają status PROPOSED. Fundament nadaje się do przyjęcia po usunięciu luki i rozstrzygnięciu decyzji.

Nie zmieniono źródłowego repozytorium, gałęzi, decyzji ani testów projektu. Nie wykonano push ani merge. Pliki robocze i ten raport powstały wyłącznie w katalogu audytu.

## 1. Zakres i wiarygodność materiałów
Przeczytano trzy załączone raporty i zestawiono je z kodem, testami oraz dokumentacją gałęzi. Wszystkie trzy załączniki są identyczne bajtowo z plikami w repozytorium (porównanie SHA-256).
Pobrano 86 plików wskazanego HEAD przez połączenie GitHub. Ich lokalną zawartość sprawdzono względem identyfikatorów Git blob: 86 zgodnych, 0 rozbieżności.
Porównanie GitHub potwierdziło, że HEAD jest dwa commity po 08c6683. Zmiany obejmują wyłącznie PROJECT_STATE, raport, raport testów i log czystego odtworzenia. Kod, testy i konfiguracja pozostały identyczne.
[Audytowany commit](https://github.com/krzysztof86/projekt-panelu-tradingowego/commit/f0c36e9bfe6408a6228eae87a33c04d5afbee61e).

## 2. Własne uruchomienie kontroli
| Kontrola | Wynik |
|---|---|
| pytest | 588 passed, 0 failures, 0 errors, 1,40 s |
| Ruff check | All checks passed |
| Ruff format --check | 57 files already formatted |
| mypy | Success, 30 source files |
| Import w izolowanym interpreterze -I | 0.0.2 2 |
| Dodatkowa próba czasu | 6/6 niepożądanych akceptacji: 3 teksty × Python/JSON |

Użyto Pythona 3.14.5 i Pydantic 2.14.1 oraz lokalnie dostępnych narzędzi. PYTHONOPTIMIZE usunięto tylko w procesie kontroli. Pakiet zainstalowano editable w lokalnym środowisku audytu.
**To nie było niezależne odtworzenie instalacji z PyPI w zupełnie pustym środowisku.** Zależności wykorzystano z istniejącego środowiska; budowanie editable wykonano bez izolacji z dostępnego lokalnie backendu. Nie utożsamiam tego z pełnym powtórzeniem procedury autora z logu 07. Log autora jest spójny z raportem, ale pozostaje jego dowodem.
Początkowe problemy z metadanymi starej instalacji, katalogiem tymczasowym i dodatkowym końcem linii przy odtwarzaniu plików usunięto przed końcową kontrolą. Nie są ustaleniami przeciwko repozytorium; końcowy snapshot odpowiada identyfikatorom Git blob.

## 3. Ocena ustaleń
| ID | Ocena | Uzasadnienie |
|---|---|---|
| A-01 | Naprawa techniczna potwierdzona w przyjętej dziedzinie; decyzja pozostaje otwarta | Prywatny Context, precyzja n+m, niezależność od kontekstu wywołującego; jawne granice i testy Fraction |
| A-02 | Zamknięte technicznie | type(value) is int przed Literal[2]; testy 5 modeli, Python i JSON |
| A-03 | Pierwotne obejście bytes zamknięte; szersza gwarancja czasu niepełna | Nowe ustalenie K1-01 poniżej |
| A-04 | Zamknięte dokumentacyjnie | Tożsamość przez instrument_id; równość i hash dotyczą snapshotu; bez zmiany __eq__ |
| A-05 | Zamknięte w zadeklarowanym ograniczonym zakresie | Kontrola importów, AST i strażnik I/O; dokumentacja przyznaje granice dowodu |
| A-06 | Zamknięte technicznie | splitlines wykrywa CR i pozostałe separatory; testy obu pól przyczyny |
| A-07 | Zamknięte w opisanych ścieżkach | replace, walidujące model_copy z aktualizacją, copy.replace, revalidate_instances=always, testy złych instancji zagnieżdżonych |
| E-1 | Zamknięte | ISO bytes odrzucane przez model bazowy i ograniczenie wejścia czasu |
| E-2 | Zamknięte | Decimal jako schema_version odrzucany |
| E-3 | Zamknięte w badanych polach | bytes/bytearray/memoryview odrzucane na poziomie modeli; obiekty zagnieżdżone rewalidowane |
| E-4 | Zamknięte | Testy wszystkich separatorów splitlines |

Źródła: [base.py](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/f0c36e9bfe6408a6228eae87a33c04d5afbee61e/src/market_intelligence/core/models/base.py), [types.py](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/f0c36e9bfe6408a6228eae87a33c04d5afbee61e/src/market_intelligence/core/models/types.py), [trade.py](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/f0c36e9bfe6408a6228eae87a33c04d5afbee61e/src/market_intelligence/core/models/trade.py), [regresje](https://github.com/krzysztof86/projekt-panelu-tradingowego/blob/f0c36e9bfe6408a6228eae87a33c04d5afbee61e/tests/regression/test_audit1_phase0.py).

## 4. K1-01 — tekstowe epoch z pominiętą częścią całkowitą
**Priorytet P2; blokuje stwierdzenie zgodności z deklarowanym kontraktem czasu.**

Miejsce: types.py, _NUMERIC_STRING oraz _require_timestamp_input.
Wyrażenie regularne wymaga co najmniej jednej cyfry przed separatorem dziesiętnym. Teksty ".5", "+.5" i "-.5" omijają filtr; parser datetime Pydantic interpretuje je jako epoch.

Odtworzenie na poprawnym payloadzie Instrument, ze zmienionym listed_at:
| Wejście | Python model_validate | JSON model_validate_json |
|---|---|---|
| ".5" | 1970-01-01T00:00:00.500000+00:00 | taki sam wynik |
| "+.5" | 1970-01-01T00:00:00.500000+00:00 | taki sam wynik |
| "-.5" | 1969-12-31T23:59:59.500000+00:00 | taki sam wynik |

Żaden z tych tekstów nie jest ISO 8601 z przesunięciem. Przyjęcie jest sprzeczne z DATA_CONTRACTS §1 i DEC-004. Typ UtcDatetime jest wspólny dla modeli; luka ma szerszy zasięg niż listed_at.
Istniejące 588 testów przechodzi mimo tej sprzeczności.

Rekomendacja: jawnie parsować dozwolone teksty daty i wymagać strefy, zamiast polegać wyłącznie na czarnej liście formatów liczbowych. Minimalna korekta regexu powinna objąć liczby z pominiętą częścią całkowitą; pełna naprawa powinna też upewnić się, że dalej nie zachodzi automatyczne parsowanie epoch.
Dodać regresje powyższych trzech przypadków na obu ścieżkach, poprawne ISO z Z i offsetem oraz warianty ułamkowe/wykładnicze i białe znaki. Nie zmieniać oczekiwanego kontraktu tylko po to, aby zaakceptować te dane.

## 5. Decimal oraz DEC-020/010
Mechanizm dokładnego iloczynu jest poprawny dla walidowanych czynników: n- i m-cyfrowe współczynniki dają najwyżej n+m cyfr. Prywatny Context nie dziedziczy precyzji, zaokrąglania, pułapek ani zakresu wykładników wywołującego. Porównania i kontrola dziedziny nie wymagają arytmetyki zależnej od kontekstu. Nie znalazłem powtórzenia błędu A-01 w przyjętej dziedzinie.
Testy mają wartości graniczne, wrogie konteksty i niezależną wyrocznię Fraction dla 300 generowanych przykładów. To istotny dowód, mocniejszy od samego odrzucenia dawnego przykładu 101 miejsc przez nowy limit.

**DEC-020 wymaga jawnej decyzji użytkownika.** Wspólne 18 miejsc dla ceny, ilości, wartości transakcji i metryk nie wynika automatycznie z dokładności arytmetyki. Poprawne osobno czynniki mogą dawać iloczyn spoza dziedziny, np. 1E-10 × 1E-10 = 1E-20. Obecne odrzucenie jest świadomie udokumentowanym ograniczeniem produktu, nie błędem mnożenia.
Rekomenduję rozdzielić dziedziny czynników, iloczynu i metryk albo poprzeć wspólną dziedzinę analizą docelowych formatów. OQ-14 pozostaje otwarte; raport uczciwie to przyznaje. Nie należy oznaczać zgodności z rzeczywistymi danymi giełdowymi jako zweryfikowanej.
Usunąć z DATA_CONTRACTS twierdzenie „żadna kwota kryptowalutowa nie wymaga więcej” — nie jest dowodem pokrycia docelowych wartości i iloczynów. „Odpowiednik DECIMAL(38,18)” traktować jako opis zakresu liczbowego, nie identycznej semantyki reprezentacji: kod odrzuca również nadmiarowe zera końcowe.
Doprecyzować zdanie o sumie miejsc czynników: o reprezentowalności rozstrzyga dokładny iloczyn po usunięciu jego zer końcowych, nie sama suma skal czynników.

**DEC-010:** rekomenduję przyjąć dokładną równość dla kontraktu transakcji liniowej po rozstrzygnięciu dziedziny. Jeśli konektor otrzymuje wartość zaokrągloną przez źródło, trzeba zapisać ją osobno lub jawnie określić sposób uzyskiwania value_usdt; nie wprowadzać ukrytej tolerancji.

## 6. model_copy, revalidate_instances oraz DEC-021
replace odtwarza pełny rekord i uruchamia model_validate. Niepusta aktualizacja przez model_copy idzie tą samą drogą. Test copy.replace rzeczywiście wykrywa niepoprawną zmianę. Rewalidacja instancji zamyka wstrzyknięcie błędnego Instrument, DataQuality i MetricValue przez model_construct.
model_copy bez aktualizacji jest celowo kopią zaufanego ważnego rekordu; nie stanowi walidatora instancji wcześniej uszkodzonej przez obejście API.
Zakaz model_construct w src jest regułą kontroli kodu, a frozen nie jest zabezpieczeniem przed dowolnym kodem Python. Dokumentacja słusznie to rozróżnia.
Rekomenduję przyjąć DEC-021 jako obecną politykę. OQ-15, czyli pomiar kosztu rewalidacji, powinno poprzedzać moduł wymagający przepustowości strumienia; sam brak benchmarku nie jest błędem poprawności FAZY 0.

## 7. Testy i raportowanie
Własne uruchomienie potwierdza liczby 588, 57 i 30. Zmiany dotychczasowych testów są opisane; zastąpienie wartości spoza nowej dziedziny jest konsekwencją DEC-020, której zatwierdzenie nadal jest wymagane. Nie uznaję samej liczby testów za dowód kompletności.
Test mutacyjny autora obejmuje 11 wybranych cofnięć. Jego wyniku 11/11 nie uruchamiałem ponownie; nie przedstawiam go jako własnego pomiaru. Regresje i próby własne sprawdzono niezależnie.
Kontrole I/O i odnośników są przydatne, ale ograniczone. Test dokumentacji potwierdza istnienie celów i wybrane kotwice/ścieżki, a nie prawdziwość tekstu ani wszystkich wariantów składni Markdown. Nie znalazłem powodu, by traktować te ograniczenia jako nowy bloker.
Dodać regresję K1-01 i po poprawce ponownie wykonać komplet kontroli na nowym wskazanym commicie.

## 8. Dokumentacja, handoff i DEC-022
Repozytorium zawiera wymagania, zlecenie korekty, kopię audytu, mapę modułów, procedurę instalacji i aktualny stan. AGENTS jest sensownym punktem wejścia także dla innego agenta. Raporty rozróżniają gotowość do audytu od przyjęcia fazy.
Nadal pozostały drobne niespójności: DATA_CONTRACTS odsyła wpływ dziedziny na giełdy do OQ-03 zamiast wskazać także OQ-14; opis MarketEvent w kodzie nadal skrótowo mówi o „no detection from future data”, podczas gdy dokumentacja trafnie ogranicza gwarancję do relacji czasów jednego rekordu. Zalecam wyrównać te sformułowania.
DEC-022: wersja 2 i pakiet 0.0.2 są spójne z fixture'ami, kodem, testami i procedurą zmiany kontraktu. Rekomenduję zachować tę wersję. Zmiana statusu decyzji wymaga użytkownika; nie ma potrzeby automatycznie wracać do niewydanej wersji 1.
Dalszą poprawkę walidacji czasu należy przeprowadzić według uzgodnionej polityki dla niewydanego schematu: obecna procedura wymaga podbicia przy zaostrzeniu albo jawnego zatwierdzenia wyjątku.

## 9. Warunki zamknięcia
1. Naprawić K1-01 i dodać testy Python/JSON; ponowić pełne kontrole.
2. Rozstrzygnąć DEC-020 i powiązaną DEC-010; zaakceptować świadomie zakres i ryzyko dziedziny lub ją poprawić.
3. Rozstrzygnąć DEC-021, DEC-022 oraz pozostałe decyzje wpływające na odbierany kontrakt, zwłaszcza DEC-004/005. Audyt nie zmienia ich statusu.
4. Skorygować opis dziedziny i drobne niespójności dokumentacji.
5. Zapisać nowy commit i wyniki; dopiero wtedy podjąć decyzję o odbiorze. Zakres FAZY 1 zatwierdzić osobno.

Blokery: K1-01 oraz brak rozstrzygnięć kontraktowych wymaganych warunkami poprzedniego audytu. Brak GUI, konektorów i bazy jest zgodny z zakresem FAZY 0 i nie jest blokerem.

