# FAZA 0 — korekta 1: raport

**Status: GOTOWA DO PONOWNEGO NIEZALEŻNEGO AUDYTU.** FAZA 0 **nie** została przyjęta; o przyjęciu
decyduje audytor i użytkownik. FAZA 1 nie została rozpoczęta.
Data: 2026-10-22. Zlecenie: [docs/requirements/FAZA0_KOREKTA1_ZLECENIE.md](../../../docs/requirements/FAZA0_KOREKTA1_ZLECENIE.md).
Audyt: [../audyt1/AUDYT_FAZY0.md](../audyt1/AUDYT_FAZY0.md) (kopia z sumami SHA-256: [../audyt1/README.md](../audyt1/README.md)).

## 1. Punkt wyjścia
- `HEAD` przed korektą = audytowany commit `2fcc5f76fc171a6f7b10b5e5333ebd11df16c226`; drzewo
  czyste; `origin/main` identyczny; różnica względem wersji audytowanej: 0 linii.
- Korekta na gałęzi `task/faza0-korekta1` (DEVELOPMENT.md §7). `main` i `origin` bez zmian; brak push.
- Środowisko: Windows 11 x64, Python 3.14.5, pip 26.2.2, zależności zgodne z `requirements-dev.lock`
  (`command_logs/01_environment.txt`).

## 2. Odtworzenie ustaleń audytu
Skrypt prób audytora uruchomiony bez zmian na `2fcc5f7` (`command_logs/08_audit_probes_before_after.txt`).

| Ustalenie | Odtworzone | Stanowisko | Dowód (wersja audytowana) |
|---|---|---|---|
| A-01 | tak | zgadzam się | 101 miejsc: błędna wartość przyjęta, poprawna odrzucona; `ROUND_UP` zmienia wynik; pułapka `Inexact` → wyciek `decimal.Inexact`; `1e999999` → wyciek `decimal.Overflow` |
| A-02 | tak | zgadzam się | `True` i `1.0` przyjęte jako `1` (Python i JSON) |
| A-03 | tak | zgadzam się | `listed_at=b"1767225600"` → `2026-01-01T00:00:00+00:00` |
| A-04 | tak | zgadzam się (opis, nie błąd kodu) | te same ID, `equal=False`, zbiór 2 elementy |
| A-05 | tak (przegląd testu) | zgadzam się | test sprawdzał tylko `sys.modules` po imporcie `core.models` |
| A-06 | tak | zgadzam się | `"first\rsecond"` przyjęte |
| A-07 | tak | zgadzam się | `model_copy(update={"tick_size": -1})` zagnieżdżony w `MarketTick` przyjęty |

**Żadnego ustalenia nie kwestionuję.** Drobne uwagi audytu też potwierdzam: 16 (nie 14) plików
`.py` w `src/`; placeholder adresu w README; `requires-python >=3.14` szersze niż przetestowane.

### 2.1 Dodatkowe luki znalezione przy odtwarzaniu (`command_logs/10_extra_probes_before_after.txt`)
| ID | Luka (wersja audytowana) | Związek |
|---|---|---|
| E-1 | `listed_at=b"2026-01-01T00:00:00Z"` (ISO jako `bytes`) przyjęte | rozszerzenie A-03 |
| E-2 | `schema_version=Decimal(1)` przyjęte | rozszerzenie A-02 |
| E-3 | `bytes` przyjmowane w polach tekstowych (`symbol=b"BTCUSDT"`) i enumach (`exchange=b"BYBIT"`) | ta sama klasa co A-03 |
| E-4 | `ReasonText` przyjmował U+0085, U+2028, U+2029, VT, FF, U+001E | rozszerzenie A-06 |
| — | `model_construct` z błędnymi danymi zagnieżdżony w innym kontrakcie przyjmowany | rozszerzenie A-07 |

