# Audyt 1 FAZY 0 — kopia materiałów audytora

Materiały niezależnego audytu FAZY 0 (commit `2fcc5f76fc171a6f7b10b5e5333ebd11df16c226`),
przekazane przez użytkownika 2026-10-22. Kopia służy temu, aby korekta i ponowny audyt
były sprawdzalne wyłącznie na podstawie repozytorium.

| Plik | Zgodność z oryginałem | SHA-256 oryginału |
|---|---|---|
| [AUDYT_FAZY0.md](AUDYT_FAZY0.md) | identyczny bajt w bajt | `5c463d83e57a36e998457e6cae3fe6cc03e5a2e7fe9fb2c46ba347fbc0fac18a` |
| [AUDYT_FAZY0_PROBY.py.txt](AUDYT_FAZY0_PROBY.py.txt) | identyczny bajt w bajt; dodano rozszerzenie `.txt`, aby skrypt audytora nie był traktowany jako kod projektu (Ruff, pytest) | `ece62512011ac47e63f8ca1223d7c6b9bd71df608560a801234e3f6e7fa79a89` |
| [AUDYT_FAZY0_WYNIKI.txt](AUDYT_FAZY0_WYNIKI.txt) | zmieniony wyłącznie przez usunięcie ścieżek lokalnych: katalog domowy → `<USER_HOME>`, nazwa użytkownika w `pytest-of-…` → `<USER>`; końce linii LF | `af71e50f30981aa9ac3b7c25e231a4ff5706d09e659fc2530805331e6daaea41` |

Odnośniki w `AUDYT_FAZY0.md` do `AUDYT_FAZY0_PROBY.py` wskazują oryginalną nazwę pliku.
Uruchomienie prób audytora na skorygowanym kodzie: `reports/phase0/korekta1/command_logs/`.
Odpowiedź na ustalenia: [../korekta1/KOREKTA1_RAPORT.md](../korekta1/KOREKTA1_RAPORT.md).
