# FAZA 0 — korekta 2: raport

**Status: GOTOWA DO PONOWNEGO NIEZALEŻNEGO AUDYTU.** FAZA 0 **nie** została przyjęta; o odbiorze
decyduje audytor i użytkownik. FAZA 1 nie została rozpoczęta; jej zakres nie jest zatwierdzony (OQ-07).
Data: 2026-10-22.

| Pole | Wartość |
|---|---|
| Podstawa | Audyt 2: [../audyt2/AUDYT_FAZY0_KOREKTA1.md](../audyt2/AUDYT_FAZY0_KOREKTA1.md) (HEAD `f0c36e9`) |
| Decyzje użytkownika | [docs/requirements/FAZA0_KOREKTA2_DECYZJE.md](../../../docs/requirements/FAZA0_KOREKTA2_DECYZJE.md) |
| Upoważnienie | Zlecenie korekty 1 (zmiany konieczne do usunięcia usterek FAZY 0; bez FAZY 1; bez push bez polecenia) — [docs/requirements/FAZA0_KOREKTA1_ZLECENIE.md](../../../docs/requirements/FAZA0_KOREKTA1_ZLECENIE.md) |
| Gałąź | `task/faza0-korekta2`, utworzona z `task/faza0-korekta1` = `f0c36e9` (HEAD audytowany) |

## 1. Odtworzenie ustalenia K1-01
Na `f0c36e9` (`command_logs/08_probes_before_after.txt`, część BEFORE):

| Wejście `listed_at` | Python | JSON |
|---|---|---|
| `".5"` | przyjęte: 1970-01-01T00:00:00.500000+00:00 | to samo |
| `"+.5"` | przyjęte: 1970-01-01T00:00:00.500000+00:00 | to samo |
| `"-.5"` | przyjęte: 1969-12-31T23:59:59.500000+00:00 | to samo |

**Zgadzam się z ustaleniem.** Przyczyna: czarna lista `_NUMERIC_STRING` wymagała cyfry przed
kropką, a dalszy parser Pydantic interpretował tekst jako epoch.

### 1.1 Pokrewne obserwacje z korekty 2
| ID | Obserwacja na `f0c36e9` | Rozwiązanie |
|---|---|---|
| K2-1 | `".5e3"`, `".5E+3"`, `"-.5e-1"` przyjmowane jako epoch | lista dozwolonych zapisów (K1-01) |
| K2-2 | `"2026-01-01T00:00:00.123456789Z"` przyjmowane z **cichym obcięciem** do mikrosekund | ułamek 1–6 cyfr; więcej → odrzucenie |
| K2-3 | przyjmowane zapisy luźniejsze niż deklarowany kontrakt: spacja zamiast `T`, małe `z`, `+0100`, czas bez sekund | profil RFC 3339 (decyzja użytkownika) |

## 2. Poprawki
| Element | Rozwiązanie | Pliki | Testy | Decyzja |
|---|---|---|---|---|
| K1-01, K2-1–K2-3 | Tekst czasu sprawdzany **listą dozwolonych zapisów** `_RFC3339` (`YYYY-MM-DDTHH:MM:SS[.ffffff](Z\|+HH:MM\|-HH:MM)`, cyfry ASCII, godziny 00–23, sekundy 00–59) i dopiero wtedy parsowany `datetime.fromisoformat`; żaden inny parser nie interpretuje tekstu. Czarna lista liczb poprawiona (alternatywa `\.\d+`) i zachowana dla czytelnego komunikatu | `core/models/types.py` | `TestK101NumericText`, `TestRfc3339Profile` | DEC-004 (ACCEPTED) |
| DEC-020 (audyt 2 §5) | Rozdzielone dziedziny: czynniki ≤ 18 miejsc; `Trade.value_usdt` ≤ 36 miejsc (`PositiveProductDecimal`, `MAX_PRODUCT_DECIMAL_PLACES`); obie \|x\| < 1E+20 | `core/models/types.py`, `core/models/trade.py` | `TestDec020ProductDomain` | DEC-020 (ACCEPTED) |
| Audyt 2 §8 (opis w kodzie) | Docstring `MarketEvent`: niezmiennik czasu dotyczy tylko kolejności deklarowanych czasów, nie dowodzi braku danych z przyszłości | `core/models/market_event.py` | — | DEC-011 |
| Audyt 2 §5 (opis dziedziny) | Usunięto twierdzenie o pokryciu wszystkich kwot; `DECIMAL(38, 18)` opisany jako zakres liczbowy, nie semantyka; reprezentowalność rozstrzyga dokładny iloczyn; odwołanie do OQ-14 | `docs/DATA_CONTRACTS.md` §1.1 | — | DEC-020 |
| Audyt 2 §8 (wersja schematu) | Schemat 2 i pakiet 0.0.2 zachowane; zasada dla faz nieprzyjętych zapisana i dodana do procedury | `docs/DECISIONS.md` (DEC-026), `docs/DEVELOPMENT.md` §8.1 | — | DEC-026 (ACCEPTED) |