## 3. Poprawki
| Ustalenie | Rozwiązanie | Pliki | Testy regresji | Decyzja |
|---|---|---|---|---|
| A-01 | (1) iloczyn w prywatnym kontekście `decimal`: precyzja = suma cyfr czynników (dokładność matematycznie zagwarantowana), pełny zakres wykładników, wszystkie pułapki; kontekst wywołującego nieużywany i niezmieniany; błąd → `ValidationError`. (2) jawna dziedzina Decimal: ≤ 18 miejsc po przecinku, \|x\| < 1E+20 | `core/models/trade.py`, `core/models/types.py` | `TestA01FinancialDomain`, `TestA01ExactProduct` | DEC-010, DEC-020 |
| A-02 | znacznik wersji: walidator wymaga `type(v) is int` przed `Literal[2]` | `core/models/base.py` | `TestA02SchemaVersion` (5 modeli × Python/JSON × 9 wartości + `Decimal`) | DEC-005, DEC-022 |
| A-03 | pola czasu: tylko `datetime` lub `str`; dodatkowo odrzucanie danych binarnych w każdym polu (walidator modelu bazowego) | `core/models/types.py`, `core/models/base.py` | `TestA03TimestampInputTypes`, `TestE3BinaryInputRejected` | DEC-004 |
| A-04 | bez zmiany `__eq__` (zgodnie z rekomendacją); opis: tożsamość = `instrument_id`, równość = snapshot | DATA_CONTRACTS §3, DEC-006, ARCHITECTURE §6–7 | `TestA04InstrumentIdentity` | DEC-006 |
| A-05 | test opisany jako ograniczony i rozszerzony na wszystkie pakiety `core`; nowe: statyczna granica importów, zakaz wywołań, strażnik I/O w czasie wykonania; definicja „aplikacyjnego I/O” | `tests/contracts/test_package_import.py`, `tests/contracts/test_core_boundaries.py`, ARCHITECTURE §3 | j.w. | DEC-023 |
| A-06 | `ReasonText`: odrzucanie wszystkich separatorów z `str.splitlines()` | `core/models/types.py` | `TestA06ReasonSingleLine` | DEC-009 |
| A-07 | `ContractModel.replace(**zmiany)`; walidujące `model_copy(update=...)` (obejmuje `copy.replace`); `revalidate_instances="always"`; zakaz `model_construct` w `src/` (test AST); opis ścieżek zaufanych/niezaufanych | `core/models/base.py`, DATA_CONTRACTS §1.2 | `TestA07SafeModification`, `test_model_construct_not_used_in_src` | DEC-021 |

Uzasadnienie granic dziedziny (zlecenie pkt 3 — „nie ograniczaj po cichu”): granice są jawne,
udokumentowane (DATA_CONTRACTS §1.1, DEC-020), stałe są w kodzie (`MAX_DECIMAL_PLACES`,
`MAX_INTEGER_DIGITS`), a naruszenie daje komunikat `ValidationError` — nic nie jest zaokrąglane ani
obcinane. 18 miejsc = najmniejsza jednostka typowych tokenów (1 wei); 1E+20 USDT przekracza każdy
obrót; 38 cyfr = maksymalna precyzja DECIMAL w popularnych bazach SQL. Dokładność iloczynu **nie
zależy** od tych granic (precyzja kontekstu wynika z liczby cyfr czynników). Granice wymagają
rozstrzygnięcia (DEC-020) i weryfikacji na danych giełdowych (OQ-14).

## 4. Dokumentacja (audyt §5)
| Uwaga audytu | Stan |
|---|---|
| Dołączyć zatwierdzoną specyfikację FAZY 0 | `docs/requirements/FAZA0_SPECYFIKACJA.md` (dosłownie) + zlecenie korekty (DEC-024) |
| PROJECT_STATE „Znane błędy: brak” | zaktualizowano: stan po korekcie, ustalenia zamknięte do potwierdzenia w ponownym audycie |
| README — placeholder adresu | wstawiono adres repozytorium GitHub |
| 14 vs 16 plików `.py` | erratum w `FAZA0_HANDOFF_AUDIT.md` |
| Rozdzielić gwarancje modelu od przyszłego systemu | ARCHITECTURE §7, DATA_CONTRACTS §1.2 i §8 |
| Narzędzie kontroli odnośników | `tests/contracts/test_documentation.py` (DEC-025) |
| `requires-python` | `>=3.14,<3.15` (DEC-002) |
| Zakres odtwarzalności DEC-016 | doprecyzowano (bez hashów, bez pełnego środowiska budowania) |

