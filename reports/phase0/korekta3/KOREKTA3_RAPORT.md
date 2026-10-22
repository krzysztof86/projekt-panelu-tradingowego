# FAZA 0 — korekta 3: raport

**Status: GOTOWA DO WERYFIKACJI AUDYTORA.** FAZA 0 **nie** została przyjęta; o odbiorze decyduje
użytkownik po weryfikacji. FAZA 1 nie została rozpoczęta; jej zakres nie jest zatwierdzony (OQ-07).
Data: 2026-10-22.

| Pole | Wartość |
|---|---|
| Podstawa | Audyt 3: [../audyt3/AUDYT_FAZY0_KOREKTA2.md](../audyt3/AUDYT_FAZY0_KOREKTA2.md) (HEAD `6c633aa`) — „Rekomenduję odbiór po jednej dodatkowej poprawce obsługi błędu granicznego czasu” |
| Upoważnienie | Zlecenie korekty 1 (zmiany konieczne do usunięcia usterek FAZY 0; bez FAZY 1; bez push bez polecenia) — [docs/requirements/FAZA0_KOREKTA1_ZLECENIE.md](../../../docs/requirements/FAZA0_KOREKTA1_ZLECENIE.md). Użytkownik przekazał raport audytu 3 bez dodatkowego polecenia. |
| Decyzje użytkownika | nie były potrzebne — poprawka nie zmienia zakresu przyjmowanych danych ani żadnej decyzji |
| Gałąź | `task/faza0-korekta3`, utworzona z `task/faza0-korekta2` = `6c633aa` (HEAD audytowany) |

## 1. Odtworzenie K2-A01
Na `6c633aa` (`command_logs/08_probes_before_after.txt`, część BEFORE) — 8/8 prób kończy się surowym
`OverflowError: date value out of range`:

| Wejście | Python | JSON |
|---|---|---|
| `listed_at="0001-01-01T00:00:00+01:00"` | `OverflowError` | `OverflowError` |
| `listed_at="9999-12-31T23:59:59-01:00"` | `OverflowError` | `OverflowError` |
| `listed_at=datetime(1,1,1,+01:00)` / `datetime(9999,12,31,23,59,59,-01:00)` | `OverflowError` | — |
| `ensure_utc(datetime(1,1,1,+01:00))`, `Candle.contains(…)` | `OverflowError` | — |

**Zgadzam się z ustaleniem i z klasyfikacją audytora:** luka istniała w `ensure_utc` od FAZY 0
(funkcja nie była zmieniana w korekcie 2); nie jest regresją korekty 2.

### 1.1 Skan innych wyjątków niż `ValidationError`
W tej samej próbie sprawdzono dane skrajne innych pól: wykładniki ±1E+999999999999999999999,
liczby 4000–5000 cyfr (tekst i `int`), `sNaN`, `-0`, strefę `+25 h`, liczbę JSON z 5000 cyfr jako
`schema_version`, okno zdarzenia od roku 1 do 9999, świecę kończącą się poza zakresem. **Poza
K2-A01 nie znaleziono wycieku** — wszystkie kończą się `ValidationError` lub poprawnym przyjęciem.
Poza zakresem: obiekty `tzinfo`, których własny kod zgłasza dowolny wyjątek (kod wywołującego, nie dane).

## 2. Poprawka
| Element | Rozwiązanie | Plik | Testy |
|---|---|---|---|
| K2-A01 | `ensure_utc` przechwytuje `OverflowError` z `astimezone(UTC)` i zgłasza `ValueError` („… has no representable UTC equivalent (outside the datetime range of years 1 to 9999)”), z `OverflowError` jako przyczyną; Pydantic zamienia go na `ValidationError`. Opis wyjątków w docstringu zaktualizowany. Bez nowego ograniczenia lat. | `src/market_intelligence/core/clock/utc.py` | `tests/regression/test_audit3_phase0.py` |

Dokumentacja: DATA_CONTRACTS §1.3 (zachowanie dla dat bez odpowiednika UTC), §1.1 (przechowanie
`value_usdt` do 56 cyfr — uwaga 3 audytu, OQ-16), MODULE_MAP, TEST_PLAN §9, DECISIONS (odnośniki,
OQ-16), CHANGELOG. **Żadna decyzja nie została zmieniona**; schemat 2 i pakiet 0.0.2 bez zmian —
poprawka nie zmienia zbioru przyjmowanych danych (te wejścia nigdy nie dawały poprawnego rekordu),
zmienia tylko rodzaj zgłaszanego błędu.

## 3. Warunki odbioru (audyt 3)
| Warunek | Stan |
|---|---|
| 1. Usunąć K2-A01, regresje, pełne kontrole na nowym commicie | wykonane — [KOREKTA3_TESTY.md](KOREKTA3_TESTY.md), §5 |
| 2. OQ-14, OQ-15 otwarte przed zależnymi modułami | bez zmian — otwarte; audyt: nie są blokerami FAZY 0 |
| 3. `value_usdt` do 56 cyfr; storage nie zakłada `DECIMAL(38,18)` | zapisane w DATA_CONTRACTS §1.1 i jako OQ-16 |
| 4. Pozostałe PROPOSED przed modułami, które ich potrzebują; FAZA 1 osobno | bez zmian — decyzja użytkownika |

## 4. Ograniczenia i ryzyka
- Weryfikację wykonał wykonawca korekty; wymagana jest weryfikacja audytora.
- Test mutacyjny obejmuje 17 wybranych cofnięć, nie wszystkie możliwe zmiany.
- OQ-14, OQ-15, OQ-16 pozostają otwarte przed modułami konektorów, replay i storage.

## 5. Git
- Zweryfikowany commit (kod, testy, dokumentacja korekty 3): **`f74cff1f5137d656619726fdcba7d9866d2b1ad9`** (`f74cff1`) na gałęzi
  `task/faza0-korekta3`, utworzonej z `task/faza0-korekta2` = `6c633aa` (HEAD audytowany w audycie 3).
  Na nim wykonano odtworzenie w czystym klonie.
- Kolejne commity zawierają wyłącznie dokumentację: wyniki odtworzenia, identyfikator commita i stan push w
  `docs/PROJECT_STATE.md` i `reports/phase0/korekta3/` (bez zmian kodu, testów, konfiguracji);
  sprawdzenie: `git diff --stat f74cff1 HEAD`.
- Porównanie z wersją audytowaną: `git diff --stat 6c633aa f74cff1`.
- `main` = `origin/main` = `2fcc5f7`. Gałąź korekty 3 wypchnięta na
  `origin/task/faza0-korekta3` 2026-10-22 na polecenie użytkownika; **bez scalania do `main`**
  — scalenie wymaga polecenia użytkownika.

## 6. Materiały do weryfikacji
| Materiał | Ścieżka |
|---|---|
| Raport, testy, zmiany | `reports/phase0/korekta3/KOREKTA3_RAPORT.md`, `KOREKTA3_TESTY.md`, `KOREKTA3_ZMIANY.md` |
| Logi | `reports/phase0/korekta3/command_logs/` |
| Kopia audytu 3 | `reports/phase0/audyt3/` |
| Stan projektu | `docs/PROJECT_STATE.md` |