Zmiana dotychczasowego testu: `test_audit1_phase0.py::TestA01ExactProduct::test_product_needing_more_than_18_places_has_no_valid_value`
→ `test_small_product_rounded_to_18_places_rejected`. Asercje bez zmian (wartości zaokrąglone do 18
miejsc nadal odrzucane); nazwa i komentarz twierdziły, że iloczyn `1E-20` nie ma poprawnej wartości,
co po decyzji DEC-020 jest nieprawdą — przyjęcie dokładnej wartości testuje
`test_audit_example_product_is_representable`.

## 3. Warunki zamknięcia (audyt 2 §9)
| Warunek | Stan |
|---|---|
| 1. Naprawić K1-01, testy Python/JSON, pełne kontrole | wykonane — [KOREKTA2_TESTY.md](KOREKTA2_TESTY.md) |
| 2. Rozstrzygnąć DEC-020 i DEC-010 | **rozstrzygnięte przez użytkownika**: DEC-020 (rozdzielone dziedziny) i DEC-010 — ACCEPTED |
| 3. Rozstrzygnąć DEC-021, DEC-022, DEC-004/005 | **rozstrzygnięte przez użytkownika** — ACCEPTED; nowa DEC-026 — ACCEPTED |
| 4. Skorygować opis dziedziny i drobne niespójności | wykonane (DATA_CONTRACTS §1.1, docstring `MarketEvent`, OQ-14) |
| 5. Nowy commit i wyniki; decyzja o odbiorze; zakres FAZY 1 osobno | commit i wyniki: §5; odbiór i FAZA 1 — decyzja użytkownika/audytora |

Decyzje nadal **PROPOSED** (nie były przedmiotem pytań; audyt 2 nie wskazał ich jako blokujących):
DEC-002, 003, 006, 007, 008, 009, 011, 012, 013, 015, 016, 018, 019, 023, 024, 025 — lista z
rekomendacjami: [docs/DECISIONS.md](../../../docs/DECISIONS.md).

## 4. Ograniczenia i ryzyka
- Profil RFC 3339 jest węższy niż RFC 3339 i ISO 8601 (bez spacji, `t`/`z`, sekundy przestępnej,
  ułamka > 6 cyfr). Teksty z innych źródeł wymagają jawnej normalizacji w konektorach.
- Dziedziny DEC-020 nie są zweryfikowane na danych giełdowych (OQ-14).
- Koszt `revalidate_instances="always"` niezmierzony (OQ-15).
- Test mutacyjny obejmuje 16 wybranych cofnięć, nie wszystkie możliwe zmiany.
- Weryfikację wykonał wykonawca korekty; wymagany jest ponowny niezależny audyt.

## 5. Git
OCZEKUJE — uzupełniane w kolejnym commicie dokumentacyjnym, po odtworzeniu w czystym klonie (odtworzenie wymaga commita do sklonowania).

## 6. Materiały do ponownego audytu
| Materiał | Ścieżka |
|---|---|
| Raport, testy, zmiany | `reports/phase0/korekta2/KOREKTA2_RAPORT.md`, `KOREKTA2_TESTY.md`, `KOREKTA2_ZMIANY.md` |
| Logi | `reports/phase0/korekta2/command_logs/` |
| Decyzje użytkownika | `docs/requirements/FAZA0_KOREKTA2_DECYZJE.md`, `docs/DECISIONS.md` |
| Kopia audytu 2 | `reports/phase0/audyt2/` |
| Stan projektu | `docs/PROJECT_STATE.md` |
