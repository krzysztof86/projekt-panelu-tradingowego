# Specyfikacja FAZY 0 (tekst źródłowy)

| Pole | Wartość |
|---|---|
| Źródło | Polecenie użytkownika (właściciela projektu) rozpoczynające FAZĘ 0, 2026-10-22 |
| Status | Wymagania zatwierdzone przez użytkownika jako zakres FAZY 0 |
| Wersja dokumentu | 1 — treść przeniesiona dosłownie; dodano wyłącznie ten nagłówek z tabelą oraz znaczniki Markdown (`##`/`###` przed tytułami sekcji, ``` wokół drzew katalogów) |
| Dodano do repozytorium | Korekta 1 FAZY 0 (ustalenie audytu: „dołączyć zatwierdzoną specyfikację FAZY 0”) |

Numeracja sekcji poniżej jest tą, do której odwołują się raporty `reports/phase0/FAZA0_*.md`.
Korekty wynikające z audytu opisuje [FAZA0_KOREKTA1_ZLECENIE.md](FAZA0_KOREKTA1_ZLECENIE.md).

---

MARKET INTELLIGENCE DESKTOP
FAZA 0 — FUNDAMENT PROJEKTU, KONTRAKTY DANYCH I DOKUMENTACJA NIEZALEŻNA OD AGENTA

TWOJA ROLA
Działasz jako Senior Python Software Engineer i Software Architect.
Pracujesz pod nadzorem architektonicznym. Implementujesz wyłącznie FAZĘ 0.
Nie wolno samodzielnie zmieniać architektury, rozszerzać zakresu ani przechodzić do następnej fazy.
Projekt musi być możliwy do kontynuowania przez dowolnego kompetentnego programistę lub agenta AI bez dostępu do historii tej rozmowy.

## 1. CEL PROJEKTU
Tworzymy natywną aplikację Windows do wykrywania anomalii na kontraktach kryptowalutowych USDT Perpetual.
Docelowe funkcjonalności:

* Market Scanner L1.
* Price Velocity Detector D1.
* Relative Volume Detector D2.
* Delta/Price Divergence Detector D3.
* Market Data Quality.
* Historia zdarzeń i deterministyczne odtwarzanie.
* Interfejs Windows w PySide6.

Źródła danych: publiczne API Bybit V5 i Binance USDⓈ-M Futures.
AGGR pozostaje osobnym narzędziem analizy Order Flow.
Automatyczne składanie zleceń nie należy do projektu.
FAZA 0 dotyczy wyłącznie fundamentów, modeli danych, dokumentacji i testów.

## 2. ARCHITEKTURA

* Python, Windows 11.
* Modularny monolit z układem `src/`.
* Docelowe GUI: PySide6.
* Modele: Pydantic v2.
* Testy: pytest.
* Typowanie: mypy.
* Linting: Ruff.
* Konfiguracja: `pyproject.toml`.
* Docelowa baza: SQLite.
* Dokumentacja: Markdown, utrzymywana w Git.

Stosuj izolowane środowisko Python. Nie instaluj zależności niepotrzebnych w tej fazie.

## 3. ANALIZA ŚRODOWISKA
Przed rozpoczęciem sprawdź:

* System operacyjny i architekturę.
* Dostępne wersje Python.
* Git i stan repozytorium.
* Istniejące pliki katalogu roboczego.
* Kompatybilność zależności.
* Możliwość tworzenia środowiska wirtualnego.

Udokumentuj wyniki. Nie nadpisuj istniejących projektów i nie modyfikuj globalnego środowiska Python.

## 4. STRUKTURA REPOZYTORIUM

```
market-intelligence-desktop/
├── AGENTS.md
├── CLAUDE.md
├── .github/
│   └── copilot-instructions.md
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── .gitignore
├── .env.example
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_CONTRACTS.md
│   ├── DETECTORS.md
│   ├── EXCHANGE_API.md
│   ├── TEST_PLAN.md
│   ├── DECISIONS.md
│   ├── MODULE_MAP.md
│   ├── PROJECT_STATE.md
│   ├── HANDOFF.md
│   └── DEVELOPMENT.md
├── src/
│   └── market_intelligence/
│       ├── __init__.py
│       └── core/
│           ├── __init__.py
│           ├── models/
│           ├── config/
│           ├── clock/
│           └── events/
├── tests/
│   ├── unit/
│   ├── contracts/
│   └── fixtures/
└── reports/
    └── phase0/
```

Nie twórz atrap detektorów, konektorów ani GUI.

## 5. KONTRAKTY DANYCH
Zaimplementuj sześć modeli:

Instrument

* Giełda: BYBIT albo BINANCE.
* Symbol giełdowy.
* Rodzaj rynku: USDT_LINEAR_PERPETUAL.
* Base asset i quote asset.
* Status kontraktu.
* Tick size jako dodatni Decimal.
* Opcjonalny czas notowania w UTC.

MarketTick

* Instrument.
* Cena ostatniej transakcji.
* Czas giełdowy, jeżeli dostępny.
* Czas odbioru.
* Źródło i status jakości.

Candle

* Instrument i interwał.
* Początek i koniec okresu UTC.
* OHLC.
* Obrót w USDT.
* Status zamknięcia świecy.
* Źródło i jakość danych.

Stosuj wewnętrzną semantykę przedziału `[start, end)`.

Trade

* Instrument.
* Identyfikator transakcji.
* Cena i ilość aktywa bazowego.
* Wartość w USDT.
* Strona agresora BUY/SELL.
* Czas wykonania i odbioru.
* Źródło oraz jakość.

DataQuality

* VALID.
* WARMUP.
* STALE.
* GAP.
* INSUFFICIENT_DATA.
* INVALID.

Każdy stan musi umożliwiać zapis przyczyny.

MarketEvent

* ID zdarzenia i instrumentu.
* ID detektora D1/D2/D3.
* Wersja detektora i konfiguracji.
* Czas wykrycia.
* Początek i koniec okna.
* Kierunek zdarzenia.
* Wartości obserwowane i referencyjne.
* Jakość danych.
* Status.
* Opcjonalna przyczyna odrzucenia.

Dozwolone statusy: CANDIDATE, ANALYZING, VERIFIED, REJECTED, EXPIRED.
Nie implementuj jeszcze silnika zmiany statusów.

## 6. WALIDACJA

* Stosuj Decimal do reprezentacji wartości finansowych.
* Odrzucaj niedozwolone NaN i Infinity.
* Kontroluj dodatniość ceny i ilości.
* Odrzucaj ujemny obrót.
* Sprawdzaj spójność OHLC.
* Normalizuj czas do UTC.
* Nie akceptuj naiwnych datetime.
* Rozróżniaj brak danych od zera.
* Nie łącz niejawnie różnych giełd i typów kontraktów.
* Zachowuj semantykę oryginalnych symboli.
* Zapewnij serializację JSON bez utraty precyzji.
* Wprowadź wersjonowanie schematu danych.
* Preferuj niemutowalne modele.

Nie uzupełniaj brakujących informacji założeniami.

## 7. TESTY
Wymagane testy:

* Poprawne instrumenty Bybit i Binance.
* Odróżnianie identycznych symboli na różnych giełdach.
* Odrzucenie Spot i COIN-M.
* Odrzucenie niewłaściwej waluty kwotowanej.
* Nieprawidłowe ceny, ilości i obrót.
* NaN i Infinity.
* Niespójne OHLC.
* Obsługa UTC.
* Odrzucenie naiwnego datetime.
* Brak opcjonalnego czasu giełdowego.
* Zachowanie Decimal przy serializacji.
* Kierunek agresora BUY/SELL.
* Walidacja jakości danych.
* Poprawne i niepoprawne alerty.
* Poprawność przedziałów czasowych.
* Rozróżnienie VERIFIED i REJECTED.
* Import pakietu po instalacji editable.

Dane testowe są syntetyczne i muszą być tak oznaczone.
Uruchom pytest, Ruff lint, Ruff format check, mypy i test importowania pakietu.
Nie wyłączaj kontroli wyłącznie w celu uzyskania pozytywnych wyników.

## 8. DOKUMENTACJA TECHNICZNA
Uzupełnij:

* `ARCHITECTURE.md` — architektura, granice modułów i uzasadnienie.
* `DATA_CONTRACTS.md` — pola, typy, jednostki, walidacje.
* `DETECTORS.md` — specyfikacja przyszłych D1–D3.
* `EXCHANGE_API.md` — źródła danych i oficjalna dokumentacja giełd.
* `TEST_PLAN.md` — zakres testów i kryteria odbioru.
* `DECISIONS.md` — zatwierdzone decyzje i otwarte kwestie.
* `README.md` — uruchomienie projektu od zera.
* `CHANGELOG.md` — istotne zmiany projektu.

Dokumentuj wyłącznie stan faktyczny. Nie przedstawiaj planowanych modułów jako istniejących.

## 9. AGENT-AGNOSTIC DEVELOPMENT — WYMAGANIE OBOWIĄZKOWE
Projekt musi być niezależny od konkretnego modelu AI.
Dokumentacja i kod stanowią jedyne autorytatywne źródło informacji o stanie projektu. Historia rozmów z Claude, Codex lub Copilot nie jest źródłem prawdy.

### 9.1. AGENTS.md
Utwórz w katalogu głównym `AGENTS.md`.
Dokument musi wyjaśniać:

* Cel aplikacji.
* Gdzie znajduje się dokumentacja architektury.
* Gdzie znajdują się aktualne zadania i status projektu.
* Jak uruchomić środowisko.
* Jak uruchomić testy.
* Jakie są granice modułów.
* Jakich zmian nie wolno wykonywać bez zgody.
* Jak aktualizować dokumentację.
* Jak zakończyć zadanie i przekazać projekt.

AGENTS.md powinien być krótki i jednoznaczny. Szczegółowe opisy należą do `docs/`.

### 9.2. Instrukcje dla Claude i Copilot
Utwórz:

* `CLAUDE.md`
* `.github/copilot-instructions.md`

Powinny wskazywać tę samą obowiązującą dokumentację i reguły co AGENTS.md.
Nie duplikuj obszernych specyfikacji.
Nie twórz konkurujących ze sobą zasad zależnych od używanego modelu.
Jeżeli narzędzie nie odczytuje automatycznie określonego pliku, procedura rozpoczęcia pracy musi umożliwiać jego jawne wskazanie.

### 9.3. PROJECT_STATE.md
To obowiązkowy, aktualizowany dokument przedstawiający rzeczywisty stan prac.
Musi zawierać:

* Aktualną fazę.
* Ostatni ukończony etap.
* Zakres działającej implementacji.
* Zakres niezrealizowany.
* Aktualny wynik testów i datę ich wykonania.
* Znane błędy.
* Blokery.
* Otwarty zestaw decyzji.
* Następne zatwierdzone zadanie.
* Ostatni zweryfikowany commit.

Projekt nie może zostać przekazany kolejnemu agentowi z nieaktualnym PROJECT_STATE.md.

### 9.4. MODULE_MAP.md
Utwórz mapę kodu.
Dla każdego istniejącego modułu wskaż:

* Ścieżkę.
* Odpowiedzialność.
* Publiczny interfejs.
* Wejścia i wyjścia.
* Zależności.
* Ograniczenia.
* Powiązane testy.
* Powiązaną dokumentację.

Przyszłe moduły oznacz jako PLANOWANE.
Nowy agent powinien móc ustalić właściwy plik do modyfikacji bez przeglądania całego repozytorium.

### 9.5. HANDOFF.md
Utwórz formalną procedurę przekazywania projektu.
Przed zakończeniem każdej kolejnej fazy agent musi zapisać:

* Co zostało wykonane.
* Jakie pliki zmieniono.
* Jakie decyzje podjęto.
* Jakie testy uruchomiono i z jakimi wynikami.
* Jakie problemy pozostają nierozwiązane.
* Jaki jest aktualny stan Git.
* Co jest następnym zatwierdzonym zadaniem.
* Czego nie wolno zakładać ani modyfikować.

HANDOFF.md ma opisywać sposób przekazania pracy i wskazywać aktualne raporty. Nie może zawierać nieaktualnego, równoległego opisu stanu projektu.

### 9.6. DEVELOPMENT.md
Utwórz instrukcję pracy z repozytorium, obejmującą:

* Instalację środowiska od zera.
* Instalację zależności z przypiętymi wersjami.
* Uruchomienie testów.
* Kontrolę typów i stylu.
* Uruchomienie podstawowego testu importu.
* Zasady tworzenia gałęzi i commitów.
* Procedurę aktualizacji kontraktów danych.
* Procedurę aktualizacji dokumentacji.
* Sposób diagnozowania problemów środowiskowych.

Polecenia muszą być przeznaczone dla Windows PowerShell i rzeczywiście sprawdzone w dostępnym środowisku.

### 9.7. Śledzenie decyzji
Istotne decyzje techniczne zapisuj w `DECISIONS.md`.
Każdy wpis musi zawierać:

* Identyfikator decyzji.
* Datę.
* Problem.
* Wybraną opcję.
* Uzasadnienie.
* Konsekwencje.
* Status: PROPOSED, ACCEPTED lub SUPERSEDED.

Nie zmieniaj zaakceptowanych decyzji bez zgody użytkownika.

### 9.8. Jedno źródło prawdy
Ustal następującą hierarchię:

1. Zatwierdzone wymagania i decyzje architektoniczne.
2. Faktyczny kod, testy i konfiguracja w repozytorium.
3. Aktualna dokumentacja techniczna.
4. Raporty wykonania i diagnostyka.
5. Rozmowy z agentami AI — wyłącznie kontekst pomocniczy.

Jeżeli kod, dokumentacja i zatwierdzone wymagania są sprzeczne, zgłoś rozbieżność. Nie wybieraj samodzielnie nowej architektury.

### 9.9. Aktualizacja dokumentacji
Każda przyszła zmiana musi obejmować analizę, czy należy zaktualizować:

* PROJECT_STATE.md.
* MODULE_MAP.md.
* DATA_CONTRACTS.md.
* ARCHITECTURE.md.
* DECISIONS.md.
* CHANGELOG.md.
* HANDOFF.md.
* Powiązane testy.

Dokumentacja ma być aktualizowana razem z implementacją, nie dopiero po wielu fazach.
Nie aktualizuj dokumentów niepowiązanych ze zmianą.

### 9.10. Test przejęcia projektu bez kontekstu
Po zakończeniu FAZY 0 wykonaj kontrolę dokumentacji z perspektywy programisty lub agenta, który nie zna wcześniejszych rozmów.
Na podstawie wyłącznie plików repozytorium musi być możliwe:

1. Zidentyfikowanie celu projektu.
2. Ustalenie architektury.
3. Rozpoznanie istniejących i planowanych modułów.
4. Odtworzenie środowiska.
5. Uruchomienie testów.
6. Zlokalizowanie modeli danych.
7. Rozpoznanie obowiązujących ograniczeń.
8. Ustalenie aktualnej fazy.
9. Ustalenie następnego zatwierdzonego zadania.
10. Wskazanie nierozstrzygniętych problemów.

Zweryfikuj, że wszystkie odnośniki do plików istnieją, polecenia są poprawne, a instrukcje nie są ze sobą sprzeczne.
Udokumentuj przeprowadzony test. Nie deklaruj rzeczywistego testu z innym modelem, jeśli go nie przeprowadzono.

### 9.11. Bezpieczeństwo i niezależność
Nie zapisuj w dokumentacji:

* Kluczy API.
* Tokenów dostępu.
* Haseł.
* Sekretów środowiskowych.
* Prywatnych danych uwierzytelniających.
* Niepotrzebnych ścieżek lokalnych zależnych od konkretnego komputera.

Nie twórz ukrytych zależności od pamięci Claude ani innych agentów.
Każdy ważny kontrakt i decyzja ma być odtwarzalny z repozytorium.

## 10. ZAKAZY
W FAZIE 0 nie wolno:

* Implementować REST/WebSocket.
* Łączyć się z giełdami.
* Pobierać danych rynkowych.
* Implementować D1, D2 lub D3.
* Tworzyć GUI.
* Tworzyć systemu alertów.
* Implementować automatycznego tradingu.
* Obsługiwać prywatnych kluczy API.
* Modyfikować AGGR.
* Dodawać heurystyk tradingowych.
* Zmieniać architektury bez zgody.
* Przechodzić do FAZY 1.
* Nadpisywać istniejących projektów.
* Publikować repozytorium ani wykonywać git push bez zgody.
* Deklarować niewykonanych testów jako zaliczonych.
* Pomijać dokumentacji zmian wpływających na kontrakty.
* Tworzyć dokumentacji zrozumiałej wyłącznie dla Claude Code.

## 11. RAPORTOWANIE
Utwórz:

```
reports/phase0/
├── FAZA0_RAPORT.md
├── FAZA0_TESTY.md
├── FAZA0_RYZYKA.md
├── FAZA0_ZMIANY.md
├── FAZA0_HANDOFF_AUDIT.md
└── command_logs/
```

Raport wykonania musi podawać faktyczne wersje środowiska, listę ukończonych zadań, wyniki testów oraz commit, jeżeli istnieje.
Raport testów musi zawierać dokładne polecenia, liczbę testów zaliczonych, niezaliczonych, pominiętych i nieuruchomionych.
Raport ryzyk musi wymieniać problemy, ograniczenia i decyzje oczekujące na zatwierdzenie.
Raport zmian musi wskazywać zmodyfikowane pliki i uzasadnienie.
`FAZA0_HANDOFF_AUDIT.md` musi wykazać wynik kontroli niezależności dokumentacji od modelu AI, w tym:

* Kompletność AGENTS.md.
* Zgodność CLAUDE.md i copilot-instructions.md.
* Aktualność PROJECT_STATE.md.
* Kompletność MODULE_MAP.md.
* Poprawność dokumentacji uruchomieniowej.
* Poprawność ścieżek i odnośników.
* Wykonanie testu przejęcia projektu bez kontekstu.
* Wszystkie stwierdzone braki.

## 12. WARUNKI ZAKOŃCZENIA
FAZA 0 może zostać zgłoszona jako gotowa do niezależnego audytu dopiero wtedy, gdy:

* Repozytorium ma poprawną strukturę.
* Modele i walidacje są zaimplementowane.
* Testy automatyczne przechodzą.
* Ruff i mypy nie wykazują błędów.
* Dokumentacja odpowiada rzeczywistemu kodowi.
* AGENTS.md i instrukcje agentów są spójne.
* PROJECT_STATE.md wskazuje rzeczywisty stan projektu.
* HANDOFF.md umożliwia przejęcie pracy.
* MODULE_MAP.md umożliwia szybkie zlokalizowanie modułów.
* Wykonano kontrolę dokumentacji bez wcześniejszego kontekstu.
* Raporty zawierają faktyczne wyniki.
* Nie przekroczono zakresu FAZY 0.

Jeżeli warunek nie został spełniony, zgłoś INCOMPLETE lub BLOCKED wraz z konkretną przyczyną.
ZAKOŃCZ PRACĘ PO FAZIE 0.
Nie implementuj FAZY 1.
Przekaż komplet raportów, aktualny PROJECT_STATE.md oraz informację o stanie Git do niezależnego audytu architektonicznego.
