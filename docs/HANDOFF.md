# HANDOFF — procedura przekazania pracy

Ten dokument opisuje **sposób** przekazania pracy. Nie zawiera opisu stanu projektu —
jedynym aktualnym opisem stanu jest [PROJECT_STATE.md](PROJECT_STATE.md).

## 1. Przejęcie projektu (start pracy)
1. Przeczytaj [AGENTS.md](../AGENTS.md), potem [PROJECT_STATE.md](PROJECT_STATE.md).
   Narzędzia, które nie wczytują AGENTS.md automatycznie, należy wprost poprosić o jego przeczytanie.
2. Przeczytaj raport przekazania wskazany w PROJECT_STATE.md (pole „Raporty ostatniej fazy”).
3. Sprawdź stan Git: `git status`, `git log --oneline -5`. Porównaj z „Ostatni zweryfikowany commit”.
4. Odtwórz środowisko i uruchom pełną kontrolę ([DEVELOPMENT.md](DEVELOPMENT.md) §2 i §6).
   Wynik musi zgadzać się z PROJECT_STATE.md. Rozbieżność zgłoś przed rozpoczęciem zmian.
5. Pracuj wyłącznie nad „Następnym zatwierdzonym zadaniem” z PROJECT_STATE.md.

## 2. Przekazanie (koniec zadania lub fazy) — checklista
Przed zgłoszeniem zakończenia wykonawca zapisuje w raporcie `reports/<faza>/` (dla faz:
`reports/phase<N>/FAZA<N>_*.md`, wzór: `reports/phase0/`; korekty po audycie:
`reports/phase<N>/korekta<M>/`, kopie materiałów audytu: `reports/phase<N>/audyt<M>/`):

- [ ] **Co wykonano** — lista zadań z odniesieniem do wymagań.
- [ ] **Zmienione pliki** — ścieżki i uzasadnienie (`git diff --stat <poprzedni>..HEAD`).
- [ ] **Decyzje** — nowe/zmienione wpisy w [DECISIONS.md](DECISIONS.md) ze statusem.
- [ ] **Testy** — dokładne polecenia i liczby: zaliczone / niezaliczone / pominięte / nieuruchomione,
      wraz z logami w `reports/<faza>/command_logs/` (bez ścieżek lokalnych i sekretów).
- [ ] **Problemy nierozwiązane** — znane błędy, ryzyka, blokery.
- [ ] **Stan Git** — gałąź, ostatni commit, czy drzewo robocze jest czyste, czy wykonano push (domyślnie: nie).
- [ ] **Następne zatwierdzone zadanie** — tylko jeśli zatwierdził je użytkownik; inaczej „brak — oczekuje na decyzję”.
- [ ] **Czego nie zakładać ani nie modyfikować** — ograniczenia dla następcy.

Następnie:
1. Zaktualizuj [PROJECT_STATE.md](PROJECT_STATE.md) (wszystkie pola) i, jeśli dotyczy,
   MODULE_MAP, DATA_CONTRACTS, ARCHITECTURE, DECISIONS, CHANGELOG.
2. Wykonaj kontrolę dokumentacji bez kontekstu (sekcja 3).
3. Zacommituj zmiany lokalnie; nie wykonuj `git push` bez zgody użytkownika.

Projekt nie może zostać przekazany z nieaktualnym PROJECT_STATE.md.

## 3. Kontrola przejęcia bez kontekstu
Na podstawie wyłącznie plików repozytorium sprawdź, czy da się ustalić: cel projektu;
architekturę; moduły istniejące i planowane; odtworzenie środowiska; uruchomienie testów;
lokalizację modeli; ograniczenia; aktualną fazę; następne zatwierdzone zadanie; otwarte problemy.
Zweryfikuj, że odnośniki do plików istnieją, polecenia działają, a instrukcje nie są sprzeczne.
Wynik zapisz w raporcie `FAZA<N>_HANDOFF_AUDIT.md`. Nie deklaruj testu z innym modelem/osobą,
jeśli go nie przeprowadzono.

## 4. Czego nie wolno zakładać
- Że moduły oznaczone PLANOWANE istnieją.
- Że decyzje PROPOSED są zatwierdzone.
- Że historia rozmów lub pamięć agenta zawiera obowiązujące ustalenia.
- Że kolejna faza jest zatwierdzona, jeżeli PROJECT_STATE.md tego nie stwierdza.
