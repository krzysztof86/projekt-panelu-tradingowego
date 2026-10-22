# Zlecenie korekty 1 FAZY 0 (tekst źródłowy)

| Pole | Wartość |
|---|---|
| Źródło | Polecenie użytkownika (właściciela projektu), 2026-10-22 |
| Podstawa | Niezależny audyt FAZY 0 commita `2fcc5f76fc171a6f7b10b5e5333ebd11df16c226` — kopia: [reports/phase0/audyt1/](../../reports/phase0/audyt1/) |
| Wersja dokumentu | 1 — tekst przeniesiony dosłownie |

---

Przeprowadź korektę FAZY 0 projektu Market Intelligence Desktop na podstawie załączonego niezależnego audytu.
Repozytorium: https://github.com/krzysztof86/projekt-panelu-tradingowego
Audytowany commit: 2fcc5f76fc171a6f7b10b5e5333ebd11df16c226.
Zezwalam na zmiany kodu, testów i dokumentacji konieczne do usunięcia usterek FAZY 0. Nie rozpoczynaj FAZY 1 i nie wykonuj git push bez mojego polecenia.

1. Przeczytaj AGENTS.md i dokumenty wskazane w nim. Sprawdź aktualny commit oraz zmiany względem wersji audytowanej.
2. Niezależnie odtwórz ustalenia audytu. Jeśli się z którymś nie zgadzasz, przedstaw konkretny dowód.
3. Napraw A-01–A-03: dokładność i niezależność obliczeń Trade od kontekstu Decimal, ścisły typ schema_version oraz obejście walidacji czasu przez bytes. Nie ograniczaj po cichu dopuszczalnych danych — uzasadnij przyjęte granice.
4. Zamknij A-04–A-07 zgodnie z raportem: doprecyzuj tożsamość instrumentów, zakres kontroli braku I/O i bezpieczne tworzenie zmienionych modeli; popraw walidację ReasonText.
5. Dodaj testy regresji. Nie osłabiaj istniejących kontroli ani nie usuwaj testów dla uzyskania zielonego wyniku.
6. Uporządkuj dokumentację, PROJECT_STATE i decyzje. Nie oznaczaj wszystkich PROPOSED jako ACCEPTED automatycznie. Wskaż decyzje wymagające mojego rozstrzygnięcia.
7. Uruchom pełne kontrole oraz odtworzenie w czystym środowisku. Przygotuj raport korekt, dokładne wyniki, logi i identyfikator zweryfikowanego commita.

Zakończ przekazaniem materiałów do ponownego niezależnego audytu. Nie deklaruj samodzielnie, że FAZA 0 została ostatecznie przyjęta.