## 5. Decyzje wymagające rozstrzygnięcia użytkownika
Pełna, uszeregowana lista z rekomendacjami audytu: [docs/DECISIONS.md](../../../docs/DECISIONS.md),
sekcja „Decyzje wymagające rozstrzygnięcia użytkownika”. Żadnej decyzji nie oznaczono jako ACCEPTED.
Najważniejsze, bo wpływają na kontrakty:
1. **DEC-020** — granice dziedziny Decimal (lub alternatywy: brak granic, inne granice, osobna dziedzina metryk).
2. **DEC-010** — ścisła równość `value_usdt == price * quantity`.
3. **DEC-022** — podniesienie schematu do 2 (alternatywa: zachować 1 jako niewydany).
4. **DEC-021** — polityka tworzenia rekordów i koszt rewalidacji (OQ-15).
5. **DEC-005 / DEC-004** — ścisły znacznik wersji, typy wejścia czasu, odrzucanie danych binarnych.
Ponadto: zakres FAZY 1 (OQ-07) i zmienna systemowa `PYTHONOPTIMIZE` (OQ-13).

## 6. Warunki ponownego odbioru (audyt §8)
| Warunek | Stan po korekcie |
|---|---|
| 1. A-01 naprawione, precyzja i dziedzina, testy kontekstu | wykonane; zatwierdzenie dziedziny — DEC-020 (użytkownik) |
| 2. A-02, A-03 zgodne z kontraktem, testy obu ścieżek | wykonane (JSON nie przenosi `bytes`, więc A-03 testowane na ścieżce Python) |
| 3. A-04, A-05, A-07 doprecyzowane; A-06 poprawione; nieaktualne stwierdzenia | wykonane |
| 4. Zapisane wymagania i decyzje; procedura wersjonowania | wymagania w `docs/requirements/`; schemat 2 wg DEVELOPMENT §8.1; rozstrzygnięcia — użytkownik |
| 5. Odtworzenie środowiska, pełne kontrole, liczba testów wzrosła | wykonane — [KOREKTA1_TESTY.md](KOREKTA1_TESTY.md) |
| 6. Zakres FAZY 1 | poza korektą — OQ-07, decyzja użytkownika |

## 7. Ograniczenia i ryzyka korekty
- Dziedzina DEC-020 może odrzucić prawdziwe dane, jeśli iloczyn ceny i ilości wymaga > 18 miejsc
  (niepotwierdzone na danych giełdowych, OQ-14).
- `revalidate_instances="always"` zwiększa koszt tworzenia zagnieżdżonych rekordów (niezmierzony, OQ-15).
- Kontrole braku I/O są ograniczone (DEC-023) — nie dowodzą braku każdej operacji I/O.
- Ograniczenie typów czasu (A-03) częściowo pokrywa się z odrzucaniem danych binarnych: dla `bytes`
  zadziała pierwsza z warstw (walidator modelu); test mutacyjny potwierdza, że obie warstwy są testowane.
- Test mutacyjny obejmuje 11 wybranych cofnięć poprawek, nie wszystkie możliwe zmiany.
- Weryfikację wykonał ten sam wykonawca, który wprowadził poprawki; wymagany jest ponowny audyt.

## 8. Git
OCZEKUJE — uzupełniane w kolejnym commicie dokumentacyjnym, po odtworzeniu w czystym klonie (odtworzenie wymaga commita do sklonowania).
