# Niezależna weryfikacja FAZY 0 — KOREKTA 2

Data: 2026-10-22.
Repozytorium: krzysztof86/projekt-panelu-tradingowego.
Gałąź lokalna: task/faza0-korekta2.
Audytowany HEAD: 6c633aa0f4b6a0cb227ff45bbbc7fa7d01e33b8f.
Commit implementacji wskazany w raporcie: 73263fac89e0d721414522d0ca6afa4ed08dfdb3.

## Werdykt
**KOREKTA 2 zamyka K1-01 i realizuje opisane rozdzielenie dziedzin Decimal. Rekomenduję odbiór po jednej dodatkowej poprawce obsługi błędu granicznego czasu.**

Nie wykryłem regresji pierwotnych poprawek w pełnym zestawie testów. Nowe ustalenie K2-A01 dotyczy istniejącej wcześniej funkcji normalizacji UTC; nie jest regresją KOREKTY 2. Nie należy przedstawiać go jako nieudanego usunięcia K1-01.

## Materiał i metoda
Odczytano lokalne KOREKTA2_RAPORT.md, KOREKTA2_TESTY.md, KOREKTA2_ZMIANY.md, AGENTS.md, zapis decyzji użytkownika, zmiany kodu i nowe regresje.
Utworzono snapshot zatwierdzonego HEAD przez git archive i uruchomiono kontrole na tej kopii we własnym katalogu audytu. Nie zmieniano źródłowego repozytorium ani jego środowiska.
Porównanie 73263fa…HEAD obejmuje tylko PROJECT_STATE, raport korekty, raport testów i log czystego odtworzenia — zgodnie z deklaracją autora.
Nie potwierdzono czystości oryginalnego drzewa roboczego: polecenia status nie zadziałały poprawnie w obecnym środowisku. Ocena dotyczy zatwierdzonego HEAD, a nie ewentualnych niezatwierdzonych plików.
Nie weryfikowano stanu zdalnych gałęzi ani faktu push.

## Własne wyniki
| Kontrola | Wynik |
|---|---|
| pytest | 720 passed, 1,67 s |
| Ruff check | All checks passed |
| Ruff format --check | 64 files already formatted |
| mypy | Success, 31 source files |
| Izolowany import -I | 0.0.2 2 |

Python 3.14.5 i Pydantic 2.14.1; zależności wykorzystano z lokalnego środowiska audytu. Pakiet ze snapshotu zainstalowano editable bez izolacji budowania. Nie jest to niezależne odtworzenie instalacji z PyPI od zera. Nie powtarzano 16 mutacji autora; 16/16 pozostaje wynikiem jego logu.

## Zamknięcie poprzednich ustaleń
- K1-01: ".5", "+.5", "-.5" są odrzucane przez ValidationError na ścieżkach Python i JSON. Potwierdzono własną próbą.
- K2-1–K2-3: nowy zestaw regresji pokrywa warianty liczbowe, luźne formaty i ułamki ponad 6 cyfr. Własna próba potwierdza odrzucenie nanosekund zamiast cichego obcinania.
- Parser tekstu korzysta z listy dozwolonych zapisów i datetime.fromisoformat. Opcjonalność offsetu w samym regexie nie jest obejściem: tekst bez strefy odrzuca ensure_utc.
- DEC-020: czynniki zachowują 18 miejsc, value_usdt ma 36; limit wartości bezwzględnej <1E+20 pozostaje wspólny. Iloczyn 1E-10 × 1E-10 ma teraz poprawną reprezentację 1E-20. Granice 36/37 miejsc i wyrocznia Fraction są testowane.
- DEC-010: dokładna równość i niezależny kontekst mnożenia zachowane. Nie znaleziono błędu tej arytmetyki.
- DEC-021: mechanizm replace/model_copy oraz rewalidacja instancji nie zostały zmienione; stare regresje przechodzą.
- DEC-022/026: schemat 2 i pakiet 0.0.2 są spójne z opisaną polityką niewydanej fazy.
- Dokumentacja usuwa wcześniejsze nadmierne twierdzenia o dziedzinie i gwarancjach MarketEvent. Zmiana testu odnośników ma uzasadnienie w semantyce kodu Markdown.

Rejestr i dokument FAZA0_KOREKTA2_DECYZJE.md zapisują DEC-004/005/010/020/021/022/026 jako ACCEPTED, z datą i opisem wyborów. To spójny zapis repozytorium; niniejszy audyt nie stanowi nowego zatwierdzenia tych decyzji ani niezależnego dowodu przebiegu odpowiedzi w innym czacie. Same wcześniejsze rekomendacje audytora nie były zgodą użytkownika.

## K2-A01 — wyciek OverflowError przy normalizacji dat granicznych
Priorytet: P2. Miejsce: src/market_intelligence/core/clock/utc.py:22, return value.astimezone(UTC).

Przykłady na poprawnym payloadzie Instrument, ze zmienionym listed_at:
| Wejście | Python | JSON |
|---|---|---|
| 0001-01-01T00:00:00+01:00 | OverflowError: date value out of range | ten sam wyjątek |
| 9999-12-31T23:59:59-01:00 | OverflowError: date value out of range | ten sam wyjątek |

Potwierdzono także oba przypadki podane jako świadome strefy obiekty datetime. Łącznie 6/6 prób ujawniło surowy OverflowError.
Teksty mieszczą się w przyjętym profilu; lokalna data jest reprezentowalna, lecz po przeliczeniu na UTC wypada poza zakres datetime. Pydantic nie zamienia OverflowError walidatora w ValidationError.
Znaczenie: konsument obsługujący odrzucenie danych przez ValidationError może dostać nieobsłużony wyjątek. Przykłady są skrajne i nierealistyczne rynkowo, ale obecny kontrakt nie ogranicza lat do zakresu rynkowego.

Rekomendowana minimalna poprawka: przechwycić OverflowError przy astimezone i podnieść ValueError z jasnym komunikatem o niereprezentowalnym czasie UTC. Pydantic zwróci wtedy ValidationError. Nie trzeba wprowadzać nowego ograniczenia biznesowego lat.
Dodać regresje obu krańców na ścieżkach Python/JSON oraz datetime, a także poprawnych dat granicznych już w UTC. Sprawdzić bezpośrednie zachowanie ensure_utc i zaktualizować jego opis wyjątków.
Funkcja nie została zmieniona w KOREKCIE 2, dlatego klasyfikuję to jako nowo wykrytą starszą lukę obsługi błędów.

## Pozostałe ryzyka i warunki odbioru
1. Usunąć K2-A01, dodać regresje i uruchomić pełne kontrole na nowym wskazanym commicie.
2. OQ-14 (zgodność dziedzin z formatami giełd) i OQ-15 (wydajność rewalidacji) pozostają otwarte przed zależnymi modułami. Nie są same w sobie nowymi blokerami czystych kontraktów FAZY 0.
3. Dziedzina value_usdt ma potencjalnie 56 cyfr precyzji (20 przed przecinkiem + 36 po nim). Przyszły storage musi przechować ją bez utraty dokładności; nie zakładać DECIMAL(38,18).
4. Pozostałe PROPOSED rozstrzygać przed modułami, które ich potrzebują. Nie rozpoczynać FAZY 1 bez osobnego zatwierdzenia zakresu.

Nie wykonano zmian kodu projektu, commitów, push ani merge.

