# FAZA 0 — audyt niezależności dokumentacji od modelu AI

Data: 2026-10-22. Wykonawca kontroli: ten sam agent AI, który przygotował FAZĘ 0.
**Nie przeprowadzono testu z innym modelem AI ani z innym człowiekiem.** Kontrola polegała na
odpowiedzi na pytania z wymagania 9.10 wyłącznie przez wskazanie plików repozytorium,
automatycznej weryfikacji odnośników oraz wykonaniu udokumentowanych poleceń w czystym klonie.

## 1. Kompletność AGENTS.md
| Wymagany element | Sekcja AGENTS.md | Wynik |
|---|---|---|
| Cel aplikacji | §1 | OK |
| Dokumentacja architektury | §2 (tabela) | OK |
| Zadania i status projektu | §2 → PROJECT_STATE.md | OK |
| Uruchomienie środowiska | §3 | OK |
| Uruchomienie testów | §3 | OK |
| Granice modułów | §4 | OK |
| Zmiany zakazane bez zgody | §5 | OK |
| Aktualizacja dokumentacji | §6 | OK |
| Zakończenie zadania i przekazanie | §7 → HANDOFF.md | OK |
Długość: ~60 linii; szczegóły delegowane do `docs/`.

## 2. Zgodność CLAUDE.md i copilot-instructions.md
Oba pliki zawierają wyłącznie wskazanie AGENTS.md i PROJECT_STATE.md, stwierdzają brak reguł
specyficznych dla narzędzia i pierwszeństwo AGENTS.md. Brak konkurujących zasad. **OK.**
Narzędzia nieczytające tych plików: HANDOFF.md §1 pkt 1 nakazuje jawne wskazanie AGENTS.md.

## 3. Aktualność PROJECT_STATE.md
Zawiera wszystkie wymagane pola: faza, ostatni etap, zakres działający i niezrealizowany,
wynik testów z datą, znane błędy, blokery, otwarte decyzje, następne zatwierdzone zadanie,
ostatni zweryfikowany commit. Wartości zgodne z `FAZA0_TESTY.md`. **OK** (commit uzupełniany
w commicie dokumentacyjnym — patrz FAZA0_RAPORT.md §5).

## 4. Kompletność MODULE_MAP.md
Każdy istniejący moduł (16 plików `.py` w `src/`; erratum z korekty 1 — pierwotnie błędnie podano 14) ma ścieżkę, odpowiedzialność, interfejs,
zależności, ograniczenia, testy i dokumentację; wejścia/wyjścia podano tam, gdzie moduł
przetwarza dane. Moduły przyszłe oznaczone PLANOWANE, pakiety puste — ZAREZERWOWANY.
Tabela „chcę zmienić…” wskazuje plik bez przeglądania repozytorium. **OK.**

## 5. Dokumentacja uruchomieniowa
Polecenia z DEVELOPMENT.md §2–§6 wykonane w PowerShell 5.1 w nowym klonie
(`command_logs/07_fresh_clone_reproduction.txt`). Wynik: **ZALICZONE** — klon commita `470eb03`, nowe `.venv`; wszystkie 9 poleceń zakończone kodem 0: pytest 277 zaliczonych / 0 niezaliczonych / 0 pominiętych, Ruff lint i format bez uwag, mypy bez błędów, import `0.0.1 1`, zainstalowane wersje zgodne z `requirements-dev.lock` (`command_logs/07_fresh_clone_reproduction.txt`)

## 6. Ścieżki i odnośniki
Automatyczna kontrola wszystkich plików `.md` (odnośniki względne `[..](..)`, kotwice oraz
ścieżki repozytorium w `` ` ` ``): wynik w `command_logs/10_doc_link_check.txt`.
Adresy dokumentacji giełd: `command_logs/08_exchange_doc_urls.txt` (Binance — niezweryfikowane).

## 7. Test przejęcia projektu bez kontekstu (wymaganie 9.10)
| # | Pytanie | Odpowiedź z repozytorium | Źródło |
|---|---|---|---|
| 1 | Cel projektu | Wykrywanie anomalii na USDT perpetual (Bybit, Binance), aplikacja Windows, bez tradingu | AGENTS.md §1, README.md |
| 2 | Architektura | Modularny monolit `src/`, warstwa `core` bez I/O, zależności do wewnątrz | ARCHITECTURE.md §2–3, DEC-001 |
| 3 | Moduły istniejące i planowane | `core.models`, `core.clock` istnieją; `config`, `events` zarezerwowane; reszta PLANOWANE | MODULE_MAP.md, ARCHITECTURE.md §4–5 |
| 4 | Odtworzenie środowiska | `py -3.14 -m venv .venv` + instalacja z `requirements-dev.lock` | DEVELOPMENT.md §2, AGENTS.md §3 |
| 5 | Uruchomienie testów | `.\.venv\Scripts\python.exe -m pytest` (+ Ruff, mypy) | DEVELOPMENT.md §3–6 |
| 6 | Lokalizacja modeli | `src/market_intelligence/core/models/` | MODULE_MAP.md, DATA_CONTRACTS.md |
| 7 | Ograniczenia | Brak I/O w core, zakazy z AGENTS.md §5, decyzje ACCEPTED | AGENTS.md §4–5, DECISIONS.md |
| 8 | Aktualna faza | FAZA 0 zakończona, oczekuje na audyt | PROJECT_STATE.md |
| 9 | Następne zatwierdzone zadanie | Niezależny audyt FAZY 0; FAZA 1 niezatwierdzona | PROJECT_STATE.md, OQ-07 |
| 10 | Problemy nierozwiązane | OQ-01–OQ-13, ryzyka R-01–R-08 | DECISIONS.md, FAZA0_RYZYKA.md |
Wszystkie 10 punktów: odpowiedź możliwa wyłącznie z repozytorium. **OK.**

Sprzeczności między instrukcjami: nie stwierdzono (AGENTS.md, DEVELOPMENT.md, README.md,
TEST_PLAN.md podają te same polecenia; CLAUDE.md/Copilot nie dodają reguł).
Sekrety, tokeny, hasła: brak w repozytorium. Ścieżki lokalne: usunięte z logów (`<REPO>`,
`<USER_HOME>`, `<TEMP>`).

## 8. Stwierdzone braki
1. Test przejęcia wykonany przez autora dokumentacji, nie przez niezależny podmiot (R-08).
2. Treść dokumentacji Binance nieweryfikowalna z tego środowiska (OQ-12).
3. Zakres FAZY 1 nieokreślony — następca nie może rozpocząć implementacji bez decyzji użytkownika (OQ-07).
4. Kontrola odnośników była skryptem jednorazowym spoza repozytorium; metoda opisana w logu 10,
   ale narzędzie nie jest częścią projektu (do rozważenia w kolejnych fazach).
