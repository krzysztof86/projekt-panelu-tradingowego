# Korekta 2 FAZY 0 — decyzje użytkownika (tekst źródłowy)

| Pole | Wartość |
|---|---|
| Źródło | Odpowiedzi użytkownika (właściciela projektu) na pytania wykonawcy, 2026-10-22 |
| Podstawa | Ponowny niezależny audyt FAZY 0 (korekta 1, HEAD `f0c36e9`) — kopia: [reports/phase0/audyt2/](../../reports/phase0/audyt2/) |
| Upoważnienie do zmian | Zlecenie korekty 1 ([FAZA0_KOREKTA1_ZLECENIE.md](FAZA0_KOREKTA1_ZLECENIE.md)): zmiany kodu, testów i dokumentacji konieczne do usunięcia usterek FAZY 0; bez FAZY 1; bez `git push` bez polecenia. Użytkownik przekazał raport audytu 2 bez dodatkowego polecenia. |
| Wersja dokumentu | 1 — pytania i wybrane odpowiedzi przeniesione dosłownie; jedyna zmiana: wzorzec formatu czasu oznaczony jako kod Markdown, aby Markdown nie renderował go jako odnośnika |

Każde pytanie miało warianty odpowiedzi; poniżej treść pytania, **wybrana odpowiedź** i jej opis
w brzmieniu przedstawionym użytkownikowi.

## 1. Format czasu (K1-01)
Pytanie: „Jak naprawić K1-01 — jaki tekstowy format czasu ma przyjmować kontrakt?”

Wybrano: **„Ścisły RFC 3339 (Recommended)”** — „Jawna lista dozwolonych zapisów zamiast czarnej
listy: `YYYY-MM-DDTHH:MM:SS[.do 6 cyfr](Z|±HH:MM)`. Odrzuca epoch w każdej postaci, ułamki >6 cyfr
(bez cichego obcinania), spację zamiast T, małe z, +0100 i czas bez sekund. To dokładnie format, w
którym kontrakty same się serializują.”

Wariant niewybrany: „Minimalna poprawka” (uzupełnić czarną listę liczb, pozostałe zapisy Pydantic dozwolone).

## 2. Wersja schematu
Pytanie: „Poprawka zaostrza walidację. Co z wersją schematu (procedura DEVELOPMENT §8.1 wymaga
podbicia albo jawnego wyjątku)?”

Wybrano: **„Zostaw 2 + polityka (Recommended)”** — „Zgodnie z rekomendacją audytu zachować wersję 2.
Zapisać zasadę: schemat fazy nieprzyjętej (niewydany, bez zapisanych danych) można korygować bez
podbicia; podbicie obowiązuje po odbiorze fazy lub po pierwszym trwałym zapisie danych.”

Wariant niewybrany: „Podbij do 3”.

## 3. DEC-020 — dziedzina Decimal
Pytanie: „DEC-020 — dziedzina Decimal. Którą wersję przyjąć?”

Wybrano: **„Rozdzielić dziedziny (Recommended)”** — „Ceny, ilości, tick size, obrót i metryki:
≤18 miejsc, |x|<1E+20. value_usdt (iloczyn): ≤36 miejsc, |x|<1E+20 — każda para poprawnych
czynników z sensownym iloczynem ma wtedy reprezentowalną wartość (1E-10×1E-10 przechodzi).
Decyzja przyjęta jako ACCEPTED.”

Warianty niewybrane: „Wspólna dziedzina jak jest”, „Zostaw PROPOSED”.

## 4. Zatwierdzenia
Pytanie: „Które z pozostałych decyzji kontraktowych zatwierdzasz teraz jako ACCEPTED?
(niezaznaczone pozostaną PROPOSED)”

Zaznaczono **wszystkie cztery** warianty:
- „DEC-010 dokładna równość” — „value_usdt == price * quantity dokładnie, bez tolerancji”;
- „DEC-021 tworzenie rekordów” — „replace/walidujące model_copy, rewalidacja zagnieżdżonych, zakaz model_construct w src”;
- „DEC-022 schemat 2, 0.0.2” — „Wersja schematu 2 i pakietu 0.0.2”;
- „DEC-004 i DEC-005” — „Czas: tylko datetime/str wg wybranego formatu, odrzucanie epoch i danych
  binarnych; niemutowalność, extra=forbid, ścisły int schema_version.”

## Skutki w repozytorium
Statusy i treść decyzji: [../DECISIONS.md](../DECISIONS.md) (DEC-004, DEC-005, DEC-010, DEC-020,
DEC-021, DEC-022 — ACCEPTED; nowa DEC-026 — polityka wersji schematu, ACCEPTED). Pozostałe
decyzje PROPOSED nie były przedmiotem pytań i pozostają PROPOSED.
